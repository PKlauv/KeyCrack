# KeyCrack

KeyCrack is a password awareness tool designed to educate users about the predictability of their passwords. By inputting personal information (such as name, date of birth, pet name, etc.), KeyCrack generates a list of common password combinations, demonstrating how easily personal data can be used to guess passwords. This project is for educational and portfolio purposes -- no data is stored.

## Features

- Password generation from personal info (name, DOB, pet name)
- Smart scoring algorithm that ranks the top 30 most likely passwords
- 19 distinct password pattern strategies (sequential numbers, birth year, initials, compound words, separators, and more)
- FastAPI backend with a single POST endpoint
- Hacker-themed frontend with matrix rain animation
- Loading animation with sequential status lines
- Sample templates for quick testing
- Privacy-first: all generation happens in-memory, nothing stored

## MVP Roadmap

- **MVP 0:** Core generation logic (terminal only) -- Done
- **MVP 1:** Functional web app (FastAPI + HTML form) -- Done
- **MVP 2:** Hacker-themed UI, loading animation, privacy disclaimer, strength tips -- Done
- **MVP 3:** Unit tests, Dockerization -- Done (current)
- **MVP 4:** CI/CD, professional workflow -- Upcoming
- **MVP 5:** Deployment (live on the internet) -- Upcoming

## Tech Stack

- Python
- FastAPI
- HTML / CSS / JS
- pytest
- Docker + docker-compose

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the web server:

   ```bash
   python run_web.py
   ```

4. Open your browser to [http://localhost:8000](http://localhost:8000)

## Usage

1. **Fill in the form** -- enter your First Name, Last Name, Date of Birth (MMDDYYYY format), and optionally a Pet Name
2. **Or click a sample template** -- three pre-filled examples (James Wilson, Sarah Miller, Tyler Brooks) let you try it out instantly
3. **Click GENERATE** -- the app builds thousands of password combinations from your input
4. **View results** -- see the top 20 most likely passwords with a typing animation, a breakdown chart by category, and expandable sections for all 5 categories (Name-Based, Leet Speak, Name + DOB, DOB + Name, DOB Only)

## Testing

The test suite includes 42 tests across two files: `test_generator.py` validates the core logic (input parsing, password generation, scoring, and category classification) and `test_api.py` validates the FastAPI endpoints (valid/invalid payloads, response structure, and optional fields). Run them after making changes to the generation logic or API to make sure nothing broke.

```bash
python -m pytest tests/ -v
```

## Docker

Docker builds a lightweight container (Python 3.12-slim) with all dependencies baked in, so you don't need Python installed locally. Use it if you want to run the app without setting up a Python environment, or to test that it works in a clean, isolated setup. The container auto-restarts on failure. This same Docker setup is the foundation for deploying the app live (MVP 5) to platforms like Railway, Render, or Fly.io.

```bash
docker-compose up --build
```

Then open [http://localhost:8000](http://localhost:8000)

## Privacy Disclaimer

KeyCrack is for educational purposes only. No information is stored, logged, or shared.

## Portfolio

Created by PKL for educational and portfolio demonstration.
