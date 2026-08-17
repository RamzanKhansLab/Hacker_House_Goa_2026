from fastapi.testclient import TestClient

from app.main import create_app


def test_health_ready_and_query_endpoints() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").json()["index_ready"]
        response = client.post("/api/v1/query", json={"query": "What is retrieval augmented generation?"})
        assert response.status_code == 200
        assert response.json()["grounded"] is True


def test_voice_endpoint_uses_demo_stt() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/voice", files={"audio": ("voice.webm", b"demo-audio", "audio/webm")})
        assert response.status_code == 200
        assert response.json()["transcript"] == "What is retrieval augmented generation?"
