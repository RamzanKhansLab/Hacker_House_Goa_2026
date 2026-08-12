import { drawText } from "./textRenderer";

export function roundedPath(context, x, y, width, height, radius) {
  const safeRadius = Math.min(radius, width / 2, height / 2);
  context.beginPath();
  context.moveTo(x + safeRadius, y);
  context.arcTo(x + width, y, x + width, y + height, safeRadius);
  context.arcTo(x + width, y + height, x, y + height, safeRadius);
  context.arcTo(x, y + height, x, y, safeRadius);
  context.arcTo(x, y, x + width, y, safeRadius);
  context.closePath();
}

export function pfpPhotoBounds() {
  return { x: 56, y: 96, width: 968, height: 842, radius: 34 };
}

export function drawBackground(context, size) {
  context.fillStyle = "#061a19";
  context.fillRect(0, 0, size, size);

  const aquaGlow = context.createRadialGradient(size * 0.14, size * 0.06, 8, size * 0.14, size * 0.06, size * 0.7);
  aquaGlow.addColorStop(0, "rgba(71, 255, 205, 0.31)");
  aquaGlow.addColorStop(0.48, "rgba(14, 137, 119, 0.16)");
  aquaGlow.addColorStop(1, "rgba(6, 26, 25, 0)");
  context.fillStyle = aquaGlow;
  context.fillRect(0, 0, size, size);

  const coralGlow = context.createRadialGradient(size * 0.89, size * 0.91, 0, size * 0.89, size * 0.91, size * 0.55);
  coralGlow.addColorStop(0, "rgba(255, 126, 91, 0.24)");
  coralGlow.addColorStop(0.6, "rgba(194, 70, 85, 0.08)");
  coralGlow.addColorStop(1, "rgba(6, 26, 25, 0)");
  context.fillStyle = coralGlow;
  context.fillRect(0, 0, size, size);

  context.save();
  context.strokeStyle = "rgba(194, 255, 232, 0.09)";
  context.lineWidth = 1;
  for (let point = 20; point < size; point += 36) {
    context.beginPath();
    context.moveTo(point, 0);
    context.lineTo(point, size);
    context.stroke();
    context.beginPath();
    context.moveTo(0, point);
    context.lineTo(size, point);
    context.stroke();
  }
  context.restore();
}

function drawCorner(context, x, y, directionX, directionY) {
  context.save();
  context.strokeStyle = "#b8ffe1";
  context.lineWidth = 7;
  context.lineCap = "square";
  context.beginPath();
  context.moveTo(x + directionX * 66, y);
  context.lineTo(x, y);
  context.lineTo(x, y + directionY * 66);
  context.stroke();
  context.strokeStyle = "#ff8f71";
  context.lineWidth = 3;
  context.beginPath();
  context.moveTo(x + directionX * 92, y + directionY * 16);
  context.lineTo(x + directionX * 42, y + directionY * 16);
  context.stroke();
  context.restore();
}

function drawSignalMark(context, x, y) {
  context.save();
  context.translate(x, y);
  context.strokeStyle = "rgba(190, 255, 226, 0.82)";
  context.lineWidth = 4;
  for (let index = 0; index < 3; index += 1) {
    const radius = 15 + index * 14;
    context.beginPath();
    context.arc(0, 0, radius, -Math.PI * 0.78, Math.PI * 0.12);
    context.stroke();
  }
  context.fillStyle = "#ff8f71";
  context.beginPath();
  context.arc(0, 0, 5, 0, Math.PI * 2);
  context.fill();
  context.restore();
}

export function drawPfpPhotoTreatment(context, bounds) {
  const shade = context.createLinearGradient(0, bounds.y + bounds.height * 0.45, 0, bounds.y + bounds.height);
  shade.addColorStop(0, "rgba(2, 16, 15, 0)");
  shade.addColorStop(0.72, "rgba(2, 16, 15, 0.12)");
  shade.addColorStop(1, "rgba(2, 16, 15, 0.84)");
  context.fillStyle = shade;
  roundedPath(context, bounds.x, bounds.y, bounds.width, bounds.height, bounds.radius);
  context.fill();
}

export function drawPfpFrame(context) {
  const bounds = pfpPhotoBounds();
  context.save();
  context.strokeStyle = "rgba(185, 255, 225, 0.78)";
  context.lineWidth = 2;
  roundedPath(context, bounds.x, bounds.y, bounds.width, bounds.height, bounds.radius);
  context.stroke();
  context.restore();

  drawCorner(context, 42, 82, 1, 1);
  drawCorner(context, 1038, 82, -1, 1);
  drawCorner(context, 42, 994, 1, -1);
  drawCorner(context, 1038, 994, -1, -1);

  drawText(context, "HACKER // HOUSE", 78, 60, {
    font: "700 23px Arial, sans-serif",
    color: "#c5ffe5",
    tracking: 2.2,
  });
  drawText(context, "GOA • 2026", 1000, 60, {
    font: "700 23px Arial, sans-serif",
    color: "#ffad95",
    tracking: 2.2,
    align: "right",
  });

  context.save();
  context.fillStyle = "rgba(5, 27, 25, 0.88)";
  context.fillRect(75, 784, 930, 118);
  context.strokeStyle = "rgba(186, 255, 225, 0.32)";
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(75, 784);
  context.lineTo(1005, 784);
  context.stroke();
  context.restore();

  drawText(context, "HH", 94, 847, {
    font: "900 78px Arial Black, Arial, sans-serif",
    color: "#d8ffec",
    tracking: -6,
  });
  drawText(context, "GOA / 26", 251, 824, {
    font: "900 38px Arial, sans-serif",
    color: "#ffffff",
    tracking: 1.3,
  });
  drawText(context, "BUILDER RESIDENCY", 254, 857, {
    font: "700 16px Arial, sans-serif",
    color: "#9ee4c5",
    tracking: 3.1,
  });
  drawText(context, "AI × CRYPTO × MULTICHAIN", 976, 858, {
    font: "700 17px Arial, sans-serif",
    color: "#ffb49d",
    tracking: 1.2,
    align: "right",
  });

  context.save();
  context.strokeStyle = "rgba(187, 255, 224, 0.72)";
  context.lineWidth = 2;
  context.setLineDash([5, 9]);
  context.beginPath();
  context.moveTo(85, 948);
  context.lineTo(995, 948);
  context.stroke();
  context.restore();

  drawText(context, "FRAME IN GOA", 80, 983, {
    font: "700 15px Arial, sans-serif",
    color: "#b8ffe1",
    tracking: 3,
  });
  drawText(context, "247 BUILDERS / 04 DAYS / ONE COASTLINE", 1000, 983, {
    font: "600 14px Arial, sans-serif",
    color: "rgba(220, 255, 239, 0.78)",
    tracking: 1.7,
    align: "right",
  });
  drawSignalMark(context, 954, 122);
}
