# KeyCrack

[![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg)](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Ruff](https://img.shields.io/badge/linter-Ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Render](https://img.shields.io/badge/Render-deployed-46E3B7?logo=render&logoColor=white)](https://render.com/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and KeyCrack uses a probabilistic context-free grammar (PCFG) to generate the most likely password candidates -- each ranked by probability. Educational and portfolio project -- nothing is stored.

**Live demo:** [keycrack.onrender.com](https://keycrack.onrender.com/) -- *(might take a few seconds to spin up)*

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
- **Hacker-themed UI** -- Matrix rain canvas, scanline overlay, monospace fonts, green-on-black
- **Typing animation** -- Passwords appear character by character with probability scores
- **Sample personas** -- 6 quick-fill buttons to demo generation instantly
- **Bug reporting** -- `/report-bug` with 4 categories, optional email for follow-up
- **Admin dashboard** -- HTTP Basic Auth protected at `/admin/bugs`
- **Privacy-first** -- Password input never stored, only bug reports persist

---

## :hammer_and_wrench: Built With

| Category | Technology |
|---|---|
| **Backend** | Python 3.12 + FastAPI |
| **Frontend** | HTML, CSS, JavaScript (vanilla, no frameworks) |
| **Database** | Supabase (PostgreSQL) / SQLite fallback |
| **DB Drivers** | asyncpg + aiosqlite |
| **Testing** | pytest (74 tests) |
| **Linting** | Ruff |
| **Containerization** | Docker + docker-compose |
| **CI/CD** | GitHub Actions |
| **Hosting** | Render |

---

## :lock: Security & Privacy

KeyCrack is designed so that password generation input never persists anywhere:

- Password generation is entirely in-memory -- input is discarded after the response
- The only data stored in the database is user-submitted bug reports (category, description, optional email)
- No logging of request bodies or user input (uvicorn only logs method/path/status)
- No third-party scripts, analytics, tracking pixels, or CDN dependencies on the frontend
- No localStorage, cookies, or sessionStorage
- The only network calls are relative fetches to `/generate` and `/report-bug` -- no data leaves the origin
- No Docker volumes -- container logs are ephemeral
- Input is sanitized (`strip_to_alpha`) and validated (Pydantic + `validate_dob`) before processing

---

## :open_file_folder: Project Structure

```
keycrack/
├── __init__.py
├── generator.py          # Original generator (MVP 0)
├── pcfg.py               # PCFG engine, templates, probability math
└── web/
    ├── __init__.py
    ├── app.py             # FastAPI routes and lifespan
    ├── db.py              # Async DB layer (Supabase / SQLite)
    └── static/
        ├── index.html     # Main UI with matrix rain + typing animation
        ├── report-bug.html
        └── admin-bugs.html
tests/
├── test_api.py            # API endpoint tests
├── test_bugs.py           # Bug reporting + admin tests
├── test_generator.py      # Original generator tests
└── test_pcfg.py           # PCFG engine + probability tests
Dockerfile
docker-compose.yml
run_web.py                 # Entry point for local dev
pyproject.toml
requirements.txt
requirements-dev.txt
render.yaml                # Render deployment config
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

- Docker with Python 3.12-slim base image
- docker-compose for one-command local deployment
- GitHub Actions CI pipeline (Ruff linting + pytest)
- Render deployment with environment variable management
</details>

---

## :seedling: How This Project Evolved

KeyCrack started as a terminal-only proof of concept -- type in a name and DOB, get a list of likely passwords printed to stdout.

From there it grew through MVP stages: the basic generator was replaced with a full **PCFG engine** (30 templates, probability ranking, diversity capping). Then came the **FastAPI web app** with a hacker-themed UI featuring matrix rain and typing animations. **Bug reporting** and an **admin dashboard** followed, backed by Supabase in production with SQLite fallback for local dev. Finally, **Docker containerization**, a **GitHub Actions CI pipeline**, and **Render deployment** brought it to production.

---

## :page_facing_up: License

This project is licensed under the [MIT License](LICENSE).

---

#### Made by PK Lauvstad (w/AI assistance)
