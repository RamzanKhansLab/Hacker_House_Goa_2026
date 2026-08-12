import "dotenv/config";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const serverRoot = path.resolve(here, "../..");

export const env = {
  nodeEnv: process.env.NODE_ENV || "development",
  port: Number(process.env.PORT || 8787),
  clientUrls: (process.env.CLIENT_URL || "http://localhost:5173").split(",").map((value) => value.trim()).filter(Boolean),
  mongoUri: process.env.MONGODB_URI || "",
  publicServerUrl: (process.env.PUBLIC_SERVER_URL || "").replace(/\/$/, ""),
  shareTtlHours: Math.min(Math.max(Number(process.env.SHARE_TTL_HOURS || 24), 1), 168),
  storageDirectory: path.resolve(serverRoot, process.env.SHARE_STORAGE_DIRECTORY || "generated"),
};

export const hasMongoConfiguration = Boolean(env.mongoUri);
