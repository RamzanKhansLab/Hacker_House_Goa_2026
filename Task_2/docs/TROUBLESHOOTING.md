# Troubleshooting

| Symptom | Check |
| --- | --- |
| `/ready` is degraded | confirm `INDEX_PATH`, or remove it to use the committed demo corpus; run `python -m ingestion.build_index --demo` for an artifact |
| Sarvam STT fails | set `DEMO_MODE=false`, check `SARVAM_API_KEY`, send a non-empty supported short audio file, and inspect provider status without logging key values |
| LLM unavailable | verify `LLM_PROVIDER=openai_compatible`, base URL, model, key, timeout, and provider compatibility with `/chat/completions` |
| `sentence-transformers` import error | install `python -m pip install -e ".[ml]"` or set `EMBEDDING_BACKEND=hash` |
| frontend cannot reach API | set `VITE_API_URL`, add its origin to `ALLOWED_ORIGINS`, then restart backend |
| npm blocked in PowerShell | use `npm.cmd install` and `npm.cmd run build` |
| no answer/source | query may be off-topic or below `MIN_RETRIEVAL_SCORE`; validate the index rather than lowering safety thresholds blindly |

For a fresh environment, delete only Task 2 generated artifacts such as `data/index/` (which is ignored), then rebuild. Never delete project source or secrets as part of routine troubleshooting.
