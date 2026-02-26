import pytest
from fastapi.testclient import TestClient

from keycrack.web.app import app

ADMIN_AUTH = ("testadmin", "testpass")


@pytest.fixture
def client(tmp_path, monkeypatch):
    import keycrack.web.app as app_module
    monkeypatch.setattr(app_module, "DB_PATH", tmp_path / "test_bugs.db")
    monkeypatch.setattr(app_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(app_module, "ADMIN_USER", "testadmin")
    monkeypatch.setattr(app_module, "ADMIN_PASS", "testpass")
    with TestClient(app) as c:
        yield c


VALID_BUG = {
    "description": "The submit button does not work",
    "category": "UI issue",
}


# --- GET /report-bug ---


class TestReportBugPage:
    def test_returns_200(self, client):
        resp = client.get("/report-bug")
        assert resp.status_code == 200

    def test_returns_html(self, client):
        resp = client.get("/report-bug")
        assert "text/html" in resp.headers["content-type"]


# --- POST /api/bugs ---


class TestSubmitBug:
    def test_valid_submission(self, client):
        resp = client.post("/api/bugs", json=VALID_BUG)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["id"] == 1
        assert "message" in data

    def test_missing_description(self, client):
        resp = client.post("/api/bugs", json={"category": "Other"})
        assert resp.status_code == 422

    def test_empty_description(self, client):
        resp = client.post("/api/bugs", json={"description": "", "category": "Other"})
        assert resp.status_code == 422

    def test_too_long_description(self, client):
        resp = client.post("/api/bugs", json={"description": "x" * 501, "category": "Other"})
        assert resp.status_code == 422

    def test_invalid_category(self, client):
        resp = client.post("/api/bugs", json={"description": "bug", "category": "Nonsense"})
        assert resp.status_code == 422

    def test_email_optional(self, client):
        resp = client.post("/api/bugs", json=VALID_BUG)
        assert resp.status_code == 201

    def test_email_included(self, client):
        payload = {**VALID_BUG, "email": "test@example.com"}
        resp = client.post("/api/bugs", json=payload)
        assert resp.status_code == 201

    def test_category_defaults_to_other(self, client):
        resp = client.post("/api/bugs", json={"description": "something broke"})
        assert resp.status_code == 201
        bugs = client.get("/api/bugs", auth=ADMIN_AUTH).json()
        assert bugs[0]["category"] == "Other"


# --- GET /admin/bugs ---


class TestAdminBugsPage:
    def test_returns_200(self, client):
        resp = client.get("/admin/bugs", auth=ADMIN_AUTH)
        assert resp.status_code == 200

    def test_returns_html(self, client):
        resp = client.get("/admin/bugs", auth=ADMIN_AUTH)
        assert "text/html" in resp.headers["content-type"]

    def test_rejects_no_credentials(self, client):
        resp = client.get("/admin/bugs")
        assert resp.status_code == 401

    def test_rejects_wrong_credentials(self, client):
        resp = client.get("/admin/bugs", auth=("wrong", "creds"))
        assert resp.status_code == 401


# --- GET /api/bugs ---


class TestListBugs:
    def test_empty_list(self, client):
        resp = client.get("/api/bugs", auth=ADMIN_AUTH)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_submit(self, client):
        client.post("/api/bugs", json={"description": "first bug"})
        client.post("/api/bugs", json={"description": "second bug"})
        resp = client.get("/api/bugs", auth=ADMIN_AUTH)
        bugs = resp.json()
        assert len(bugs) == 2
        assert bugs[0]["description"] == "second bug"
        assert bugs[1]["description"] == "first bug"

    def test_field_correctness(self, client):
        payload = {
            "description": "test bug",
            "email": "a@b.com",
            "category": "Crash",
        }
        client.post("/api/bugs", json=payload)
        bugs = client.get("/api/bugs", auth=ADMIN_AUTH).json()
        bug = bugs[0]
        assert bug["description"] == "test bug"
        assert bug["email"] == "a@b.com"
        assert bug["category"] == "Crash"
        assert "created_at" in bug
        assert "id" in bug

    def test_rejects_no_credentials(self, client):
        resp = client.get("/api/bugs")
        assert resp.status_code == 401

    def test_rejects_wrong_credentials(self, client):
        resp = client.get("/api/bugs", auth=("wrong", "creds"))
        assert resp.status_code == 401
