export function setTracking(context, value) {
  context.letterSpacing = `${value}px`;
}

export function drawText(context, text, x, y, options = {}) {
  const {
    font = "600 24px Arial, sans-serif",
    color = "#ffffff",
    align = "left",
    baseline = "alphabetic",
    tracking = 0,
    maxWidth,
  } = options;
  context.save();
  context.font = font;
  context.fillStyle = color;
  context.textAlign = align;
  context.textBaseline = baseline;
  setTracking(context, tracking);
  context.fillText(String(text || ""), x, y, maxWidth);
  context.restore();
}

export function fitText(context, text, maxWidth, options = {}) {
  const { minSize = 20, maxSize = 56, weight = 700, family = "Arial, sans-serif" } = options;
  context.save();
  for (let size = maxSize; size >= minSize; size -= 1) {
    context.font = `${weight} ${size}px ${family}`;
    if (context.measureText(text).width <= maxWidth) {
      context.restore();
      return size;
    }
  }
  context.restore();
  return minSize;
}
