export function clamp(value, min, max) {
  return Math.min(Math.max(Number(value) || 0, min), max);
}

/**
 * Computes object-fit: cover placement while allowing a user to select the
 * visible part of any non-square input. Position values range from -1 to 1.
 */
export function getCoverPlacement({ imageWidth, imageHeight, target, zoom = 1, position = {} }) {
  if (!imageWidth || !imageHeight || !target?.width || !target?.height) {
    return null;
  }

  const safeZoom = clamp(zoom, 1, 3);
  const scale = Math.max(target.width / imageWidth, target.height / imageHeight) * safeZoom;
  const width = imageWidth * scale;
  const height = imageHeight * scale;
  const overflowX = Math.max(0, width - target.width);
  const overflowY = Math.max(0, height - target.height);
  const positionX = (clamp(position.x, -1, 1) + 1) / 2;
  const positionY = (clamp(position.y, -1, 1) + 1) / 2;

  return {
    x: target.x - overflowX * positionX,
    y: target.y - overflowY * positionY,
    width,
    height,
    scale,
  };
}

export function drawImageCover(context, image, target, crop) {
  const placement = getCoverPlacement({
    imageWidth: image.naturalWidth || image.width,
    imageHeight: image.naturalHeight || image.height,
    target,
    zoom: crop.zoom,
    position: crop.position,
  });

  if (placement) {
    context.drawImage(image, placement.x, placement.y, placement.width, placement.height);
  }
  return placement;
}
