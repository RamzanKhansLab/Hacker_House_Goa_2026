import { env } from "../config/env.js";
import { shareService } from "../services/shareService.js";
import { storageService } from "../services/storageService.js";
import { validateSharePayload } from "../utils/validateSharePayload.js";

function publicBaseUrl(request) {
  return env.publicServerUrl || `${request.protocol}://${request.get("host")}`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[character]));
}

export async function createShare(request, response, next) {
  try {
    const validation = validateSharePayload(request.body);
    if (!validation.valid) return response.status(400).json({ message: validation.message });
    const share = await shareService.create({ imageBuffer: validation.buffer, format: request.body.format });
    const baseUrl = publicBaseUrl(request);
    return response.status(201).json({
      url: `${baseUrl}/share/${share.slug}`,
      expiresAt: share.expiresAt,
    });
  } catch (error) {
    return next(error);
  }
}

export async function getSharePage(request, response, next) {
  try {
    const share = await shareService.get(request.params.slug);
    if (!share) {
      return response.status(404).type("html").send(expiredHtml());
    }
    const baseUrl = publicBaseUrl(request);
    const imageUrl = storageService.getPublicUrl(share.imageFileName, baseUrl);
    return response.type("html").send(shareHtml({ imageUrl, pageUrl: `${baseUrl}/share/${share.slug}` }));
  } catch (error) {
    return next(error);
  }
}

function layout({ title, description, imageUrl = "", pageUrl = "", body }) {
  const safeTitle = escapeHtml(title);
  const safeDescription = escapeHtml(description);
  const ogTags = imageUrl ? `
    <meta property="og:title" content="${safeTitle}">
    <meta property="og:description" content="${safeDescription}">
    <meta property="og:image" content="${escapeHtml(imageUrl)}">
    <meta property="og:image:type" content="image/png">
    <meta property="og:type" content="website">
    <meta property="og:url" content="${escapeHtml(pageUrl)}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${safeTitle}">
    <meta name="twitter:description" content="${safeDescription}">
    <meta name="twitter:image" content="${escapeHtml(imageUrl)}">` : "";
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${safeTitle}</title>${ogTags}<style>body{margin:0;background:#061a19;color:#edfff7;font-family:Arial,sans-serif}main{width:min(92vw,680px);margin:0 auto;padding:48px 0;text-align:center}img{display:block;width:100%;margin:28px 0;border:1px solid #74cfa9;box-shadow:0 18px 60px #0008}a{display:inline-block;padding:14px 20px;background:#b8ffe1;color:#061a19;font-weight:700;text-decoration:none}p{color:#b4d4c7;line-height:1.55}.eyebrow{color:#ffad95;font-size:12px;font-weight:bold;letter-spacing:2px}</style></head><body>${body}</body></html>`;
}

function shareHtml({ imageUrl, pageUrl }) {
  return layout({
    title: "HH Goa 2026 — Builder Frame",
    description: "A builder frame created for Hacker House Goa 2026. #FrameInGoa",
    imageUrl,
    pageUrl,
    body: `<main><p class="eyebrow">HACKER HOUSE GOA // 2026</p><h1>Builder frame</h1><p>Made for builders shaping AI × Crypto × Multichain.</p><img src="${escapeHtml(imageUrl)}" alt="Hacker House Goa 2026 builder frame"><a href="${escapeHtml(imageUrl)}" download="hh-goa-2026-frame.png">Download PNG</a></main>`,
  });
}

function expiredHtml() {
  return layout({
    title: "This share has expired — HH Goa 2026",
    description: "Create a fresh Hacker House Goa 2026 builder frame.",
    body: "<main><p class=\"eyebrow\">HACKER HOUSE GOA // 2026</p><h1>This share has expired.</h1><p>Generated images are held temporarily for privacy. Create a fresh frame to keep building.</p><a href=\"/\">Open generator</a></main>",
  });
}
