# Docker deployment

Build and run from `Task_2`:

```bash
docker build -t goa-voice-rag .
docker run --rm -p 8000:8000 --env-file .env goa-voice-rag
```

The image does not build an MSMARCO-XI index. Mount/provide a prepared index if using local storage, or configure Qdrant. Verify `GET /health` and `GET /ready` after startup. Build the frontend separately; it is deliberately not bundled with the backend image.
