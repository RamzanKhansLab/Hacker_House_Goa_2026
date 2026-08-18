# Security

Secrets are server-only environment variables. Never commit `.env`, Sarvam/LLM/Qdrant keys, private certificates, raw customer voice clips, or frontend variables beginning with a provider key. `.env.example` contains empty secret values only.

The API enforces a media allow-list, audio byte limit, request concurrency bound, and a per-instance rate limiter. Production should place TLS, authentication, centralized rate limiting, secret rotation, and request-size enforcement at the deployment edge. The included in-memory limiter is not suitable for multiple replicas.

Retrieved text is untrusted. The generation prompt tells the model not to follow context instructions, and injection-pattern queries are blocked before retrieval. Logs use request IDs and timings; do not log transcript/audio/query bodies in production without a privacy policy and explicit retention controls.
