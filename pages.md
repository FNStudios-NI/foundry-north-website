# Pages — what is on every page the template makes

The skills say *when* a page is made; this file says *what is on it*. Read it before publishing any page.
Start every page from the blank, `docs/blanks/page.html`: copy it, fill the `<like this>` places, delete what the page does not need.
Why: the first trial's master was able, but it had no page rules, so its pages came out with no pictures and nowhere for his words. Told the rules once, it made the best page of the day. A form holds a shape better than prose.

There are three kinds of page: the **discovery page** (the Design page and the look; Problem, Scope, Facts and the Team are talked through in the chat and written down), the **plan page** and the **review page**. Two more are checked for their read-back (rule 20) only: a page sent to someone else (`<body data-page-kind="sent">`) and a board of options he marks (`<body data-page-kind="board">`).
Pages are for build stages, not every decision; small back and forth has no page unless he asks (his ruling, 5 Oct 2026).

## Every page

**Where it lives**

1. **Every sheet is a new page with its own link,** and its copy is saved in `docs/pages/` in the same step, named `<yyyy-mm-dd>-<stage>-sheet-<n>.html`.
   Why: in the trial each sheet was published over the last at the same link, so the earlier sheets could no longer be read, and none were in git.
   **How a page reaches his phone** (proven 6 Oct 2026): copied from the blank, checked (rule 30), served from the work machine on its private-network address, and opened in the thread's preview panel. Never the loopback address: the preview panel loads the page on the device he views it from, so a loopback address points at that device, not the work machine.
   Nothing sensitive goes on a page that will be on the open internet.
   A page server started from a thread lasts only as long as the thread's background jobs. A page he will open later needs a server that stays up, and setting one up is the machine owner's act.
   Why: the first page sent this way read on his phone and its copy button worked; served on the loopback address it showed an error, and its server stopped with the thread's background jobs about half an hour later.
2. **The session never repeats a page's questions in the terminal.** It gives the link, how many questions, and the minutes, then waits for his pasted letters.
   Why: in the trial he forgot the page existed and answered everything by hand in the terminal. A page he can skip is not doing its job.
3. **Typed answers are still taken.** If he answers in the terminal instead, the next sheet opens with "What I took from your message": his answers as a list he can correct.
   Why: his words are the ruling, wherever he types them; the list lets him catch a misreading.

**The top of the page**

4. **A title block with the stage and its place, and the minutes it takes:** "Scope · 2 of 6 · about 8 minutes", and how many questions.
   Why: with no map he could not tell how far he was through discovery, or whether he had time to open the page now.
5. **His last answers written back at the top,** before anything new.
   Why: he sees at once that he was heard, and can correct a misreading before it is built on.
6. **If his last answer grew or shrank the whole project a lot, the page opens with that,** says by how much, and offers paths, each priced in his hours: all of it, a first slice, or the small version first.
   Why: in the trial one answer roughly tripled the project, and the page listed it as one more line.

**Pictures and words**

7. **The mechanism as a picture before any question:** how the thing works, as a flow of boxes and arrows, drawn as an inline SVG diagram with a caption under it.
   Why: he is a film-maker; a picture is read in a minute. Three trial sheets explained systems in paragraphs and he missed the diagrams at once.
   The diagram reads in light and dark: its lines and words use `currentColor` and the page's colour tokens, never fixed colours. Steps that are his own hand are in a second colour; a step outside the system is dashed.
   This picture is the whole page's; each item the page explains still has its own (rule 31).
8. **An everyday likeness for each new idea** ("a hired edit suite", "a hotel key card"), in one line, beside its proper name.
   Why: a likeness from his world carries the idea; the technical name is said once and explained.
9. **Plain words.** A technical name is explained the first time. No commit ids, pull request numbers or file paths in what is said to him; they belong in the record.
   Why: he needs the meaning, not the reference.
10. **A fact about a machine, a tool or a service is marked checked or guessed, with its source** ("checked: read off the machine today" · "guessed: from an old note").
    Why: the trial stated a machine's backup and its free hours as plain fact when nobody had looked. A later sheet said a web page cannot vibrate or show a badge, which an installed one can on Android; so the mark covers tools and services as well as machines.

**Each question**

11. **Each question sits right under the evidence it asks about,** never in a list at the end.
    Why: he reads on his phone, often away from the laptop; scrolling back to find the evidence loses him.
    The evidence is an item block, and the question sits inside it (rule 31).
12. **Every option is priced: what it gains, what it costs him, and what it risks.**
    Why: his words, "This is perfect and should always be done like this."
13. **The recommendation is one of the letters offered, and says what each letter sets in motion:** "if a … · if b … · if c …".
    Why: a trial recommendation said "a, with b alongside", which his pasted letter cannot say; and a reason alone does not show him the consequences.
14. **A question that wants his words is a text box, not letters.** "What would count as success?" is his to write.
    Why: letters forced his answer into the master's guesses.
15. **A note box under every question,** letter or not, labelled for that question.
    Why: he wanted somewhere to add depth or sound out a thought without leaving the page.
16. **A new large thing in one word** ("an app", "a dashboard", "a database") **is asked about before it is scoped:** what he means, with two or three small pictures of what it could be.
    Why: in the trial "an app" was heard as a phone app when he meant a web page with a home-screen shortcut, and one word tripled the project on a guess.

**The bottom of the page**

17. **"Calls I'm making"**, listed apart from his rulings: each call the master is taking itself, with its undo.
    Why: silence is not a ruling. These are confirmed or undone at the plan sign-off; nothing is ever recorded as his because he did not object.
18. **Nothing enters the scope by silence.** Something the master wants to add is a question on the page, never "tell me if you'd rather leave it out".
    Why: twice in the trial work was added by opt-out.
19. **A copy button on anything he has to send to someone else** (a list of what is needed from another person, a message to forward).
    Why: that send is his act, and retyping a list on a phone loses lines.
20. **One read-back at the end, and one button that copies his letters and his notes together** (and his text-box words).
    If the clipboard is refused, the text appears in a box already selected, with "long-press to copy".
    Why: a paste is exact and a retyped answer is not; a button that copies letters only leaves his notes behind.
21. **"Where this comes from"** at the very end: the files and pages the sheet was built from.
    Why: so he, or the next session, can check any claim.

**People**

22. Discovery asks once, early, whether the project will ever be shared, copied to someone else or made public. If yes, a third person appears on a page and in the record by role ("the user"), never by name, health, employer or history, with their details outside the project and a pointer in `docs/register.md`.
    Why: the trial put a third person's private details in git and on a hosted page; his ruling was that it depends on whether the project stays private (a private project may keep them), so it is his question.
    It is asked in the chat, before the first page, and the brief's `Shared:` line, read by `tools/people_check.py`, is written from his answer in the blank's words; only a yes switches this rule on.
    Why: with no Shared line the people check refuses a new project's first page, as it refused the job scout's nine minutes before he answered.

**Stage, prices, words and size** (from the roast of the trial's sheet 4, 6 Oct 2026: its parts were right, its sequencing and pricing were not)

23. **A page asks only its stage's questions.** A plan question (a path, the team, a date) never shares a page with a facts question still unanswered. When a steer asks for two stages at once, the master first says which comes first and why, then makes that page.
    Why: sheet 4 asked him to pick a path and a team on sizes it called estimates, beside the facts question that was due. The steer, the conductor's own, asked for both, and no rule said no.
24. **Each option is priced as if it were the recommendation.** A cost or a risk just as true under the recommended letter is not a difference, and is not listed as one.
    Why: sheet 4 gave the other path a risk and a cost that were just as true of the one it recommended, so the prices argued for the pick.
25. **Calendar time is computed, never asserted:** build days against the agents the plan actually runs, under his cap, the same way for every path, with the sum shown.
    Why: sheet 4 let its recommended path run three workers side by side and the other only one; worked out evenly, the gap between them dissolved.
26. **A team page names each handoff on the diagram as a contract:** what crosses each arrow between desks, and who owns each end. Writing and keeping those contracts is a sized piece in the table.
    Why: sheet 4's desks were to build "against the other desks' fixed shapes" that nobody had written, while its own diagram's arrows already named what passes between them.
27. **Every question is a numbered question with a legend, never in a label, a caption or a sentence.** The intro's count of questions matches the numbered ones.
    Why: sheet 4 hid a fourth question in a note box's label and its intro said three; a question outside a numbered question is one he misses.
28. **Each page explains its own terms:** a word explained on an earlier sheet gets one clause again here.
    Why: sheet 4 used "one true line", "the judge" and "stand-in data" unexplained; he reads a sheet on his phone, often the next morning, without the sheet before it.
29. **Diagram text is never below 11 px at the drawing's own width,** and the read-back bar leaves the last question's note box usable.
    Why: sheet 4's small labels were 9.5 to 11 pixels in a 360-wide drawing, about 9 once the page's gutters were taken, and its read-back bar covered about a fifth of a small screen the whole way down.
30. **The page check is run before any page is published:** `python tools/page_check.py <page> --project .`, with `python tools/people_check.py` beside it. A REFUSE from either is a stop: fix the page and run it again, never publish around it.
    Why: the page rules were prose, and the trial's best page still broke five of them. A check that refuses holds a shape better.

**Each item, the way a pilot's manual explains it** (his ruling, 6 Oct 2026)

31. **Every item a page explains (a piece, a fork, the evidence under a question) is an item block with four parts:** the area it belongs to · the problem it solves · the links in the chain around it (what feeds it, what it feeds) · cause and effect (if this, then that).
    **Each item has its own diagram with visual cues:** his hand in the second colour, a step outside the system dashed, an arrow from each cause to its effect. Never one picture for many items. A question sits inside the item block of the evidence it asks about.
    In the blank it is `<section class="item">`, its parts marked `data-part="area"`, `"problem"`, `"links"` and `"effect"`, and its own `<figure>` holding an inline `<svg>`; the page check (rule 30) refuses an item without them, and a question outside any item.
    Why: his words, "things need to be explained clearly and plainly. like the way the a pilots manual does … what area, what problem is it solving, what are the links in the chain around this and the cause and effect … where are the diagrams, visual cues". Run 1's review put 17 results in a row under one shared picture, and he called it "mid at best".
    **A plan item (a piece on the plan page) also carries its mark, its lane and its cost.** In the blank it is `<section class="item" data-piece="<n>" data-mark="proven | documented | assumed | risk" data-lane="light | standard | full" data-touches="<paths, space-separated>">`, with three more parts: `data-part="mark"` (✅ proven, 📄 documented, ❓ assumed or ⚠ known risk, with its evidence: where it was seen working, the docs it rests on, or what happens if it fails), `data-part="lane"` (the lane and the checks it climbs) and `data-part="cost"` (its share of his week). This markup is fixed: `plan_check` reads it. The page check refuses a plan item without its mark, lane or cost.
    Why: his rulings 4 and 7 of 8 Oct 2026 (lanes; plans he can judge): he can weigh a piece only when he sees whether it was seen working, which checks it climbs, and what share of his week it takes.

## The discovery page

Discovery has six stages, in order: Problem · 1 of 6, Scope · 2 of 6, Facts · 3 of 6, Design · 4 of 6, Team · 5 of 6, Plan · 6 of 6 (the plan page, below). Problem, Scope and Facts are talked through in the chat and written down, each as one decisions entry and its own section of `docs/brief.md` (`## The problem`, `## Scope`, `## Facts`) with words of its own under it; the Team is talked the same way. Pages are made for Design and Plan only, and each names its place.
Why: his words, "lets not worry about html's for the brainstorm, we can just chat. the html's are more for direction once you have enough" (his ruling 2 of "Run 4 closed", 13 Oct 2026). On the job scout two of five pages were never answered as pages, and a facts sheet with no questions was made only because the page check demanded one.
Before a Design, Team or Plan page, the page check (rule 30) looks for each of Problem, Scope and Facts in the record: its section in `docs/brief.md`, with words of its own under it.
In a talked step, put together in one message every question that does not depend on another's answer, each numbered with its letters; one question at a time only where the next question depends on this answer.
Why: his note of 15 Oct 2026 on foundry-north-website: about 20 single-question turns of discovery 'could have been grouped and reduced the amount of back and forth'.

What each stage holds, talked or on a page:

- **Problem** (talked) asks about the problem only: what happens today, who it hurts, what "fixed" would look like to him. Looking for existing tools belongs to Facts.
  Why: the first trial sheet skipped the problem and went straight to a parts list and a search.
- **Scope** (talked) sets out IN, OUT and LATER, the OUT lines written down too. Each IN line has its size: small, medium or large, in build days and in his hours, with a total. One line says how much his last answer grew or shrank the whole.
  Why: a scope with no sizes hid that the project had tripled, and what is left out unwritten creeps back in as unasked work.
- **Facts** (talked) are read off the real machines and the tools' own documentation, and looking for existing tools belongs here. Every fact is marked checked or guessed, with its source. Research offered before a signed plan comes with a real ceiling: how many readers, on which model, how many turns each, and how much of his usage window (light, medium or heavy).
  Why: a first brief once assumed a tool the machine did not run, and everything built on it fell. "I can't measure it exactly from here" is not a price, and a figure in currency meant nothing to him: "the 15 dollars doesn't mean anything" (his words and ruling, 6 Oct 2026).
- **Design** (a page) is one picture of how it works, in plain words, and names what is deliberately left out.
  Why: he is a film-maker, and a picture is read in a minute; the picture is what the review is held against.
- **The look** ends the Design stage of any project with a screen: a clickable look on his phone, with made-up information, in two or three styles, before anything is built to it. He chooses one, and the plan is built to it.
  Why: his ruling 3 of "Run 4 closed" (13 Oct 2026). Fifteen pieces of the job scout landed before he saw how it looked; his words then: "lets build the look first and show me it to my phone, it needs to be clickable with fake information". The look took 27 minutes to make, and he chose ten minutes later.
  The look is made by one helper, started by the planning master when he says "make the look" in the chat; it builds only the look, in its own scratch copy, and nothing of it is kept in the project until the plan says so.
  Why: his ruling 5 of "Run 5 closed" (14 Oct 2026): the master never builds, and no desk or worker exists before his signature.
- **Team** (talked) names each desk: what it owns, and what it hands the others. A desk earns its folder by having a job no other desk has; one desk is a fine answer. When a page is made for it, each desk is a box and each arrow is named as rule 26 says.
  Why: he wants to see why a desk earns its folder before he rules it.

**No calendar dates before the Facts stage.** Before it, sizes are build days and his hours, never "ready by the 10th".
Why: a trial page promised two dates from estimates before any fact about the machines had been read.

**A project that adopts the template after its discovery:** its pages made before it adopted are not stages to the page check. Its first act under the template is today's facts in the record, talked through as any Facts stage is; Design, Team and Plan come after it. A facts sheet in `docs/pages/` still stands, for a project that adopted the template or one that walked the earlier form (a page for every stage).
Why: the page check refused an adopted project's plan page for want of a facts sheet, and the check was right: a plan's prices rest on today's facts, not on the facts its earlier pages were made on.

## The plan page — Plan · 6 of 6

- **The status board first,** right after the title block: the output of `python tools/status.py --html`, one element marked `data-status-board`. The page check refuses a plan or review page without it there. Why: he sees which step is an idea, on trial or a foundation before he signs what leans on it (design 0.9.0, Part 3).
  **The workflow question.** In a project with a closed run and no workflow file, a plan or review page puts that to him as its own needs-thought question, naming the kind of work with no file: one question marked `data-needs-thought="workflow"` and `data-work="<the kind of work, in plain words>"`, those same words in the question's own text; the board's line `workflows: none` alone is refused by the page check. Why: at the review of runs 6 and 7 the board said `workflows: none` in one line and he had to ask where the workflow section was (his ruling 1 of "Run 8 asked for", 19 Nov 2026; L040).
- **Paths,** each priced in his hours against the result it buys, drawn as a timeline: all of it, a first slice, the small version first; what he gets for one hour of his time, for three, for none, and the same at any blocker.
  Every path is priced the same way whichever is recommended (rule 24), and its calendar time is worked out from the same agents and the same cap (rule 25).
  Why: his words, "so we can decide how much human time to put in to get what results."
- **A mark on every item:** ✅ **proven**, seen working on his machines, with where; 📄 **documented**, the tool's own docs, linked; ❓ **assumed**, nobody has checked. Every ❓ is spiked before he signs, as the conductor skill's § 3 says, and the signed plan holds none. A spike that needs his hands (his screen, an install) is priced in his minutes like any act, or, by his word, he signs the item as a **known risk** (⚠, his ruling 9 of 8 Oct 2026), shown with what happens if it fails.
  Why: run 2 took two roads on untested guesses; he can judge a plan only when he sees which parts are known (his ruling 7 of 8 Oct 2026). A gamble he takes knowingly is his call; one dressed as a fact is not.
  A spike is a 5 to 15 minute throwaway test on Sonnet, started by the master the moment its ❓ is spotted, in the background while the talk goes on, side by side inside the cap; it writes one line back: what was tried, what was seen, ✅ or ❌. A pass costs him nothing; a fail, one question: which road instead.
  Why: started at once, spikes hold the plan up 15 to 20 minutes at most, usually not at all (his question, 8 Oct 2026: the time added against the time unblocked).
  Anything that touches another house first gets one letter: "are you building this?"
  Why: that house may be building it already, and one letter costs less than the same thing built twice.
- **A lane for each piece,** light, standard or full, with the checks it climbs (the card blank's Lane line), proposed for his signature; never light on a tool, a skill or `template/`.
  Why: the lane decides who builds and who checks, so how much checking a piece gets is his to sign (his ruling 4 of 8 Oct 2026).
- **The size table:** each piece small, medium or large, its build days, his hours, a total, and the biggest unknown named.
- **What a run costs:** in his hours and in his usage window, light, medium or heavy; never in currency. A service that bills him per use is named as such, and paying it is his act.
  Why: paying is always his, and he cannot weigh a path without its price; a currency figure meant nothing to him, his hours and his window do (his ruling, 6 Oct 2026).
- **Dates appear here first,** once the facts are read, each with what it rests on.
- **Every key point** downstream, for him to mark a (stop there), b (tell me and show me on my phone) or c (power through).
  Why: he chooses his stops in advance instead of watching every step.
- **The budget and the hard stop,** as default numbers he may change when he signs: the budget a share of his week, the hard stop the planned end plus a margin. The budget's default is the plan's own estimate, and the hard stop's is the planned end plus 50%; after a few runs, what the measures show is normal. In the blank they are marked `data-budget` and `data-hard-stop`; the page check refuses a plan page without both.
  Why: a run stops at the first cut-off, and these two are the cut-offs he signs for; run 2 ran twice its length (his ruling 5 of 8 Oct 2026). The budget's default was a flat 10% of his week until the job scout's plan, which estimated 20%, was given the 10% and stopped early (his ruling 4 of 13 Oct 2026).
- **How many agents it would like at once,** against his cap: four, masters and checkers included, unless he lifts it by his word (only when video generation is off).
  Why: four beside a take is his ruling, on his caution and the ramp's memory readings until the road desk measures more. The work machine did not crash at fifteen agents: the 5 Oct stop was his own shutdown (his correction, 6 Oct).
- **The calls I'm making** from every discovery sheet, gathered, each with its undo, to confirm or undo now.
  Why: a call he never saw is not ruled.
- **The two starts,** `Start: tracks` or `Start: now`, each with its one line of meaning from the plan blank.
- **The acts tried beforehand:** the permission probe's answers (`tracks.md` rule 19) and the dry run of every command in his acts, or the refusal that was looked for. An act that has not been tried is marked ❓ like any other piece. They sit in the page's element marked `data-acts-tried`; the plan check (`python tools/plan_check.py <page>`) refuses a plan page without it.
  Why: the page the job scout's plan was signed on held no probe answers, and its install command had never been tried: the wall was found with him at the keyboard.
  An act file of many commands is built and checked as a piece, never written by the master.
  Why: the job scout's held about twelve untried commands, and its handover had the master write it; the master never builds.
- **The plan check:** before the plan page is published, `python tools/plan_check.py <page>` must say ALLOW, beside the page and people checks (rule 30). A REFUSE is a stop: spike the ❓, add the lane, fill the numbers; never publish around it.
  Why: the plan is all the build gets, and the check reads whether it holds what the build needs.
- **His acts** as one numbered list, "approve all" first, the hand-only ones named apart with their minutes.
  Why: work once sat for hours waiting on his hand.

## The review page

It lives at `docs/runs/<n>/review.html`, not in `docs/pages/`: that is where the where-am-I check looks for it. The review is one pass over the forks the master made that could affect him later in the design, not a keep-or-undo of every piece: the pieces are the master's decisions (his ruling, 6 Oct 2026).
Why: he cannot judge technical pieces; he can judge forks that shape his later work. Run 1's first review put 17 pieces in a row for keep or undo, and he stopped answering part-way.

- **The status board first,** as on the plan page, and under it **the scoreboard's last five rows** (every row, when fewer): the output of `python tools/scoreboard.py --last 5 --html`, one section marked `data-scoreboard`. The page check refuses a review without either, or with other rows.
  Why: nothing set one template version beside the next, so a change that made things worse could not be seen (his ruling 1 of 17 Nov 2026).
- **"It works" first:** the page's first item block (rule 31), headed "It works": each done-when line of the signed plan, tried, pass or fail, with how it was tried (the run record's `## It works`). The page check refuses a review whose first item block is not it.
  Why: his ruling 8 of 8 Oct 2026; a run can land every piece while the thing itself does not work.
- **The measures,** worked out from the run record, never estimated: usage per finished piece (his time is not measured, his ruling of 8 Oct 2026); surprises after he left (unforeseen key points, refusals and blockers after go); share of the plan finished (pieces landed, out of those in `docs/runs/<n>/plan-signed.md`).
- **The two taps, last:** the page's last two numbered questions, five letters each, 1 to 5, in one item block (the run is the item): the thing made, then the run's enjoyment. `python tools/scoreboard.py --run <n> --made <1-5> --enjoyment <1-5>` writes both into the run's row at the close. The page check refuses a review whose last two questions are not they.
  Why: his verdict on what is made comes first, then his time (his ruling 1 of 17 Nov 2026); one stretch scored eight merges while nothing worked. A tap, not a text box (his ruling 8 of 8 Oct 2026); a line on why goes in its note box.
- **One section per fork,** each an item block (rule 31) with its own diagram: what the master chose, and the options it turned down, each priced (rule 12) with what it would set in motion later; his letters, and a note box. Each key point nobody saw coming is a fork.
  Why: his condition for letting the master decide is that each choice is laid out against the options turned down.
- **The upgrade,** every review, after the forks and before the two taps: one section marked `data-upgrade`, as the blank has it. Its list comes from `python tools/upgrade.py`, never from memory. Its groups, in this order, each marked `data-group` with the name `upgrade.py` gives it; a group with nothing in it says "none" in one line:
  - **needs thought** (`needs-thought`): highlighted and first; anything that would take a system or workflow in a very different direction, each its own question, kept out of approve all;
  - **lines to keep, change or drop** (`lines`): one item block, a table of the lines with the master's lean on each, one "approve all my leans" question and its note box; he overrides a lean by naming its L-number in the note;
  - **suggested foundations** (`foundations`): each its own item block and question. A foundation is his word, decided in the review conversation from doing the work and testing it; the numbers inform it and never judge it;
  - **candidate tracks** (`tracks`): each its own question: keep as a candidate, put on trial, or drop;
  - **foundations to reopen as trials** (`trials`): each its own question; and every foundation (`foundation`) listed with a tick to reopen it as a trial;
  - **for the template** (`template`): the lines whose file the template owns, listed and answered with the rest, never edited in the project.
  The closing entry's `### The upgrade` table (`| L-numbers | his answer | the line as kept | where it is |`) is written from his answers, and `python tools/upgrade.py --check` passes before the run is closed. In a project that has `docs/lessons.md`, the page check refuses a review without the section, with it after the taps, with a group named otherwise than `upgrade.py` names it, with needs thought not first, with a lines group that is not one "approve all" question, with a needs-thought, foundations, tracks or trials item that is not one question, or with a group holding neither an item nor "none".
  Why: a step he is never shown never runs; nobody ever proposed a foundation while the review was counted and remembered (his ruling 1 of 12 Nov 2026: every review, held by tools). Approve all saves his time for what only he can judge, and the needs-thought group keeps a change of direction out of it (his ruling 2). A foundation is his, from the work (his ruling 9). An unknown case worked out with him becomes a track the next case can follow (his ruling 8). The close's table is what `--check` reads, so a close without the upgrade is not a close.
- **The pieces, as a short list:** each merged piece in one line, with its undo. No question is asked of them; he may name any to undo.
- **The read-back,** copying his answers, his notes and his two taps together.
  Why: the review is where his pass replaces the wait he no longer spends before each merge.

## How a page is built

The blank's top comment carries these; they are what the page host accepts and what reads well on his phone.

- The first line is `<meta charset="utf-8">`. The page check refuses a page whose first line is not.
  Why: with no text encoding declared, a page served by a plain page server showed its "·" marks as Chinese characters in its title.
- No doctype, html, head or body tags: after that line, the page is a `<title>`, one `<style>`, the content and one `<script>`.
- Every colour is a token in `:root`, with a dark set under `prefers-color-scheme: dark`. No colour is written anywhere else.
- Phone width first: one narrow column, nothing that needs a wide screen, tables in a scrolling wrapper.
- Labels on every box and button, and the read-back announced as it changes, so it works with a screen reader.
