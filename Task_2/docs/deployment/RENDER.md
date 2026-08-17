# Render

Create a Render Blueprint from `render.yaml` with `Task_2` as the service root. The Docker service runs in demo mode by default and exposes `/health` for health checks. This validates service wiring without a dataset download during every build.

For production, set server-side environment variables in Render: `DEMO_MODE=false`, Sarvam values, LLM values, index/Qdrant values, `ALLOWED_ORIGINS`, and resource bounds. Prepare the index offline or use Qdrant before deployment. Test `/ready`, a typed query, and a short real voice upload after changing provider configuration. A free instance may cold-start; do not claim it is always on.
