# KeyCrack

![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg)

**Live demo:** [keycrack.onrender.com](https://keycrack.onrender.com/)

KeyCrack is a password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and it generates a ranked list of common password combinations. Educational and portfolio project -- nothing is stored.

## How It Was Built

1. **Core Logic** -- Started with the generation engine in the terminal. Pass in a name, DOB, and pet name, get a password list back.
2. **Web App** -- Added FastAPI backend and an HTML form. End-to-end flow, all in-memory.
3. **Polished Experience** -- Hacker-themed UI with matrix rain animation, loading animations, sample templates, privacy disclaimer, and strength tips.
4. **Testing and Containerization** -- Added 56 pytest tests covering generation logic and API endpoints. Containerized with Docker and docker-compose.
5. **CI/CD Pipeline** -- GitHub Actions running tests and Ruff linting on every push and PR.
6. **Live Deployment** -- Deployed to Render.com using Docker runtime. The app is live at [keycrack.onrender.com](https://keycrack.onrender.com/).

## Features

- Password generation from personal info (name, DOB, pet name)
- Smart scoring algorithm that ranks the top 30 most likely passwords
- 19 distinct password pattern strategies
- Hacker-themed frontend with matrix rain animation
- Loading animation with sequential status lines
- Sample templates for quick testing
- Privacy-first: all generation happens in-memory, nothing stored

## Tech Stack

- Python
- FastAPI
- HTML / CSS / JS
- pytest
- Docker + docker-compose
- GitHub Actions (CI/CD)
- Ruff (linting)
- Render (deployment)

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   For development (includes Ruff linter):

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run the web server:

   ```bash
   python run_web.py
   ```

4. Open your browser to [http://localhost:8000](http://localhost:8000)

## Usage

1. **Fill in the form** -- enter your First Name, Last Name, Date of Birth (MMDDYYYY format), and optionally a Pet Name
2. **Or click a sample template** -- three pre-filled examples let you try it out instantly
3. **Click GENERATE** -- the app builds thousands of password combinations from your input
4. **View results** -- see the top 30 most likely passwords with a typing animation, a breakdown chart by category, and expandable sections for all 5 categories

## Testing

56 tests covering core generation logic and API endpoints.

```bash
python -m pytest tests/ -v
```

## Linting

Ruff runs automatically in CI on every push and PR.

```bash
ruff check .
```

## Docker

Docker builds a lightweight container (Python 3.12-slim) with all dependencies baked in. The same Docker setup powers the live deployment on Render.

```bash
docker-compose up --build
```

Then open [http://localhost:8000](http://localhost:8000)

## Privacy Disclaimer

KeyCrack is for educational purposes only. No information is stored, logged, or shared.

---

Created by PKL
