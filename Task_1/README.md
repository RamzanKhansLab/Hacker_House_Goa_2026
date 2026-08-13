# HH Goa 2026 — Builder Frame Generator

A mobile-first Frame / ID Card Generator for the Hacker House Goa 2026 shortlisting task.

**Live URL:** Configure the deployment below, then add the Vercel URL here.

## Implemented product

- 1080 × 1080 PFP frame and Builder ID Card formats.
- Local JPG, JPEG, PNG, HEIC, and HEIF processing with browser-side HEIC conversion.
- Cover crop, zoom, horizontal/vertical position controls, and live Canvas preview.
- Real PNG export using `canvas.toBlob()`.
- Native file sharing where supported, plus an editable X fallback containing `#FrameInGoa`.
- Per-share Open Graph and X metadata for the generated image.
- Payload validation, PNG signature verification, rate limits, and temporary share metadata.

The original uploaded photo stays in the browser. Only the final generated PNG is sent to the API when a user needs the X share-link fallback.

## Production architecture

```text
Vercel (React/Vite)
       │ VITE_API_BASE_URL
       ▼
Render Free Web Service (Express)
       ├── MongoDB Atlas: temporary /share/:slug metadata + TTL index
       └── Cloudflare R2: temporary generated PNGs + public custom image domain
```

Render runs the API only; it does **not** store generated images. The R2 adapter keeps the existing `storageService` contract (`initialize`, `upload`, `delete`, `getPublicUrl`, `cleanupExpiredFiles`) so controllers do not use the AWS SDK directly.

## Project structure

```text
Task_1/
├── client/                   # React, Vite, Tailwind and Canvas renderer
├── server/                   # Express API, MongoDB model and R2 storage adapter
├── render.yaml               # Render Free API Blueprint (no persistent disk)
├── vercel.json               # Vercel static-site build configuration
├── .env.example              # Safe combined local-development example
└── .nvmrc                    # Node 22.14.0
```

## Local development

Requirements: Node.js 22.14+ and npm.

```powershell
cd Task_1
npm ci
Copy-Item .env.example .env
Copy-Item client/.env.example client/.env
npm run dev
```

The root `Task_1/.env` is read by the API. Create it from `.env.example` for offline/local work; that template sets `STORAGE_PROVIDER=local` explicitly and stores temporary share PNGs under `server/generated/`. This provider is blocked when `NODE_ENV=production`.

For an R2-backed local API instead, change only these values in your uncommitted `.env`:

```env
STORAGE_PROVIDER=r2
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=hh-goa-share-images
R2_PUBLIC_BASE_URL=https://images.your-domain.com
# Optional; derived from R2_ACCOUNT_ID if omitted
R2_ENDPOINT=https://your_cloudflare_account_id.r2.cloudflarestorage.com
```

## Environment variables

| Variable | Runtime | Required | Purpose |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | Vercel/client | Yes in split deployment | Public Render API URL, no trailing slash. |
| `NODE_ENV` | Render/server | Yes | Set to `production`. |
| `CLIENT_URL` | Render/server | Yes | Public Vercel frontend URL. Supports comma-separated origins. |
| `PUBLIC_SERVER_URL` | Render/server | Yes | Public Render API URL; used to build `/share/:slug` links. |
| `MONGODB_URI` | Render/server | Yes | Atlas connection string for expiring share metadata. |
| `SHARE_TTL_HOURS` | Render/server | Yes | Share expiry from 1–168 hours; default `24`. |
| `STORAGE_PROVIDER` | Render/server | Yes | Must be `r2` in production. `local` is development-only. |
| `R2_ACCOUNT_ID` | Render/server | Yes | Cloudflare Account ID. |
| `R2_ACCESS_KEY_ID` | Render/server | Yes | Scoped R2 S3 API token access key. |
| `R2_SECRET_ACCESS_KEY` | Render/server | Yes | Scoped R2 S3 API token secret. |
| `R2_BUCKET_NAME` | Render/server | Yes | R2 bucket that holds generated share PNGs. |
| `R2_PUBLIC_BASE_URL` | Render/server | Yes | HTTPS public custom bucket domain, no trailing slash. |
| `R2_ENDPOINT` | Render/server | Optional | Defaults to `https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com`. |

Never commit `.env` files, MongoDB connection strings, R2 access keys, or R2 secrets. Values beginning with `VITE_` are exposed to browser builds—do not use that prefix for server credentials.

## Cloudflare R2 setup

1. Sign in to Cloudflare and select the correct account.
2. Open **R2 Object Storage → Create bucket**.
3. Name it `hh-goa-share-images` and create it.
4. Open the bucket → **Settings → Custom Domains → Add**.
5. Attach a domain such as `images.your-domain.com`, then wait until it becomes **Active**. The domain must belong to a Cloudflare zone in the same account.
6. Use `https://images.your-domain.com` as `R2_PUBLIC_BASE_URL`. Do not use the S3 API endpoint as the public image URL.
7. In **R2 → Manage API Tokens**, create an **Account API Token**:
   - Permissions: **Object Read & Write**.
   - Scope: only the `hh-goa-share-images` bucket.
   - Copy the Access Key ID and Secret Access Key immediately; the secret is displayed only once.
8. Copy the Cloudflare Account ID from the dashboard and set `R2_ACCOUNT_ID`.
9. In the bucket, configure an object lifecycle rule to delete objects with the `generated/` prefix after **2 days**. The app removes known expired images hourly; the lifecycle rule safely cleans up any orphaned object.

The bucket must allow public **read** access through the custom domain so X/Open Graph crawlers can fetch each generated image. Do not expose R2 API credentials or enable public write access.

## Deploy the API on Render Free

The included [`render.yaml`](./render.yaml) targets the Render Free tier and intentionally has no disk configuration.

1. Push `Task_1` to GitHub.
2. In Render, select **New → Blueprint** and connect this repository.
3. Set the Blueprint file path to `Task_1/render.yaml`.
4. Apply the Blueprint. It creates `hh-goa-frame-api` in Singapore with:

   ```text
   Root directory: Task_1
   Build command: npm ci
   Start command: npm run start --workspace=@hh-goa/frame-server
   Health check: /health
   Plan: Free
   ```

5. In the Render service **Environment** page, fill every `sync: false` variable from the table above:

   ```env
   CLIENT_URL=https://your-vercel-project.vercel.app
   PUBLIC_SERVER_URL=https://hh-goa-frame-api.onrender.com
   MONGODB_URI=mongodb+srv://...
   R2_ACCOUNT_ID=...
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_BUCKET_NAME=hh-goa-share-images
   R2_PUBLIC_BASE_URL=https://images.your-domain.com
   # Leave R2_ENDPOINT empty to use the derived R2 endpoint, or set it explicitly.
   ```

   `NODE_ENV=production`, `STORAGE_PROVIDER=r2`, `SHARE_TTL_HOURS=24`, and `NODE_VERSION=22.14.0` are already non-secret defaults in the Blueprint.

6. Deploy and open:

   ```text
   https://hh-goa-frame-api.onrender.com/health
   ```

   Expected response:

   ```json
   {"status":"ok","storage":"r2"}
   ```

7. Render Free services can spin down during inactivity. The first request after idle can be slow; it does not affect the browser-local frame generation, only the optional X share-link fallback.

## Deploy the frontend on Vercel

1. In Vercel, select **Add New → Project** and import the same repository.
2. Set **Root Directory** to `Task_1`.
3. Vercel reads [`vercel.json`](./vercel.json), which configures:

   ```text
   Install command: npm ci
   Build command: npm run build
   Output directory: client/dist
   ```

4. Set this production environment variable before the first build:

   ```env
   VITE_API_BASE_URL=https://hh-goa-frame-api.onrender.com
   ```

5. Deploy. Copy the Vercel URL.
6. Return to Render and set `CLIENT_URL` to that exact Vercel URL, then redeploy the API.
7. If the Render API URL changes, update `VITE_API_BASE_URL` in Vercel and redeploy the frontend.

## MongoDB Atlas setup

1. Create an Atlas project and a free/shared cluster.
2. Create a database user limited to the `hh_goa` database with `readWrite` access.
3. In **Network Access**, permit the Render service. For a simple hackathon deployment without a fixed outbound IP, use `0.0.0.0/0` only with a long, unique database password and least-privilege user.
4. Copy the `mongodb+srv://` connection string, include the `hh_goa` database name, and set it as `MONGODB_URI` in Render.
5. Confirm the Render log says `MongoDB connected for temporary share metadata.`

## Verification commands

```powershell
cd Task_1
npm ci
npm test
npm run build
```

Before submission, test the deployed Vercel URL with JPG, PNG, and a real iPhone HEIC image. Then test the Share to X fallback, open the returned `/share/:slug` URL in an incognito window, and confirm its page source contains `og:image`, `og:title`, and `og:description` pointing to the R2 custom domain.

## Known limitations

- A real iPhone HEIC upload must still be verified on a physical iOS device after deployment.
- Direct X posting is controlled by browser/X platform policies. Native file sharing is used where supported; otherwise the product opens an editable X intent with an expiring OG link.
- Render Free can cold-start after inactivity. The primary generator remains fast because all composition happens in the browser.
