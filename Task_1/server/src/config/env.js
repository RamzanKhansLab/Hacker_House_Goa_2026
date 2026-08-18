import dotenv from "dotenv";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const serverRoot = path.resolve(here, "../..");
const projectRoot = path.resolve(serverRoot, "..");

// A root Task_1/.env is convenient for this workspace. A server/.env can be
// used to override it when running the API independently.
dotenv.config({ path: path.join(projectRoot, ".env") });
dotenv.config({ path: path.join(serverRoot, ".env"), override: true });

function storageProvider() {
  const provider = (process.env.STORAGE_PROVIDER || "r2").trim().toLowerCase();
  if (!["r2", "local"].includes(provider)) {
    throw new Error("STORAGE_PROVIDER must be either 'r2' or 'local'.");
  }
  return provider;
}

const nodeEnv = process.env.NODE_ENV || "development";
const r2AccountId = (process.env.R2_ACCOUNT_ID || "").trim();

export const env = {
  nodeEnv,
  port: Number(process.env.PORT || 8787),
  clientUrls: (process.env.CLIENT_URL || "http://localhost:5173").split(",").map((value) => value.trim()).filter(Boolean),
  mongoUri: process.env.MONGODB_URI || "",
  publicServerUrl: (process.env.PUBLIC_SERVER_URL || "").replace(/\/$/, ""),
  shareTtlHours: Math.min(Math.max(Number(process.env.SHARE_TTL_HOURS || 24), 1), 168),
  storageProvider: storageProvider(),
  storageDirectory: path.resolve(serverRoot, process.env.SHARE_STORAGE_DIRECTORY || "generated"),
  r2: {
    accountId: r2AccountId,
    accessKeyId: (process.env.R2_ACCESS_KEY_ID || "").trim(),
    secretAccessKey: (process.env.R2_SECRET_ACCESS_KEY || "").trim(),
    bucketName: (process.env.R2_BUCKET_NAME || "").trim(),
    publicBaseUrl: (process.env.R2_PUBLIC_BASE_URL || "").trim().replace(/\/$/, ""),
    endpoint: (process.env.R2_ENDPOINT || `https://${r2AccountId}.r2.cloudflarestorage.com`).trim().replace(/\/$/, ""),
  },
};

export const hasMongoConfiguration = Boolean(env.mongoUri);
