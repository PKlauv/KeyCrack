# KeyCrack

KeyCrack is a password awareness tool designed to educate users about the predictability of their passwords. By inputting personal information (such as name, date of birth, pet name, etc.), KeyCrack generates a list of common password combinations, demonstrating how easily personal data can be used to guess passwords. This project is for educational and portfolio purposes—no data is stored.

## Features

- Generates password lists based on user-provided personal info
- FastAPI backend with a simple HTML frontend
- CLI and web interface options
- Privacy-first: no data is stored or logged
- Docker and docker-compose support
- Unit tests with pytest
- CI/CD workflow with GitHub Actions

## MVP Roadmap

- **MVP 0:** Core generation logic (terminal only)
- **MVP 1:** Functional web app (FastAPI + HTML form)
- **MVP 2:** Polished UI, loading animation, privacy disclaimer, strength tips
- **MVP 3:** Unit tests, Dockerization
- **MVP 4:** CI/CD, README, professional workflow

## Tech Stack

- Python
- FastAPI
- HTML/CSS (frontend)
- pytest (testing)
- Docker, docker-compose
- GitHub Actions (CI/CD)

## Usage

### CLI

Run the generator from the terminal:

```bash
python -m keycrack.cli
```

### Web

Start the FastAPI server:

```bash
python run_web.py
```

Then open your browser to [http://localhost:8000](http://localhost:8000).

### Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

## Privacy Disclaimer

KeyCrack is for educational purposes only. No information is stored, logged, or shared.

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run CLI or web as above

## Portfolio

Created by PKL for educational and portfolio demonstration.
