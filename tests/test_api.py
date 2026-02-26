import pytest
from fastapi.testclient import TestClient

from keycrack.web.app import app

VALID_PAYLOAD = {
    "first_name": "john",
    "last_name": "doe",
    "dob": "03141983",
    "pet_name": "buddy",
}

EXPECTED_CATEGORIES = {"name_based", "leet_speak", "name_dob", "dob_name", "dob_only"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    import keycrack.web.db as db_module
    monkeypatch.setattr(db_module, "DATABASE_URL", None)
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_bugs.db")
    monkeypatch.setattr(db_module, "DATA_DIR", tmp_path)
    with TestClient(app) as c:
        yield c


# --- GET / ---


class TestIndex:
    def test_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_returns_html(self, client):
        resp = client.get("/")
        assert "text/html" in resp.headers["content-type"]


# --- POST /generate (valid) ---


class TestGenerateValid:
    def test_returns_200(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        assert "categories" in data
        assert "top_passwords" in data
        assert "total_count" in data
        assert "elapsed_seconds" in data

    def test_categories_has_five_keys(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        assert set(data["categories"].keys()) == EXPECTED_CATEGORIES

    def test_top_passwords_max_30(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        assert len(data["top_passwords"]) <= 30

    def test_top_passwords_have_probability(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        for entry in data["top_passwords"]:
            assert "password" in entry
            assert "probability" in entry
            assert isinstance(entry["password"], str)
            assert isinstance(entry["probability"], float)
            assert entry["probability"] > 0

    def test_total_count_positive(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        assert data["total_count"] > 0

    def test_elapsed_seconds_is_float(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        assert isinstance(data["elapsed_seconds"], float)

    def test_category_detail_structure(self, client):
        resp = client.post("/generate", json=VALID_PAYLOAD)
        data = resp.json()
        for key, cat in data["categories"].items():
            assert "label" in cat
            assert "description" in cat
            assert "passwords" in cat
            assert "count" in cat
            assert isinstance(cat["passwords"], list)
            assert cat["count"] == len(cat["passwords"])


# --- POST /generate (invalid) ---


class TestGenerateInvalid:
    def test_bad_dob_format(self, client):
        payload = {**VALID_PAYLOAD, "dob": "abcdefgh"}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422

    def test_bad_dob_month(self, client):
        payload = {**VALID_PAYLOAD, "dob": "13141983"}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422

    def test_bad_dob_day(self, client):
        payload = {**VALID_PAYLOAD, "dob": "03321983"}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422

    def test_empty_first_name(self, client):
        payload = {**VALID_PAYLOAD, "first_name": ""}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422

    def test_no_alpha_first_name(self, client):
        payload = {**VALID_PAYLOAD, "first_name": "123"}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422

    def test_empty_last_name(self, client):
        payload = {**VALID_PAYLOAD, "last_name": ""}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422


# --- POST /generate (optional pet) ---


class TestGenerateOptionalPet:
    def test_missing_pet_name_succeeds(self, client):
        payload = {
            "first_name": "john",
            "last_name": "doe",
            "dob": "03141983",
        }
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200

    def test_empty_pet_name_succeeds(self, client):
        payload = {**VALID_PAYLOAD, "pet_name": ""}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200

    def test_pet_name_null_succeeds(self, client):
        payload = {**VALID_PAYLOAD, "pet_name": None}
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
