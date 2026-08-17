# API

Interactive OpenAPI is served at `/docs` and schema JSON at `/openapi.json`.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | process liveness |
| `/ready` | GET | index readiness and non-secret manifest |
| `/api/v1/query` | POST | typed RAG request |
| `/api/v1/voice` | POST | audio upload → STT → RAG |
| `/api/v1/metrics` | GET | development-safe aggregate state |

`POST /api/v1/query` accepts `{"query":"What is RAG?","language":"en","cross_language":false}`. `POST /api/v1/voice` accepts multipart `audio`, optional `language_hint`, and optional `cross_language`. Accepted audio includes WAV, MP3, M4A, OGG, WebM, FLAC, and AAC up to `MAX_AUDIO_SIZE_MB`; production Sarvam REST is designed for short clips.

Successful responses include answer, sources, confidence, grounding decision, guardrail status, request ID, language, transcript where applicable, and stage latency. Errors use a stable `{request_id,error,detail}` shape and never intentionally expose stack traces.
