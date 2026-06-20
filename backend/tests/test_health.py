"""Tests for /api/health endpoints"""


def test_health_check(client):
    res = client.get("/api/health/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "timestamp" in body
    assert body["service"] == "Multimedia Summary API"


def test_health_readiness(client):
    res = client.get("/api/health/ready")
    assert res.status_code == 200
    body = res.json()
    assert body["ready"] is True
    assert "components" in body


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "online"
    assert "docs" in body
