# KeyCrack

[![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg)](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-client--side-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-deployed-222?logo=github&logoColor=white)](https://pklauvstad.github.io/KeyCrack/)
[![Ruff](https://img.shields.io/badge/linter-Ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and KeyCrack uses a probabilistic context-free grammar (PCFG) to generate the most likely password candidates -- each ranked by probability. Runs entirely in your browser -- nothing is stored, no server needed.

**Live demo:** [pklauvstad.github.io/KeyCrack](https://pklauvstad.github.io/KeyCrack/)

> **Tip:** The UI is hacker-themed -- matrix rain, scanlines, green-on-black. Try one of the 6 sample personas for an instant demo.

---

## :brain: How It Works

KeyCrack uses a **probabilistic context-free grammar (PCFG)** to model how people build passwords from personal information:

1. **30 structural templates** define common password patterns (e.g. `{Name}{123}`, `{Name}{BirthYear}`, `{DOB}{Name}`)
2. Each template carries a **base probability** reflecting how common that pattern is in practice
3. Slots in each template expand into **concrete values** (first name, last name, pet name, date-of-birth parts) with their own probability distributions
4. **Case variations** (lowercase, capitalized, uppercase) are applied with weighted probabilities
5. The final probability of a password is the **product** of its template and slot probabilities
6. The **top 30** most probable passwords are selected with diversity capping (max 2 per template) to avoid repetition
7. Results are grouped into 5 categories: **Name-Based**, **Leet Speak**, **Name + DOB**, **DOB + Name**, **DOB Only**

---

## :sparkles: Features

- **PCFG generation engine** -- 30 templates, probability-ranked, diversity-capped top 30
- **100% client-side** -- All generation runs in your browser via JavaScript, no server calls
- **Instant loading** -- Static site hosted on GitHub Pages, no cold starts
- **Hacker-themed UI** -- Matrix rain canvas, scanline overlay, monospace fonts, green-on-black
- **Typing animation** -- Passwords appear character by character with probability scores
- **Sample personas** -- 6 quick-fill buttons to demo generation instantly
- **Privacy-first** -- Nothing leaves your browser, no data stored anywhere

---

## :hammer_and_wrench: Built With

| Category | Technology |
|---|---|
| **Engine** | JavaScript (client-side PCFG algorithm) |
| **Frontend** | HTML, CSS, JavaScript (vanilla, no frameworks) |
| **Reference impl.** | Python 3.12 (original algorithm) |
| **Testing** | pytest (Python) + Node.js assert (JS) |
| **Linting** | Ruff |
| **CI/CD** | GitHub Actions |
| **Hosting** | GitHub Pages |

---

## :lock: Security & Privacy

KeyCrack runs entirely in your browser -- no data ever leaves your machine:

- All password generation happens client-side in JavaScript -- no server, no network calls
- No database, no logging, no analytics, no tracking
- No third-party scripts, CDN dependencies, localStorage, cookies, or sessionStorage
- Input is sanitized (`stripToAlpha`) and validated (`validateDob`) before processing
- The site is two static files (`index.html` + `pcfg.js`) -- nothing else

---

## :open_file_folder: Project Structure

```
docs/                        # Static site (GitHub Pages)
├── index.html               # Main UI with matrix rain + typing animation
├── pcfg.js                  # Client-side PCFG engine (JS port)
├── supabase-config.js       # Supabase API config + helpers
├── report-bug.html          # Bug report form (writes to Supabase)
└── admin-bugs.html          # Admin dashboard (Supabase Auth login)
keycrack/                    # Python reference implementation
├── generator.py             # Data types, validation, leet speak
├── pcfg.py                  # PCFG engine, templates, probability math
└── web/
    ├── app.py               # FastAPI routes (legacy server version)
    └── static/index.html    # Original server-rendered UI
tests/
├── test_pcfg.mjs            # JS engine tests (Node.js assert)
├── test_pcfg.py             # Python PCFG tests (pytest)
├── test_generator.py        # Python generator tests
├── test_api.py              # Python API tests
└── test_bugs.py             # Python bug reporting tests
```

---

## :brain: What I Learned

<details>
<summary><strong>Python</strong></summary>

- Building a PCFG algorithm from scratch with dataclasses and probability math
- Leet speak character mapping and weighted random transforms
- Designing a template system with slot expansion and diversity capping
</details>

<details>
<summary><strong>FastAPI</strong></summary>

- Pydantic models for input validation and sanitization
- Lifespan events for async database setup/teardown
- Async request handling with background DB operations
- Serving static files alongside API routes
- HTTP Basic Auth for admin endpoints
</details>

<details>
<summary><strong>Database</strong></summary>

- Dual-mode architecture: PostgreSQL (Supabase) in production, SQLite locally
- Async drivers (asyncpg + aiosqlite) with a unified interface
- Schema management across two different database backends
</details>

<details>
<summary><strong>Frontend</strong></summary>

- HTML5 Canvas for the matrix rain animation
- Character-by-character typing effect with probability scores
- Fetch API for async form submission
- Responsive hacker-themed design without any frameworks or libraries
</details>

<details>
<summary><strong>DevOps</strong></summary>

- GitHub Pages static site deployment (zero build step)
- GitHub Actions CI pipeline (Ruff linting + pytest + Node.js tests)
- Supabase direct REST API integration from the browser
</details>

---

## :seedling: How This Project Evolved

KeyCrack started as a terminal-only proof of concept -- type in a name and DOB, get a list of likely passwords printed to stdout.

From there it grew through many stages: the basic generator was replaced with a full **PCFG engine** (30 templates, probability ranking, diversity capping). Then came a **FastAPI web app** with a hacker-themed UI featuring matrix rain and typing animations, hosted on Render with Supabase for bug reports.

Most recently, the PCFG algorithm was **ported to JavaScript** to run entirely client-side. The site is now hosted on **GitHub Pages** as a static site -- instant loading, no server, no cold starts. The Python code remains as the reference implementation.

---

## :page_facing_up: License

This project is licensed under the [MIT License](LICENSE).

---

#### Made by PK Lauvstad (w/AI assistance)
