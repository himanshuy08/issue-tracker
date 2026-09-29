from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_issue():
    r = client.post("/issues", json={"title": "Login bug", "priority": "high"})
    assert r.status_code == 201
    issue_id = r.json()["id"]
    assert client.get(f"/issues/{issue_id}").json()["title"] == "Login bug"


def test_update_status():
    issue_id = client.post("/issues", json={"title": "Bug"}).json()["id"]
    r = client.patch(f"/issues/{issue_id}", json={"status": "closed"})
    assert r.json()["status"] == "closed"


def test_empty_title_rejected():
    assert client.post("/issues", json={"title": ""}).status_code == 422


def test_missing_issue_returns_404():
    assert client.get("/issues/999999").status_code == 404
