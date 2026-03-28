# KeyCrack

[![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg)](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml)
[![JavaScript](https://img.shields.io/badge/JavaScript-client--side-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-deployed-222?logo=github&logoColor=white)](https://pklauvstad.github.io/KeyCrack/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and KeyCrack uses a probabilistic context-free grammar (PCFG) to generate the most likely password candidates -- each ranked by probability. Runs entirely in your browser -- nothing is stored, no server needed.

**Live demo:** [pklauv.github.io/KeyCrack](https://pklauv.github.io/KeyCrack/)

> **Tip:** The UI is hacker-themed -- matrix rain, scanlines, green-on-black. Try one of the 6 sample personas for an instant demo.

---

## How It Works

KeyCrack uses a **probabilistic context-free grammar (PCFG)** to model how people build passwords from personal information:

1. **30 structural templates** define common password patterns (e.g. `{Name}{123}`, `{Name}{BirthYear}`, `{DOB}{Name}`)
2. Each template carries a **base probability** reflecting how common that pattern is in practice
3. Slots in each template expand into **concrete values** (first name, last name, pet name, date-of-birth parts) with their own probability distributions
4. **Case variations** (lowercase, capitalized, uppercase) are applied with weighted probabilities
5. The final probability of a password is the **product** of its template and slot probabilities
6. The **top 30** most probable passwords are selected with diversity capping (max 2 per template) to avoid repetition
7. Results are grouped into 5 categories: **Name-Based**, **Leet Speak**, **Name + DOB**, **DOB + Name**, **DOB Only**

---

## Features

- **PCFG generation engine** -- 30 templates, probability-ranked, diversity-capped top 30
- **100% client-side** -- All generation runs in your browser via JavaScript, no server calls
- **Instant loading** -- Static site hosted on GitHub Pages, no cold starts
- **Hacker-themed UI** -- Matrix rain canvas, scanline overlay, monospace fonts, green-on-black
- **Typing animation** -- Passwords appear character by character with probability scores
- **Sample personas** -- 6 quick-fill buttons to demo generation instantly
- **Privacy-first** -- Nothing leaves your browser, no data stored anywhere

---

## Built With

| Category | Technology |
|---|---|
| **Engine** | JavaScript (client-side PCFG algorithm) |
| **Frontend** | HTML, CSS, JavaScript (vanilla, no frameworks) |
| **Testing** | Node.js assert (JS) |
| **CI/CD** | GitHub Actions |
| **Hosting** | GitHub Pages |

---

## Security & Privacy

KeyCrack runs entirely in your browser -- no data ever leaves your machine:

- All password generation happens client-side in JavaScript -- no server, no network calls
- No database, no logging, no analytics, no tracking
- No third-party scripts, CDN dependencies, localStorage, cookies, or sessionStorage
- Input is sanitized (`stripToAlpha`) and validated (`validateDob`) before processing
- The site is a handful of static files -- no build step, no server

---

## Project Structure

```
docs/                        # Static site (GitHub Pages)
├── index.html               # Main UI with matrix rain + typing animation
├── pcfg.js                  # Client-side PCFG engine
├── supabase-config.js       # Supabase API config + helpers
├── report-bug.html          # Bug report form (writes to Supabase)
└── admin-bugs.html          # Admin dashboard (Supabase Auth login)
tests/
└── test_pcfg.mjs            # JS engine tests (Node.js assert)
```

---

## What I Learned

<details>
<summary><strong>Algorithms</strong></summary>

- Building a PCFG algorithm from scratch with probability math
- Leet speak character mapping and weighted random transforms
- Designing a template system with slot expansion and diversity capping
</details>

<details>
<summary><strong>Frontend</strong></summary>

- HTML5 Canvas for the matrix rain animation
- Character-by-character typing effect with probability scores
- Porting a Python algorithm to client-side JavaScript
- Responsive hacker-themed design without any frameworks or libraries
</details>

<details>
<summary><strong>Backend (previous version)</strong></summary>

- Python 3.12 with FastAPI, Pydantic models, async request handling
- Docker containerization and deployment on Render
- Dual-mode database architecture: PostgreSQL (Supabase) in production, SQLite locally
- Async drivers (asyncpg + aiosqlite) with a unified interface
</details>

<details>
<summary><strong>DevOps</strong></summary>

- GitHub Pages static site deployment (zero build step)
- GitHub Actions CI pipeline
- Supabase direct REST API integration from the browser
</details>

---

## How This Project Evolved

KeyCrack started as a terminal-only proof of concept -- type in a name and DOB, get a list of likely passwords printed to stdout.

From there it grew through many stages: the basic generator was replaced with a full **PCFG engine** (30 templates, probability ranking, diversity capping). Then came a **FastAPI web app** with a hacker-themed UI featuring matrix rain and typing animations, containerized with **Docker** and hosted on **Render** with Supabase for bug reports.

That setup worked, but the ~5 second cold-start loading time on Render bugged me -- maybe a silly reason to rewrite things, but it was enough motivation. The PCFG algorithm was **ported to JavaScript** and the entire site was rebuilt as static HTML/JS, now hosted on **GitHub Pages** with instant loading and zero server dependencies. The Python backend, Docker setup, and all related infrastructure have since been removed.

Building the Docker/FastAPI version was a great learning experience though -- working with containerization, async Python, dual database backends, and deployment pipelines taught me a lot, even if the end result ended up being a few static files.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

#### Made by: PK Lauvstad