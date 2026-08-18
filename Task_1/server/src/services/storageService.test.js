import test from "node:test";
import assert from "node:assert/strict";
import { DeleteObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { createR2StorageAdapter, StorageConfigurationError, StorageOperationError } from "./storageService.js";

const config = {
  accountId: "account-id",
  accessKeyId: "access-key",
  secretAccessKey: "secret-key",
  bucketName: "hh-goa-share-images",
  publicBaseUrl: "https://images.example.com/",
  endpoint: "https://account-id.r2.cloudflarestorage.com",
};

function createClient() {
  const calls = [];
  return {
    calls,
    async send(command) {
      calls.push(command);
      return {};
    },
  };
}

test("reports each missing R2 variable clearly during initialization", async () => {
  const adapter = createR2StorageAdapter({ client: createClient(), config: { ...config, bucketName: "", publicBaseUrl: "" } });
  await assert.rejects(adapter.initialize(), (error) => {
    assert.ok(error instanceof StorageConfigurationError);
    assert.match(error.message, /R2_BUCKET_NAME/);
    assert.match(error.message, /R2_PUBLIC_BASE_URL/);
    return true;
  });
});

test("uploads a generated PNG with a unique safe key and correct content type", async () => {
  const client = createClient();
  const adapter = createR2StorageAdapter({ client, config });
  const first = await adapter.upload({ slug: "fr4m3_01", buffer: Buffer.from("png"), contentType: "image/png" });
  const second = await adapter.upload({ slug: "fr4m3_02", buffer: Buffer.from("png"), contentType: "image/png" });

  assert.deepEqual(first, { fileName: "generated/fr4m3_01.png" });
  assert.notEqual(first.fileName, second.fileName);
  assert.equal(client.calls.length, 2);
  assert.ok(client.calls[0] instanceof PutObjectCommand);
  assert.deepEqual(client.calls[0].input, {
    Bucket: "hh-goa-share-images",
    Key: "generated/fr4m3_01.png",
    Body: Buffer.from("png"),
    ContentType: "image/png",
    CacheControl: "public, max-age=86400, immutable",
  });
});

test("generates normalized public URLs and deletes stored objects", async () => {
  const client = createClient();
  const adapter = createR2StorageAdapter({ client, config });
  assert.equal(adapter.getPublicUrl("generated/fr4m3_01.png"), "https://images.example.com/generated/fr4m3_01.png");
  await adapter.delete("generated/fr4m3_01.png");
  assert.ok(client.calls[0] instanceof DeleteObjectCommand);
  assert.deepEqual(client.calls[0].input, { Bucket: "hh-goa-share-images", Key: "generated/fr4m3_01.png" });
});

test("does not accept unsafe object keys or non-image output", async () => {
  const adapter = createR2StorageAdapter({ client: createClient(), config });
  assert.throws(() => adapter.getPublicUrl("../unsafe.png"), StorageConfigurationError);
  await assert.rejects(adapter.upload({ slug: "fr4m3_03", buffer: Buffer.from("image"), contentType: "text/plain" }), StorageOperationError);
});
