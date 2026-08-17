# Frontend deployment

Deploy `frontend/` to a static host such as Vercel, Netlify, or Render Static Site with build command `npm run build` and publish directory `dist`. Set one build-time variable: `VITE_API_URL=https://your-api.example`.

Add the static origin to backend `ALLOWED_ORIGINS`. Provider keys must never be frontend variables. Confirm a query and browser microphone request from the production origin after deploy.
