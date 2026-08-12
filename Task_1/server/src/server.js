import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import mongoose from "mongoose";
import path from "node:path";
import { env, hasMongoConfiguration } from "./config/env.js";
import { errorHandler, notFoundHandler } from "./middleware/errorHandler.js";
import { shareRouter } from "./routes/shareRoutes.js";
import { shareService } from "./services/shareService.js";
import { storageService } from "./services/storageService.js";

const app = express();
app.set("trust proxy", 1);
app.use(helmet({ contentSecurityPolicy: false, crossOriginResourcePolicy: { policy: "cross-origin" } }));
app.use(cors({ origin: env.clientUrls, methods: ["GET", "POST"] }));
app.use(express.json({ limit: "6mb", type: "application/json" }));
app.use("/generated", express.static(env.storageDirectory, { maxAge: "1h", fallthrough: false }));

const shareLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 12,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  message: { message: "Too many share requests. Please try again in a few minutes." },
});
app.use("/api/share", shareLimiter);
app.get("/health", (request, response) => response.json({ status: "ok", storage: "local-temporary" }));
app.use(shareRouter);
app.use(notFoundHandler);
app.use(errorHandler);

async function connectDatabase() {
  if (!hasMongoConfiguration) {
    console.info("MONGODB_URI is not set; share metadata will be temporary in-memory data.");
    return;
  }
  try {
    await mongoose.connect(env.mongoUri, { serverSelectionTimeoutMS: 5000 });
    console.info("MongoDB connected for temporary share metadata.");
  } catch (error) {
    console.error("MongoDB unavailable; share metadata will be temporary in-memory data.", error.message);
  }
}

async function start() {
  await storageService.initialize();
  await connectDatabase();
  await shareService.cleanupExpired();
  const cleanupTimer = setInterval(() => {
    shareService.cleanupExpired().catch((error) => console.error("Share cleanup failed", error));
  }, 60 * 60 * 1000);
  cleanupTimer.unref();

  app.listen(env.port, () => {
    console.info(`HH Goa share service listening on http://localhost:${env.port}`);
  });
}

start().catch((error) => {
  console.error("Server startup failed", error);
  process.exitCode = 1;
});
