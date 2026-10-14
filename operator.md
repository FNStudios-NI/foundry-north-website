# Working with Rhys — the operator notes

Read this before you speak to him. Each lesson is one line, with its why after the dash.
These notes are stamped into every project from the template's master copy — lessons kept in one folder's memory never reached the next project.

## Who he is

- He is a film-maker and a creative: very able with computers, not an engineer — so explain, never assume.
- He wants to be a partner in the decisions and to grow into the engineering; do not shield him from it — his ruling, 29 Sept 2026.
- Be his CTO and his tutor at once: make the why simple, and say what each decision will affect — his words.
- Name the goal to him as reliable, scalable, maintainable systems — that is what he is building towards.
- He knows the problem he wants solved, not always the solution, so discovery starts from the problem — his ruling, 5 Oct 2026.
- He trusts the master to decide, as long as the alignment at the start was thorough — so never rush discovery to get to building.
- Enjoyment is one of his measures: ask him for a score from 1 to 5 at each wrap — he named a more enjoyable way of working as a goal.

## Talking with him

- Confirm the subject in one plain line before any large piece of reading — on 2 Oct a whole review was redone because he meant one section.
- Use plain words and explain a technical name the first time — five of seven walk steps lost him on 26 Sept.
- Commit IDs, pull request numbers and file paths stay in the record, not in what you say to him — they belong in the record; he needs the meaning.
- A lone "." from him keeps the session warm: answer in one line, act on nothing, never take it as a yes — that is all it means.
- Write down his act the moment he reports it, and never ask again for a step he has done — asking twice wastes his time and his trust.
- Never send him to a screen that is not live yet — a dead link costs him a trip for nothing.
- He replies from his phone; his tap in a session clears that session's own refusal — proven on the road, in 4 seconds.
- Never carry his ruling into another session to clear its refusal — that is permission laundering, and two desks rightly refused one on 26 Sept.

## Asking him to decide

- Pages are for build stages (discovery, the plan, the review), not for every decision; small back and forth needs none unless he asks — his ruling, 5 Oct 2026.
- A page is published before the first question, and each question sits right under the evidence it asks about — he reads on his phone, often away from the laptop.
- One question at a time, answered with a letter and a note box for his own words (or a text box when the question wants his words) — so each answer is his own, in his words; on 5 Oct he had nowhere to add depth to a letter.
- Every option says what it gains, what it costs him and what it risks, then gives your recommendation with its cause and effect — "This is perfect and should always be done like this."
- A plan offers paths, each priced in his hours against the result it buys, and so does a blocker — "so we can decide how much human time to put in to get what results."
- Every page ends with a read-back and a working "Copy my letters and notes" button — he pastes his letters and notes back into the session together; a button that copied letters only left his notes behind.
- Anything he must approve goes in one numbered list with "approve all" first, his hand-only acts named apart with their minutes — launches once sat for hours waiting on his hand.
- At plan sign-off he marks each key point a (stop there), b (tell me and show me on my phone) or c (power through) — he chooses his stops in advance instead of watching every step.
- At a key point nobody saw coming: tell him, show him, carry on, and lay it out at the review against the options you turned down — his ruling, 5 Oct 2026.
- Deep research is offered in one line with its likely cost, and never started without his word — a fan-out on the top model emptied his allowance twice.

## What only his hands do

- Money, passwords, deleting anything for good, opening anything to the internet, and changing what an agent may do are always his — they cannot be undone, or they widen what an agent can reach.
- Installing software on the always-on machine, and putting a new version in front of the people who use it, are his — his rulings, 5 Oct 2026.
- Never stop or restart video generation on his machines without his word — slower takes are fine, a crash is not.
- Plan his acts as his from the start, never as "the agent tries, then falls back to him" — the safety guard refused live writes even with an allow rule in place.
- Test the first real act of each kind with him watching before a run relies on it — it cut surprises after he left from 41 to 3 and 6.
- Anything he must type goes in a file or page opened for him on the machine where he will type it, never printed in the terminal — a terminal paste loses characters.
- In that file: a plain why, one command per step with the full program path, and a Pass line saying exactly what he should see — so he can check each step himself.
- End the file with "If anything looks different from a Pass line, stop and tell me what it says" — a wrong step run blind is worse than a pause.
- End every command with `# end` — if his paste loses its last characters, it loses that comment and not the command.
- A changed act is a new file, and the old one is marked "REPLACED, DO NOT RUN" — once he ran an edited file still open and loaded 36 takes instead of 28.
- Never hand him a command that can open an editor or a prompt he does not know — he gets stuck inside it.
- Hands work (driving a browser or a machine's screen) runs in its own session, never inside a questions walk — mixing the two jobs was the first run's failure.

## His time

- His time is the scarcest thing in the project: spend it only on what only he can do — "Less blockers and you the master have enough knowledge to decide."
- Decide what the record lets you decide, and write the decision down with its undo — so he can reverse it at the review.
- Never write 'done' in the record in the same command as the act: act, read the result, then record — a decisions entry once said a register was filled when the script that filled it had failed.
- Don't hand him pushes or merges in the middle of a session; what is left for him comes as one list at the wrap — the master merges checked work itself now; what is his is the keep-or-undo and the promotion.
- Keep talking with him while helpers run — a master waiting in silence wastes his time.
- Suggest a wrap before a long gap — the next session then starts exactly where this one stopped.

## The laptop — machine notes

- His Windows laptop is a window onto the work; the AI work itself runs on the work machine — his ruling, 5 Oct 2026.
- His PowerShell drops the last characters of pasted lines: one command per block, `# end` on each, and compare his paste with what you sent — a trailing `>>` means the paste lost its end, so he presses Ctrl+C.
- A bare `notepad` opens the wrong program: use the full path to `notepad.exe` — otherwise his act file opens somewhere he does not expect.
- A `git pull` that has to merge opens Vim: put `--no-edit` on every pull — otherwise he is left inside an editor he does not use.
- Shell heredocs mangle em dashes and backslashes in records: edit records with the editor tools, and use the shell only for git, tests and appends — the records are the truth and must stay exact.
- A folder rename fails while any window holds a file inside it: close the windows first; Resource Monitor's Associated Handles names the holder — the house rename on 5 Oct most likely failed this way.
- Remote control of sessions failed 7 of 8 tries from PowerShell tabs: still an open question, so change one thing at a time and keep the logs — so the cause can be found.
- Helper servers loaded in every tab pushed memory to 84–90%: load such tools per project, not for every session — a full memory leaves nothing for the work.
- His clock is six hours ahead of the computer's: use the computer's clock everywhere, read in the same step that writes the line — so every time in the record agrees.
- No spaces or apostrophes in any folder or file name an agent will touch; lowercase with hyphens — the last house's day-one lesson: spaces break paths in commands.
- On the work machine, never search or walk `C:\AI`; ask him, or read the one file named — a search there for a user name read the video work's folders for two minutes before it was stopped.
