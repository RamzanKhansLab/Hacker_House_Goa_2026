import { randomBytes } from "node:crypto";
import mongoose from "mongoose";
import { env } from "../config/env.js";
import { Share } from "../models/Share.js";
import { storageService } from "./storageService.js";

const memoryShares = new Map();

function usingMongo() {
  return mongoose.connection.readyState === 1;
}

function expiryDate() {
  return new Date(Date.now() + env.shareTtlHours * 60 * 60 * 1000);
}

async function createUniqueSlug() {
  for (let attempts = 0; attempts < 5; attempts += 1) {
    const slug = randomBytes(6).toString("base64url").toLowerCase();
    const exists = usingMongo() ? await Share.exists({ slug }) : memoryShares.has(slug);
    if (!exists) return slug;
  }
  throw new Error("Could not create a unique share link.");
}

async function removeRecord(record) {
  await storageService.delete(record.imageFileName);
  if (usingMongo()) await Share.deleteOne({ slug: record.slug });
  else memoryShares.delete(record.slug);
}

export const shareService = {
  async create({ imageBuffer, format }) {
    const slug = await createUniqueSlug();
    const expiresAt = expiryDate();
    const storage = await storageService.upload({ slug, buffer: imageBuffer });
    const record = { slug, imageFileName: storage.fileName, format, createdAt: new Date(), expiresAt };

    try {
      if (usingMongo()) await Share.create(record);
      else memoryShares.set(slug, record);
      return record;
    } catch (error) {
      await storageService.delete(storage.fileName);
      throw error;
    }
  },

  async get(slug) {
    let record;
    if (usingMongo()) record = await Share.findOne({ slug }).lean();
    else record = memoryShares.get(slug);
    if (!record) return null;
    if (new Date(record.expiresAt).getTime() <= Date.now()) {
      await removeRecord(record);
      return null;
    }
    return record;
  },

  async cleanupExpired() {
    const now = new Date();
    let removedMetadata = 0;
    if (usingMongo()) {
      const expired = await Share.find({ expiresAt: { $lte: now } }).lean();
      await Promise.all(expired.map((record) => removeRecord(record)));
      removedMetadata = expired.length;
    } else {
      const expired = [...memoryShares.values()].filter((record) => new Date(record.expiresAt) <= now);
      await Promise.all(expired.map((record) => removeRecord(record)));
      removedMetadata = expired.length;
    }
    const removedFiles = await storageService.cleanupExpiredFiles();
    return removedMetadata + removedFiles;
  },
};
