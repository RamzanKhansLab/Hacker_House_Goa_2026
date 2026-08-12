import test from "node:test";
import assert from "node:assert/strict";
import { validateSharePayload } from "./validateSharePayload.js";

const pngPrefix = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]).toString("base64");

test("accepts a verified generated PNG payload", () => {
  const result = validateSharePayload({ imageDataUrl: `data:image/png;base64,${pngPrefix}`, format: "pfp" });
  assert.equal(result.valid, true);
  assert.equal(result.buffer.length, 8);
});

test("rejects a non-PNG or unsupported format", () => {
  assert.equal(validateSharePayload({ imageDataUrl: "data:image/jpeg;base64,ZmFrZQ==", format: "pfp" }).valid, false);
  assert.equal(validateSharePayload({ imageDataUrl: `data:image/png;base64,${pngPrefix}`, format: "avatar" }).valid, false);
});
