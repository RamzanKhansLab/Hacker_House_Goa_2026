import test from "node:test";
import assert from "node:assert/strict";
import { getCoverPlacement } from "./cropCalculator.js";

const target = { x: 0, y: 0, width: 1080, height: 800 };

test("cover placement preserves a portrait image without stretching", () => {
  const placement = getCoverPlacement({
    imageWidth: 800,
    imageHeight: 1600,
    target,
    zoom: 1,
    position: { x: 0, y: 0 },
  });
  assert.equal(placement.width, 1080);
  assert.equal(placement.height, 2160);
  assert.equal(placement.y, -680);
});

test("position moves the visible landscape crop across the target", () => {
  const left = getCoverPlacement({ imageWidth: 2000, imageHeight: 800, target, position: { x: -1, y: 0 } });
  const right = getCoverPlacement({ imageWidth: 2000, imageHeight: 800, target, position: { x: 1, y: 0 } });
  assert.equal(left.x, 0);
  assert.equal(right.x, -920);
});

test("zoom is clamped to the supported editing range", () => {
  const placement = getCoverPlacement({ imageWidth: 1080, imageHeight: 800, target, zoom: 7, position: {} });
  assert.equal(placement.width, 3240);
});
