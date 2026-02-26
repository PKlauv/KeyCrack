# KeyCrack

![CI](https://github.com/PKlauv/KeyCrack/actions/workflows/ci.yml/badge.svg) 

**Live demo:** [keycrack.onrender.com](https://keycrack.onrender.com/) ***--> (might have to wait a couple seconds)***

KeyCrack is a password awareness tool that shows how predictable your passwords might be. Enter personal info (name, DOB, pet name), and it generates a ranked list of the top 30 most likely password combinations out of thousands, scored across 19 distinct pattern strategies. Educational and portfolio project -- nothing is stored.

## Tech Stack

| Technology | Role in the app |
|---|---|
| **Python** | All backend logic; generates thousands of password combinations from personal info using pattern matching, leet speak transforms, and a scoring algorithm |
| **FastAPI** | Serves the single-page frontend and exposes a POST `/generate` endpoint; Pydantic models validate and sanitize input before it reaches the generator |
| **HTML / CSS / JS** | Self-contained single-page frontend; CSS handles the hacker-themed UI with matrix rain canvas animation and responsive layout; JS manages form submission, fetch to the API, and typing animation for results |
| **pytest** | 56 unit tests covering generation logic and API endpoint behavior |
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

---

Made by PK Lauvstad with assistance of artificial intellegence
