# HH Goa 2026 — Builder Frame Generator

A focused, mobile-first Frame / ID Card Generator for the Hacker House Goa 2026 shortlisting task.

**Live URL:** Not deployed from this workspace yet. The project is deployment-ready once the frontend and share API URLs are configured.

## What is implemented

- Format A: a polished 1080 × 1080 PFP frame, composed around the uploaded photo.
- Format B: a builder ID card with name, role, stack, and local builder-title selection.
- Local JPG, JPEG, PNG, HEIC, and HEIF processing. HEIC/HEIF conversion is performed in the browser with `heic2any`.
- Cover-style crop rendering with zoom, horizontal, vertical, and reset controls.
- Real PNG download using `canvas.toBlob()`.
- Native file sharing where the browser supports it, with the required `#FrameInGoa` caption.
- X fallback that uploads only the generated PNG, creates an expiring share URL, and opens an editable X intent.
- A share page with per-image Open Graph and Twitter image metadata.
- Express payload validation, PNG signature verification, 15-minute request rate limits, temporary storage, MongoDB TTL metadata, and a no-Mongo local-development fallback.

The normal upload-to-render path never sends the original photo to the server.

## Architecture

```text
Photo (browser)
  → HEIC conversion when needed
  → crop calculator + Canvas renderer
  → 1080px PNG preview/download
  └→ optional share fallback → Express API → temporary PNG + metadata → /share/:slug
```

`client/` is a React + Vite + Tailwind CSS application. Rendering is deliberately independent of React in `client/src/renderer/`.

`server/` is an Express service. Its `storageService` is a local temporary-storage adapter with `upload`, `delete`, and `getPublicUrl` operations; it can be replaced with an R2/S3 adapter without changing the API/controller layer. MongoDB is used for share metadata when `MONGODB_URI` is configured; the `expiresAt` TTL index removes records automatically, while the local adapter cleans matching expired image files by age.

## Project structure

```text
Task_1/
├── client/                 # React, Vite, Tailwind, Canvas composition
│   └── src/
│       ├── components/     # Upload, editor, preview, fields
│       ├── hooks/          # image upload, renderer, share state
│       ├── renderer/       # crop, frame, ID-card, canvas modules
│       └── services/       # share API client
├── server/                 # Express temporary-share service
│   └── src/
│       ├── controllers/
│       ├── models/
│       ├── services/
│       └── utils/
├── .env.example
└── package.json
```

## Run locally

Requirements: Node.js 20.19+ (Node 22 is also supported) and npm.

```bash
cd Task_1
npm install
copy client\.env.example client\.env
copy server\.env.example server\.env
npm run dev
```

The client runs at `http://localhost:5173` and the API at `http://localhost:8787`.

For PowerShell, use `Copy-Item client/.env.example client/.env` and the matching server command. A MongoDB connection is optional in development: without it, temporary share records remain in memory until the API restarts or the expiry window elapses.

## Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | client | Public share API base URL; use the deployed Express URL for split hosting. |
| `PORT` | server | Express port. |
| `CLIENT_URL` | server | Comma-separated origins allowed to call the share API. |
| `PUBLIC_SERVER_URL` | server | Public HTTPS base URL used in returned share and OG image URLs. |
| `MONGODB_URI` | server | Managed MongoDB connection for share metadata and the TTL index. |
| `SHARE_TTL_HOURS` | server | Retention window for generated share images, from 1 to 168 hours. |
| `SHARE_STORAGE_DIRECTORY` | server | Temporary local storage directory; replace the adapter for object storage in production. |

Never commit `.env` files or provider credentials.

## Commands

```bash
npm run dev      # client and API together
npm run build    # production Vite build
npm test         # crop/file validation and share-payload tests
npm run start    # run the Express share API
```

## Deployment

Deploy `client/` to a static host and `server/` to a Node host, then set:

1. `VITE_API_BASE_URL` to the public Express URL before building the client.
2. `CLIENT_URL` on the API to the public client URL.
3. `PUBLIC_SERVER_URL` on the API to its own public HTTPS URL.
4. `MONGODB_URI` to a managed MongoDB instance.
5. Replace `server/src/services/storageService.js` with an R2/S3 implementation for durable, cross-instance temporary assets. Keep the same three-method interface.

The static client needs no photo-upload backend. Only a user choosing the desktop/X link fallback uploads the final generated PNG.

## Verification scope

Automated tests cover the crop placement algorithm, client file validation, and server-side share payload verification. Build and server smoke-test results are recorded in the implementation handoff after dependencies are installed.

## Known limitations

- Browser HEIC decoding is implemented client-side, but real-device verification still matters because iOS/browser codec support varies.
- Direct X image posting is controlled by X and browser platform policy. The application uses native file sharing where available; otherwise it uses an expiring OG share link and editable X intent.
- The included local storage adapter is suitable for local development and a single ephemeral API instance. A production multi-instance deployment should use the documented object-storage adapter replacement.
