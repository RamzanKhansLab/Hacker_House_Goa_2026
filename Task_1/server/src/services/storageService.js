import { DeleteObjectCommand, PutObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { mkdir, readdir, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { env } from "../config/env.js";

const SUPPORTED_IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);
const OBJECT_KEY_PATTERN = /^generated\/[a-zA-Z0-9_-]{6,64}\.png$/;

export class StorageConfigurationError extends Error {
  constructor(message) {
    super(message);
    this.name = "StorageConfigurationError";
    this.code = "STORAGE_CONFIGURATION";
  }
}

export class StorageOperationError extends Error {
  constructor(message, cause) {
    super(message, { cause });
    this.name = "StorageOperationError";
    this.code = "STORAGE_OPERATION";
  }
}

function objectKeyForSlug(slug) {
  const key = `generated/${String(slug || "")}.png`;
  if (!OBJECT_KEY_PATTERN.test(key)) {
    throw new StorageConfigurationError("The generated share identifier is invalid.");
  }
  return key;
}

function assertObjectKey(value) {
  if (!OBJECT_KEY_PATTERN.test(String(value || ""))) {
    throw new StorageConfigurationError("The stored share image key is invalid.");
  }
  return value;
}

function encodeObjectKey(key) {
  return key.split("/").map(encodeURIComponent).join("/");
}

function assertImageBuffer(buffer, contentType) {
  if (!Buffer.isBuffer(buffer) || buffer.length === 0) {
    throw new StorageOperationError("The generated image buffer is invalid.");
  }
  if (!SUPPORTED_IMAGE_TYPES.has(contentType)) {
    throw new StorageOperationError("The generated image type is not supported by storage.");
  }
}

function missingR2Variables(config) {
  const expected = {
    R2_ACCOUNT_ID: config.accountId,
    R2_ACCESS_KEY_ID: config.accessKeyId,
    R2_SECRET_ACCESS_KEY: config.secretAccessKey,
    R2_BUCKET_NAME: config.bucketName,
    R2_PUBLIC_BASE_URL: config.publicBaseUrl,
  };
  return Object.entries(expected).filter(([, value]) => !value).map(([key]) => key);
}

function validateR2Configuration(config) {
  const missing = missingR2Variables(config);
  if (missing.length) {
    throw new StorageConfigurationError(`Cloudflare R2 configuration is incomplete. Missing: ${missing.join(", ")}.`);
  }
  if (!/^https:\/\//.test(config.endpoint)) {
    throw new StorageConfigurationError("R2_ENDPOINT must be an HTTPS URL.");
  }
  if (!/^https:\/\//.test(config.publicBaseUrl)) {
    throw new StorageConfigurationError("R2_PUBLIC_BASE_URL must be an HTTPS URL.");
  }
}

/**
 * Cloudflare R2 is accessed through its S3-compatible API. Controllers and
 * share business logic retain the same storage-service interface as before.
 */
export function createR2StorageAdapter({ client, config }) {
  return {
    async initialize() {
      validateR2Configuration(config);
    },

    async upload({ slug, buffer, contentType = "image/png" }) {
      validateR2Configuration(config);
      assertImageBuffer(buffer, contentType);
      const fileName = objectKeyForSlug(slug);
      try {
        await client.send(new PutObjectCommand({
          Bucket: config.bucketName,
          Key: fileName,
          Body: buffer,
          ContentType: contentType,
          CacheControl: "public, max-age=86400, immutable",
        }));
        return { fileName };
      } catch (error) {
        throw new StorageOperationError("Cloudflare R2 could not store the generated share image.", error);
      }
    },

    async delete(fileName) {
      validateR2Configuration(config);
      try {
        await client.send(new DeleteObjectCommand({ Bucket: config.bucketName, Key: assertObjectKey(fileName) }));
      } catch (error) {
        throw new StorageOperationError("Cloudflare R2 could not delete the expired share image.", error);
      }
    },

    getPublicUrl(fileName) {
      validateR2Configuration(config);
      return `${config.publicBaseUrl.replace(/\/+$/, "")}/${encodeObjectKey(assertObjectKey(fileName))}`;
    },

    async cleanupExpiredFiles() {
      // The existing share cleanup timer deletes R2 objects through delete().
      // Configure an R2 lifecycle rule as a second safety net for any orphan.
      return 0;
    },
  };
}

function localFileName(objectKey) {
  return path.basename(assertObjectKey(objectKey));
}

function createLocalStorageAdapter() {
  return {
    async initialize() {
      if (env.nodeEnv === "production") {
        throw new StorageConfigurationError("STORAGE_PROVIDER=local is not allowed in production. Configure Cloudflare R2 with STORAGE_PROVIDER=r2.");
      }
      await mkdir(env.storageDirectory, { recursive: true });
    },

    async upload({ slug, buffer, contentType = "image/png" }) {
      assertImageBuffer(buffer, contentType);
      await this.initialize();
      const fileName = objectKeyForSlug(slug);
      await writeFile(path.join(env.storageDirectory, localFileName(fileName)), buffer, { flag: "wx" });
      return { fileName };
    },

    async delete(fileName) {
      try {
        await unlink(path.join(env.storageDirectory, localFileName(fileName)));
      } catch (error) {
        if (error?.code !== "ENOENT") throw new StorageOperationError("Local development storage could not delete the share image.", error);
      }
    },

    getPublicUrl(fileName, baseUrl) {
      if (!baseUrl) throw new StorageConfigurationError("A public server URL is required for local development storage.");
      return `${baseUrl.replace(/\/$/, "")}/generated/${encodeURIComponent(localFileName(fileName))}`;
    },

    async cleanupExpiredFiles() {
      await this.initialize();
      const oldestPermittedTime = Date.now() - env.shareTtlHours * 60 * 60 * 1000;
      const entries = await readdir(env.storageDirectory);
      let removed = 0;
      await Promise.all(entries.map(async (fileName) => {
        if (!/^[a-zA-Z0-9_-]{6,64}\.png$/.test(fileName)) return;
        const filePath = path.join(env.storageDirectory, fileName);
        const details = await stat(filePath);
        if (details.mtimeMs <= oldestPermittedTime) {
          await this.delete(`generated/${fileName}`);
          removed += 1;
        }
      }));
      return removed;
    },
  };
}

let r2Adapter;

function getR2Adapter() {
  if (!r2Adapter) {
    const client = new S3Client({
      region: "auto",
      endpoint: env.r2.endpoint,
      credentials: {
        accessKeyId: env.r2.accessKeyId,
        secretAccessKey: env.r2.secretAccessKey,
      },
    });
    r2Adapter = createR2StorageAdapter({ client, config: env.r2 });
  }
  return r2Adapter;
}

const localAdapter = createLocalStorageAdapter();
function activeAdapter() {
  return env.storageProvider === "r2" ? getR2Adapter() : localAdapter;
}

export const storageService = {
  initialize: () => activeAdapter().initialize(),
  upload: (input) => activeAdapter().upload(input),
  delete: (fileName) => activeAdapter().delete(fileName),
  getPublicUrl: (fileName, baseUrl) => activeAdapter().getPublicUrl(fileName, baseUrl),
  cleanupExpiredFiles: () => activeAdapter().cleanupExpiredFiles(),
};
