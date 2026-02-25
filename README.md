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

## Testing

```bash
python -m pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
```

Then open [http://localhost:8000](http://localhost:8000)

## Privacy Disclaimer

KeyCrack is for educational purposes only. No information is stored, logged, or shared.

## Portfolio

Created by PKL for educational and portfolio demonstration.
