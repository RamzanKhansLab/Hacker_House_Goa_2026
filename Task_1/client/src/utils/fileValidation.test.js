import test from "node:test";
import assert from "node:assert/strict";
import { isHeicFile, validateImageFile } from "./fileValidation.js";

test("accepts a JPG where MIME type is unavailable", () => {
  assert.deepEqual(validateImageFile({ name: "goa.jpg", type: "", size: 1024 }), { valid: true });
});

test("accepts HEIC by extension and identifies it for conversion", () => {
  const file = { name: "IMG_1234.HEIC", type: "", size: 1024 };
  assert.equal(validateImageFile(file).valid, true);
  assert.equal(isHeicFile(file), true);
});

test("rejects unsupported formats and oversized files", () => {
  assert.equal(validateImageFile({ name: "frame.gif", type: "image/gif", size: 100 }).valid, false);
  assert.equal(validateImageFile({ name: "huge.png", type: "image/png", size: 21 * 1024 * 1024 }).valid, false);
});
