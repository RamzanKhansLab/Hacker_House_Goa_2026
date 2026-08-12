import { OUTPUT_SIZE } from "../constants";
import { drawImageCover } from "./cropCalculator";
import { drawBackground, drawPfpFrame, drawPfpPhotoTreatment, pfpPhotoBounds, roundedPath } from "./frameRenderer";
import { drawIdCard, drawIdCardPhotoTreatment, idCardPhotoBounds } from "./idCardRenderer";

function drawPhoto(context, image, crop, bounds, treatment) {
  context.save();
  roundedPath(context, bounds.x, bounds.y, bounds.width, bounds.height, bounds.radius);
  context.clip();
  drawImageCover(context, image, bounds, crop);
  treatment(context, bounds);
  context.restore();
}

export function renderGraphic(canvas, { image, format, crop, builder }) {
  if (!canvas || !image) return false;

  canvas.width = OUTPUT_SIZE;
  canvas.height = OUTPUT_SIZE;
  const context = canvas.getContext("2d", { alpha: false });
  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = "high";
  drawBackground(context, OUTPUT_SIZE);

  if (format === "id-card") {
    drawPhoto(context, image, crop, idCardPhotoBounds(), drawIdCardPhotoTreatment);
    drawIdCard(context, builder);
  } else {
    drawPhoto(context, image, crop, pfpPhotoBounds(), drawPfpPhotoTreatment);
    drawPfpFrame(context);
  }

  return true;
}

export function canvasToBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("EXPORT_FAILED"));
    }, "image/png");
  });
}
