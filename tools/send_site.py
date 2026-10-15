# send_site.py: send the site, desks/site/public/, to its own repository.
#
# What it is for
#   The site's files live in desks/site/public/. Cloudflare publishes them
#   from a repository of their own, foundry-north-site, which holds the site
#   and nothing else. This tool is the one way they cross:
#     1. It reads what git holds under desks/site/public/ at this checkout's
#        HEAD, and refuses a symbolic link there, or any uncommitted change
#        (an edit, a new file, a removal) under that folder on disk.
#     2. It clones the site's repository into a scratch folder of its own.
#     3. It makes the clone's tree exactly those files, at its top, and
#        nothing else: a file gone from public/ is gone from the site.
#     4. It checks the staged clone holds those files and no other, each
#        the same as git holds it here, and refuses if not.
#     5. It commits, naming this project's commit, and pushes the clone's
#        main.
#   It prints SENT: <site commit> from <project commit> and exits 0, or
#   NOTHING TO SEND (exit 0) if the site already holds exactly these files.
#   It refuses with REFUSE: <why>, exit 1, having pushed nothing.
#   The site's commit is made under this checkout's own git identity
#   (git config user.name and user.email here), which the clone does not
#   inherit; with none here it refuses before cloning.
#   With --dry-run it says what would cross and pushes nothing.
#
# Why the rule exists
#   Rhys ruled the site its own repository (brief § Design, his letter "b"),
#   so that Cloudflare sees the site and nothing else. desks/site/public/ is
#   the only part of this project that may be public: what crosses is what
#   git holds in that folder, never what happens to sit on disk.
#
# How to run it (in this project's checkout, from its top folder)
#   python tools/send_site.py              send to foundry-north-site
#   python tools/send_site.py --dry-run    say what would cross; push nothing
#   python tools/send_site.py --repo <url or path>    another repository
#
# Python 3 standard library and git only. Its only network steps are the
# clone and the push.

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile

SITE_REPO = "https://github.com/FNStudios-NI/foundry-north-site.git"
PUBLIC = "desks/site/public/"
# Byte for byte: no line-ending change on the way across.
EXACT = ["-c", "core.autocrlf=false", "-c", "core.safecrlf=false"]


class Refuse(Exception):
    pass


def git(*args, cwd=".", data=None):
    """Run one git command; return (exit code, what it printed as bytes)."""
    done = subprocess.run(["git", *EXACT, *args], cwd=cwd, input=data, capture_output=True)
    return done.returncode, done.stdout + done.stderr


def must(step, *args, cwd="."):
    """Run one git command that has to work; return its output as text."""
    code, out = git(*args, cwd=cwd)
    text = out.decode("utf-8", errors="replace").strip()
    if code != 0:
        raise Refuse(f"{step} failed — {text}")
    return text


def public_files():
    """What git holds under desks/site/public/ at HEAD: {path in the site: blob id}."""
    code, out = git("ls-tree", "-r", "-z", "HEAD", "--", PUBLIC)
    if code != 0:
        raise Refuse(f"git could not read HEAD — {out.decode('utf-8', errors='replace').strip()}")
    files = {}
    for entry in out.split(b"\0"):
        if not entry:
            continue
        info, path = entry.decode("utf-8").split("\t", 1)
        mode, kind, blob = info.split()
        if mode == "120000":
            raise Refuse(f"{path} is a symbolic link; only plain files cross")
        if kind != "blob":
            raise Refuse(f"{path} is not a plain file ({kind}); only plain files cross")
        files[path[len(PUBLIC):]] = blob
    if not files:
        raise Refuse(f"git holds nothing under {PUBLIC} at HEAD")
    return files


def identity():
    """This checkout's git identity, for the site's commit: [-c user.name=..., -c user.email=...]."""
    found = []
    for key in ("user.name", "user.email"):
        code, out = git("config", key)
        value = out.decode("utf-8", errors="replace").strip()
        if code != 0 or not value:
            raise Refuse(f"this checkout has no git {key}; set it here (git config {key} ...) so the site's commit has an author")
        found += ["-c", f"{key}={value}"]
    return found


def uncommitted():
    code, out = git("status", "--porcelain=v1", "--untracked-files=all", "--", PUBLIC)
    if code != 0:
        raise Refuse(f"git status failed — {out.decode('utf-8', errors='replace').strip()}")
    return out.decode("utf-8", errors="replace").strip()


def stage(clone, files):
    """Make the clone's index exactly these files; return the site's last commit, or None."""
    has_main = git("rev-parse", "--verify", "-q", "refs/remotes/origin/main", cwd=clone)[0] == 0
    if has_main:
        must("checkout", "checkout", "-q", "-B", "main", "origin/main", cwd=clone)
    else:
        must("checkout", "symbolic-ref", "HEAD", "refs/heads/main", cwd=clone)
    # Empty the clone, all but its .git, then write each file as git holds it here.
    for name in os.listdir(clone):
        if name != ".git":
            target = os.path.join(clone, name)
            if os.path.isdir(target) and not os.path.islink(target):
                remove(target)
            else:
                os.remove(target)
    for path, blob in files.items():
        code, data = git("cat-file", "blob", blob)
        if code != 0:
            raise Refuse(f"git could not read {PUBLIC}{path}")
        target = os.path.join(clone, *path.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)
    must("git add", "add", "-A", ".", cwd=clone)
    # The staged clone must hold these files and no other, each byte for byte.
    staged = {}
    for line in must("git ls-files", "ls-files", "-s", "-z", cwd=clone).split("\0"):
        if line:
            info, path = line.split("\t", 1)
            staged[path] = info.split()[1]
    extra = sorted(set(staged) - set(files))
    if extra:
        raise Refuse(f"the staged clone holds {', '.join(extra)}, not a tracked file of {PUBLIC}")
    differ = sorted(p for p in files if staged.get(p) != files[p])
    if differ:
        raise Refuse(f"the staged clone's {', '.join(differ)} differs from what git holds here")
    return must("rev-parse", "rev-parse", "HEAD", cwd=clone) if has_main else None


def remove(folder):
    """Remove a folder this tool made; git leaves some files read-only on Windows."""
    def unlock(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(folder, onerror=unlock)


def send(repo, dry_run):
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        raise Refuse("this folder is not inside a git working copy")
    os.chdir(top.decode("utf-8").strip())
    files = public_files()
    changes = uncommitted()
    if changes:
        raise Refuse(f"uncommitted changes under {PUBLIC}; commit them first — {changes}")
    project = must("rev-parse", "rev-parse", "HEAD")
    author = identity()

    scratch = tempfile.mkdtemp(prefix="send-site-")
    try:
        clone = os.path.join(scratch, "site")
        must("clone", "clone", "-q", "--no-checkout", repo, clone)
        last = stage(clone, files)
        if last and must("write-tree", "write-tree", cwd=clone) == must("rev-parse", "rev-parse", "HEAD^{tree}", cwd=clone):
            print(f"NOTHING TO SEND: {repo} already holds {PUBLIC} as at {project[:7]}")
            return 0
        if dry_run:
            if last:
                changed = must("diff", "diff", "--cached", "--name-status", "HEAD", cwd=clone)
            else:
                changed = "\n".join(f"A\t{p}" for p in sorted(files))
            print(f"DRY RUN: would send {len(files)} files from {project[:7]} to {repo}; nothing pushed\n{changed}")
            return 0
        must("commit", *author, "commit", "-q", "-m", f"Site from foundry-north-website {project}", cwd=clone)
        site = must("rev-parse", "rev-parse", "HEAD", cwd=clone)
        must("push", "push", "-q", "origin", "HEAD:refs/heads/main", cwd=clone)
    finally:
        remove(scratch)
    print(f"SENT: {site[:7]} from {project[:7]} to {repo}")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Send desks/site/public/ to the site's own repository.")
    parser.add_argument("--repo", default=SITE_REPO, help="the site's repository, a URL or a path")
    parser.add_argument("--dry-run", action="store_true", help="say what would cross; push nothing")
    args = parser.parse_args(argv[1:])
    try:
        return send(args.repo, args.dry_run)
    except Refuse as why:
        print(f"REFUSE: {why}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
