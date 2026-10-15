# Brief — foundry-north-website
Shared: never
Held apart: none

## The problem
Ruled 14 Oct 2026 02:58 ("yes" to the read-back).

**The problem.** Foundry North has no public website. When someone looks the business up before signing a deal, they find nothing, so there is no authority behind the conversation. Social posts and cold outreach have nowhere to land.

**Who it hurts.** Rhys, at the point of closing. The people looking are both founders and people inside organisations (his letter "c").

**Fixed means.** A person who clicks through sees something impressive and clear, comes away reassured that this is a real and serious business, and has one clear way to get in touch (his letter "b"). A booking tool is not part of "fixed".

His words:
- What hurts: "we don't have any authority if people go looking before signing the deal. if we do social or cold outreach i would like them to see something impressive and clear once they click on."
- Said in the template project on 13 Oct 2026, carried here by the hand-over: "this will be a simple but functional website with the goal to a. be authority if we build funnels and people end up here. b. help convert founders into mini studios which we run." and "a simple 1 Era project that can give me a finished placeholder website that is ready to be public facing"

Left for later steps, not part of the problem: which of the two buyers the page speaks to first; what the offer is called ("mini studios" against "your engine"); whether the site goes live at the address in this era.

## Scope
Ruled 14 Oct 2026 05:51 ("Yes" to the read-back). Sizes are estimates until the facts are read. Lines marked (master's) were the master's proposals, put to him in the read-back and ruled in by his "Yes".

In:
- One scrolling page: the result first, a "for founders" section, a "for organisations" section, how it works, why to trust, an email button. Small: about half a build day, about 1 hour of his (approving the words).
- The look first: two or three styles, clickable on his phone with made-up words; he chooses one before anything is built to it. About half an hour of building, about 15 minutes of his.
- The film placeholder: a space designed so his film drops straight in. Part of the page.
- Search basics and the link preview (title, line and picture when the link is shared). Part of the page.
- (master's) A private preview address he can open on his phone, where the finished site sits until going live. About a quarter of a build day; it may need an account of his (read at the facts step).
- (master's) Phone first: designed for a phone screen first.
- (master's) Words drafted from his July voice rules and page words, approved by him line by line.
- (master's) Nothing faked: trust from what is true and public ("built by filmmakers, fifteen years of craft"); no testimonials, no client names or logos, nothing the digest marks private.
- Going live (moved in at the facts step, 14 Oct 2026 08:29, his letter "B"): the finished page at foundrynorthstudios.co.uk and `www.`, replacing today's error page, seen first on the private preview; the switch is his act. About half a build day and 20 to 30 minutes of his hands.
Total before going live moved in: about 1¼ build days and about 1½ hours of his; with it, about 1¾ build days and about 2 hours of his. His answers made the whole smaller than the master's recommendations: "not live" alone took off about half a build day and 20 minutes of his hands.

Out:
- Any change to the domain's email, the portal, `pick.` or anything but the bare address and `www.`.
- More pages, or a page for each buyer.
- A contact form, and a booking tool.
- Making the film itself.
- A price.
- The full search plan and articles.
- (master's) Visitor counting and cookie banners (with no form and no tracking, no banner is needed).
- (master's) Client stories and testimonials.

Later:
- His film dropped into its space.
- A contact form, tried for real once live.
- A page aimed at one buyer for a particular outreach push.
- A booking button.
- The full search plan.
- (master's) Visitor counting, once live.
- (master's) Client stories, once a client agrees to be named.

The forks, his letters in order (14 Oct 2026):
- How big: one page (his letter "a" of a one page, b three pages, c a page for each buyer).
- Live or not: finished but not live; going live is a separate later step on his word (his letter "b" of a live at the address, b finished but not live; the master had recommended a). Superseded at the facts step by his letter "B": going live is in.
- Who the page speaks to first: neither by name; the top talks about the result, and two short sections below say "for founders" and "for organisations" (his letter "C" of a the founder first, b the organisation first, c neither by name; the master had recommended a).
- The one way to get in touch: an email button; a form is for the later going-live step (his letter "A" of a an email button, b a short form, c both).
- Film on the page: none in this era, with a designed-in placeholder for a film he will make soon (his letter "A" of a no film, b a silent loop at the top, c a film to press play on). His words: "Have a placeholder for a film, as we will make one of the next couple of days."
- A price on the page: none (his letter "A" of a no price, b a "from" price, c no number but a signal). Settles the digest's contradiction 5.
- Search: the basics only, including the link preview (his letter "A" of a the basics only, b the full search plan). His words: "A this is the 1st instance, the rest can come later". Settles the digest's contradiction 7.


## Facts
Being read and talked through (14 Oct 2026, read on Pandora about 05:50). Each fact is marked checked (read off a real machine or service today) or documented (read in a file, not re-checked), with its source.

- The website's address is `foundrynorthstudios.co.uk`; he holds the domain (his ruling 2 of 14 Oct 2026 02:47).
- The record is online in a private repository (his ruling 1 of 14 Oct 2026 02:47).
- The domain's DNS is on Cloudflare (name servers angelina and jaime.ns.cloudflare.com). Checked: `nslookup` against 1.1.1.1.
- Its email is Zoho (MX mx.zoho.eu, mx2, mx3), with an SPF record naming Zoho and IONOS. Checked: the same lookup.
- The bare address and `www.` both resolve through Cloudflare and both answer **error 525** (Cloudflare cannot make a secure connection to whatever sits behind them): anyone who types the address today sees an error page. Checked: `curl`. What sits behind them is not known (a guess: an old host, perhaps IONOS, from the SPF record).
- `portal.` answers 200 with the client workspace page (saved 2026-07-28); `pick.` answers 404 "There is nothing at this link." Checked: the same `curl`. Neither is touched in this era (Scope: Out).
- The portal and Studio OS's page run on Hephaestus behind cloudflared; the job scout planned its own tunnel and address there (proposed `jobs.`), never Studio OS's. Documented: job-scout `docs/brief.md`, lines 55 to 80.
- A private preview can reach his phone with no account and no domain change: Pandora already serves pages "tailnet only" through Tailscale Serve (`/pages`, `/letters`, ports 8443 and 10000), and his iPhone 15 Pro Max is on the same tailnet, active. Checked: `tailscale status` and `tailscale serve status`.
- The two website folders are unpacked outside the project, at `C:\Users\3070s\AiEngineering\laptop-inbox\2026-10-13\website-folders\unpacked-2026-10-14\` (355 files: `15Website\` and `Advisor-website\`). Checked: listed.
- No logo file is in the zip: the logos sit only on the laptop, in the brand folder the digest names (§ 8), and predate the current colours. Checked: no file named logo in the unpacked folders.
- Footage exists: six clips and five "for web" sequences of 21 May 2026 in `Advisor-website\Videos for website v1\`, not viewed. Checked: listed. Not used in this era (Scope: no film).
- The July page words are `Advisor-website\pages.md`; its email button was a placeholder, `rhys@foundrynorth.studio`, "to confirm". Checked: lines 263 and 298 read. The brand voice file is not in the zip; the digest quotes it (§ 7).
- Fonts: the brand's first choice (Neue Montreal) is a paid face with no licence held; Inter and IBM Plex Mono are free. Documented: the digest § 8.
- Hosting for going live (read after going live moved in, about 08:30): Cloudflare Pages is a current product; for a domain already on Cloudflare, adding a custom domain to a Pages project adds its CNAME record automatically, apex included. The docs do not say what happens to existing A records on the same name, and warn that CAA records can block the certificate. Documented: developers.cloudflare.com/pages/configuration/custom-domains/. Whether Pages accepts the bare address over today's proxied A records is ❓, to be tried before the plan is signed (it needs his Cloudflare sign-in).
- CAA records: this machine's `nslookup` cannot query them ("unknown query type: CAA"); not yet read.
- No Node, npm or wrangler on Pandora (Cloudflare's own upload tool needs Node; installing is his act). Checked: `which`. A Pages project can instead build from a folder of a GitHub repository, connected once in the Cloudflare dashboard (his act; it gives Cloudflare read access to the repository). Documented in Cloudflare's Pages docs; not tried.
- `foundrynorth.studio` is not a registered domain: 1.1.1.1 answers Non-existent domain, and the .studio registry's RDAP answers 404 Object not found. Checked 15 Oct 02:04. So the email button uses `rhys@foundrynorthstudios.co.uk` (his letter "A", the master's call on the mailbox; tried with a test email at the sign-off sitting).
- Today's error page is Cloudflare's own (Server: cloudflare, served from London), 525. Checked: `curl -I`, 07:30 UTC.

## Design
Ruled 15 Oct 2026 (the look: "C please"; the design page `docs/pages/2026-10-15-design-sheet-1.html`: letters 1 a, 2 b).

**The look: style C, Rose.** Porcelain base (`#e7ede6`, ink `#0e1512`, body `#4a5750`) with the rose accent (`#e9b4b7`, deep `#d1808c`, hot `#c46b7a`, labels `#9c6f79`, hairline `#c99c85`); centred and airy; ink pill buttons; rose only on the engine things (the waveform in the film frame, the step marks); rose-gold hairlines, warm shadows. Tagline "An engine that understands you better every month." The offer is called "your own mini studio". The look is `C:\Users\3070s\AiEngineering\scratch\foundry-north-look-2026-10-15\style-c-rose.html`, with the helper's `NOTES.md` beside it: reference for the build, not its code.

**The page, in order:** the name "Foundry North" set in type with the email button · the top, leading with the result, naming neither buyer · the film space ("Film coming soon", 16:9, built so the film drops in) · how it works in three steps · for founders · for organisations (teams, schools, companies) · why trust us (only what is true and public: "Built by filmmakers. Fifteen years of craft.", "The last cut is human. Every time.") · contact, one email button to `mailto:rhys@foundrynorthstudios.co.uk`. Phone first. Search basics and the link preview. Words drafted from his voice rules (digest § 7) and approved by him line by line before going live.

**The journey (the design page's picture):** built → the private preview on his phone (tailnet only) → he approves the words and the page (his hand) → Cloudflare publishes it once he connects it and switches the address (his hand) → a visitor at foundrynorthstudios.co.uk and `www.` → an email to his Zoho inbox. Nothing is public until both of his steps are done.

**Where the site's files live: a repository of its own, holding only the site** (his letter "b" on question 2; the master had recommended a). Cloudflare sees the site and nothing else. Making that repository is his act (about 2 minutes); how a checked change in this project reaches it is a piece of the plan.

**Deliberately left out** (from the scope): more pages, a form, a booking tool, a price, visitor counting, client stories, any change to the email, the portal or the other sub-addresses. The film waits for his film.

References he named (rulings 3 and 4 of 14 Oct 2026 02:47): https://land-book.com/websites/95602-kvant-executive-search ; https://foundercontentengine.com/

## The team
<not ruled yet>

## The plan
<not ruled yet>
