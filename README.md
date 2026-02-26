# KeyCrack

![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker&logoColor=white)
![Ruff](https://img.shields.io/badge/linter-Ruff-D7FF64?logo=ruff&logoColor=black)
![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Live demo:** [keycrack.onrender.com](https://keycrack.onrender.com/) ***--> (might have to wait a couple seconds)***

KeyCrack is a password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and it uses a probabilistic context-free grammar (PCFG) to generate the most likely password candidates -- each ranked by probability. Educational and portfolio project -- nothing is stored.

## How It Works

KeyCrack uses a **probabilistic context-free grammar (PCFG)** to model how people build passwords from personal information:

1. **30 structural templates** define common password patterns (e.g. `{Name}{123}`, `{Name}{BirthYear}`, `{DOB}{Name}`)
2. Each template carries a **base probability** reflecting how common that pattern is in practice
3. Slots in each template expand into **concrete values** (first name, last name, pet name, date-of-birth parts) with their own probability distributions
4. **Case variations** (lowercase, capitalized, uppercase) are applied with weighted probabilities
5. The final probability of a password is the **product** of its template and slot probabilities
6. The **top 30** most probable passwords are selected with diversity capping (max 2 per template) to avoid repetition
7. Results are grouped into 5 categories: **Name-Based**, **Leet Speak**, **Name + DOB**, **DOB + Name**, **DOB Only**

## Tech Stack

| Technology | Role in the app |
|---|---|
| **Python** | All backend logic; uses a PCFG engine to generate and rank password candidates from personal info, including leet speak transforms and case variations |
| **FastAPI** | Serves the single-page frontend and exposes a POST `/generate` endpoint; Pydantic models validate and sanitize input before it reaches the generator |
| **HTML / CSS / JS** | Self-contained single-page frontend; CSS handles the hacker-themed UI with matrix rain canvas animation and responsive layout; JS manages form submission, fetch to the API, and typing animation for results |
| **pytest** | 55 unit tests covering generation logic and API endpoint behavior |
| **Docker** | Python 3.12-slim container with docker-compose for one-command local deployment; same image powers production |
| **GitHub Actions** | CI pipeline runs Ruff linting and pytest on every push and PR |
| **Ruff** | Fast Python linter enforcing code quality |
| **Render** | Cloud deployment platform running the Docker container |

## Security & Privacy

KeyCrack is designed so that user input never persists anywhere:

- No database, no file writes, no caching -- all generation is in-memory and discarded after the response
- No logging of request bodies or user input (uvicorn only logs method/path/status)
- No third-party scripts, analytics, tracking pixels, or CDN dependencies on the frontend
- No localStorage, cookies, or sessionStorage
- The only network call is a relative fetch to `/generate` -- no data leaves the origin
- No Docker volumes -- container logs are ephemeral
- Input is sanitized (`strip_to_alpha`) and validated (Pydantic + `validate_dob`) before processing

## What's next

- UI/UX design
- Expand template library with more structural patterns

---

#### Made by PK Lauvstad (w/AI assistance)
