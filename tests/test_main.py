from app.main import app


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_root():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Hello" in resp.get_json()["message"]
