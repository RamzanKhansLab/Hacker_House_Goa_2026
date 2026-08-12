import { mkdir, readdir, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { env } from "../config/env.js";

function safeFileName(value) {
  if (!/^[a-zA-Z0-9_-]+\.png$/.test(value)) throw new Error("Invalid storage file name");
  return value;
}

/**
 * Local storage adapter. Its small interface makes switching to S3, R2, or
 * another object store a contained replacement instead of a controller change.
 */
export const storageService = {
  async initialize() {
    await mkdir(env.storageDirectory, { recursive: true });
  },

  async upload({ slug, buffer }) {
    const fileName = safeFileName(`${slug}.png`);
    await this.initialize();
    await writeFile(path.join(env.storageDirectory, fileName), buffer, { flag: "wx" });
    return { fileName };
  },

  async delete(fileName) {
    try {
      await unlink(path.join(env.storageDirectory, safeFileName(fileName)));
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
    }
  },

  getPublicUrl(fileName, baseUrl) {
    return `${baseUrl}/generated/${encodeURIComponent(safeFileName(fileName))}`;
  },

  // MongoDB's TTL monitor removes metadata independently, so local generated
  // files are also cleaned by their own age. A cloud adapter should map this to
  // an object-store lifecycle policy or equivalent scheduled cleanup.
  async cleanupExpiredFiles() {
    await this.initialize();
    const oldestPermittedTime = Date.now() - env.shareTtlHours * 60 * 60 * 1000;
    const entries = await readdir(env.storageDirectory);
    let removed = 0;
    await Promise.all(entries.map(async (fileName) => {
      if (!/^[a-zA-Z0-9_-]+\.png$/.test(fileName)) return;
      const filePath = path.join(env.storageDirectory, fileName);
      const details = await stat(filePath);
      if (details.mtimeMs <= oldestPermittedTime) {
        await this.delete(fileName);
        removed += 1;
      }
    }));
    return removed;
  },
};
