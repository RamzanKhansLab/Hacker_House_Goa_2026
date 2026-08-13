import { drawText, fitText } from "./textRenderer";
import { roundedPath } from "./frameRenderer";

export function idCardPhotoBounds() {
  return { x: 58, y: 108, width: 964, height: 548, radius: 30 };
}

export function drawIdCardPhotoTreatment(context, bounds) {
  const shade = context.createLinearGradient(0, bounds.y + bounds.height * 0.45, 0, bounds.y + bounds.height);
  shade.addColorStop(0, "rgba(3, 18, 17, 0)");
  shade.addColorStop(1, "rgba(3, 18, 17, 0.68)");
  context.fillStyle = shade;
  roundedPath(context, bounds.x, bounds.y, bounds.width, bounds.height, bounds.radius);
  context.fill();
}

export function drawIdCard(context, builder) {
  const bounds = idCardPhotoBounds();
  context.save();
  context.strokeStyle = "rgba(245, 241, 232, 0.75)";
  context.lineWidth = 2;
  roundedPath(context, bounds.x, bounds.y, bounds.width, bounds.height, bounds.radius);
  context.stroke();
  context.restore();

  drawText(context, "HACKER HOUSE", 77, 61, {
    font: "700 22px Arial, sans-serif",
    color: "#fffbe8",
    tracking: 3.4,
  });
  drawText(context, "GOA // 2026", 1000, 61, {
    font: "700 22px Arial, sans-serif",
    color: "#ffe719",
    tracking: 2.3,
    align: "right",
  });

  context.save();
  context.fillStyle = "#004b31";
  roundedPath(context, 58, 684, 964, 330, 30);
  context.fill();
  context.strokeStyle = "rgba(245, 241, 232, 0.45)";
  context.lineWidth = 2;
  context.stroke();
  context.fillStyle = "#ff0073";
  context.fillRect(58, 684, 10, 330);
  context.restore();

  const name = builder.name?.trim() || "YOUR NAME";
  const role = builder.role?.trim() || "BUILDER";
  const stack = builder.stack?.trim() || "AI · CRYPTO · MULTICHAIN";
  const title = builder.builderTitle?.trim() || "ONCHAIN BUILDER";
  const nameSize = fitText(context, name.toUpperCase(), 820, { minSize: 40, maxSize: 74, weight: 800 });

  drawText(context, "BUILDER ID // 247", 100, 735, {
    font: "700 16px Arial, sans-serif",
    color: "#ffe719",
    tracking: 3,
  });
  drawText(context, name.toUpperCase(), 98, 809, {
    font: `800 ${nameSize}px Arial, sans-serif`,
    color: "#ffffff",
    tracking: 0.6,
  });
  drawText(context, role.toUpperCase(), 100, 853, {
    font: "700 24px Arial, sans-serif",
    color: "#ff57a2",
    tracking: 1.6,
  });

  context.save();
  context.fillStyle = "rgba(255, 231, 25, 0.14)";
  roundedPath(context, 98, 884, 884, 86, 15);
  context.fill();
  context.restore();
  drawText(context, title.toUpperCase(), 122, 920, {
    font: "700 19px Arial, sans-serif",
    color: "#ffe719",
    tracking: 1.8,
  });
  drawText(context, stack.toUpperCase(), 122, 950, {
    font: "600 17px Arial, sans-serif",
    color: "rgba(245, 241, 232, 0.8)",
    tracking: 1,
    maxWidth: 810,
  });

  drawText(context, "#FRAMEINGOA", 1000, 1000, {
    font: "700 15px Arial, sans-serif",
    color: "#d7ff3f",
    tracking: 2.2,
    align: "right",
  });
}
