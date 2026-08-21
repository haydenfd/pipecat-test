---
name: visualize-bot
description: >
  Rebuild the bot-side Pipecat interview visual explainer as a single in-repo
  HTML report. Use when the user says "visualize pipecat", "visualize bot",
  "update bot diagram", "refresh bot flow", "bot architecture diagram", or
  asks to re-render how the interview bot works after flow/pipeline changes.
  Manual only — never run from hooks or on every edit. Bot-side Python only
  (exclude client/). Always overwrite docs/bot-flow/index.html in the repo root.
license: MIT
compatibility: >
  OpenCode and Codex (Agent Skills). Requires a browser to view the HTML.
  Optional: visual-explainer skill patterns for Mermaid/CSS quality.
metadata:
  audience: developers
  workflow: understanding
  output: docs/bot-flow/index.html
---

# Visualize Bot (Pipecat interview flow)

Manual teaching diagram for **this repo's bot-side code**. Every run **overwrites**
one stable path so you always open the same file after changes.

## Triggers (invoke only on these — never automatic)

- "visualize pipecat"
- "visualize bot"
- "update bot diagram" / "refresh bot flow"
- "bot architecture" / "how does the interview flow work" (when they want a visual)

Do **not** run on commit, save, PR, or background hooks.

## Hard output contract

| Rule | Value |
|------|--------|
| Output path | `<repo-root>/docs/bot-flow/index.html` |
| Behavior | **Overwrite** that file every run (single living document) |
| Not allowed | `~/.agent/diagrams/`, timestamped copies, multiple HTML files |
| Scope | Bot-side only: `bot.py`, `flow.py`, `services.py`, `config.py`, `README.md`, `Makefile`, `pyproject.toml` |
| Exclude | `client/**`, `.venv/**`, lockfile noise |
| Open | After write, open the file in the default browser (`open` on macOS) |
| Chat reply | Short: path + 2–4 bullet "what changed / current shape" |

Resolve `<repo-root>` as the git worktree root of the current workspace (or CWD if not a git repo).

## Workflow

1. **Locate sources** at repo root. Fail clearly if `bot.py` / `flow.py` are missing.
2. **Read all bot modules** fully (`bot.py`, `flow.py`, `services.py`, `config.py`). Skim `README.md` / `Makefile` only as needed.
3. **Inventory facts** (verify from code, do not invent):
   - Pipeline processor order
   - Flow nodes (names), transitions (functions), post_actions
   - Interview question source (`INTERVIEW_QUESTION_MD` or successor)
   - Services + config defaults
   - Connect / disconnect / end_conversation lifecycle
4. **Optionally** load the `visual-explainer` skill for Mermaid shell, CSS patterns, TOC, and quality bar. If unavailable, still produce a complete self-contained HTML page using the same invariants below.
5. **Write** a complete self-contained HTML document to `docs/bot-flow/index.html` (create parent dirs).
6. **Open** the page in the browser.
7. **Reply briefly** in chat (no long paste of the HTML).

## Page requirements

Teaching page, not a dump. Prefer:

1. **Big picture** — transport ↔ pipeline ↔ FlowManager
2. **File map** — what each bot module owns
3. **Boot sequence** — process → ready for client
4. **Audio pipeline** — ordered stages from `Pipeline([...])`
5. **Interview flow graph** — every node + transition function + end
6. **Turn-by-turn** — one realistic session walkthrough
7. **Services & config** — providers and defaults
8. **Session lifecycle** — connect / idle / disconnect / end_conversation
9. **Where to look next** — reading order for ownership

### Visual rules

- Complete HTML document: embedded CSS, self-contained favicon, needed JS
- CSS variables: `--bg`, `--surface`, `--border`, `--text`, `--text-dim`, 3–5 accents
- One palette + one font pair (not Inter/Roboto/violet-default)
- Good pairs: IBM Plex Sans + IBM Plex Mono; DM Sans + Fira Code; Bricolage + JetBrains Mono
- Sticky TOC if 4+ sections (responsive-nav pattern)
- Mermaid: `theme: 'base'`, custom `themeVariables`, ELK when useful
- Every Mermaid diagram uses `diagram-shell` → zoom/pan/expand (never bare `<pre class="mermaid">`)
- Never define page-level `.node` (use `.ve-card`)
- Flowcharts: `flowchart TD` for complex graphs; `<br/>` in labels
- Hybrid if needed: small overview Mermaid + CSS detail cards
- Respect `prefers-reduced-motion`
- No secrets (API keys) in the HTML

### Aesthetic

Pick one clear direction per regen (rotate if stale): blueprint, editorial, paper/ink, or IDE-inspired. Accents: teal+slate, terracotta+sage, amber+emerald, deep blue+gold.

## Fact sources (current architecture — re-verify each run)

Code is source of truth. Typical shape as of this skill's writing (update the page if code diverged):

- **Entry:** `bot.py` → `bot()` → SmallWebRTC transport → `run_bot()`
- **Pipeline:** `transport.input` → STT → user aggregator (Silero VAD) → LLM → TTS → `transport.output` → assistant aggregator
- **Flow start:** `on_client_connected` → `flow_manager.initialize(create_intro_node())`
- **Nodes:** Intro → (`start_interview`) → Discussion → (`conclude_interview`) → Conclusion → `end_conversation`
- **Discussion:** injects full problem MD as context; bot summarizes only; one Q&A then conclude
- **Services:** Deepgram STT/TTS, Groq LLM via `services.py` + `config.py`
- **Disconnect:** `on_client_disconnected` → `worker.cancel()`

## Anti-patterns

- Writing under `~/.agent/diagrams/`
- Creating `bot-flow-v2.html` or dated filenames
- Including `client/` implementation detail
- Auto-running without an explicit user trigger
- Dumping entire source files into the page (outline + key snippets only)
- Violet/fuchsia Tailwind-default aesthetic

## Done checklist

- [ ] `docs/bot-flow/index.html` overwritten
- [ ] Facts match current `flow.py` / `bot.py`
- [ ] Mermaid diagrams have zoom/pan/expand
- [ ] Browser opened
- [ ] Short chat summary only
