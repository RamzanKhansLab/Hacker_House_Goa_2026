import { ACCEPTED_EXTENSIONS, ACCEPTED_MIME_TYPES, MAX_UPLOAD_BYTES } from "../constants.js";

export function getFileExtension(name = "") {
  const extension = name.split(".").pop();
  return extension && extension !== name ? extension.toLowerCase() : "";
}

export function isHeicFile(file) {
  const extension = getFileExtension(file?.name);
  const mime = (file?.type || "").toLowerCase();
  return ["heic", "heif"].includes(extension) || mime.includes("heic") || mime.includes("heif");
}

export function validateImageFile(file) {
  if (!file) {
    return { valid: false, message: "Choose a photo to continue." };
  }

  const extension = getFileExtension(file.name);
  const mime = (file.type || "").toLowerCase();
  const supportedExtension = ACCEPTED_EXTENSIONS.includes(extension);
  const supportedMime = !mime || ACCEPTED_MIME_TYPES.has(mime);

  if (!supportedExtension || !supportedMime) {
    return {
      valid: false,
      message: "This file format isn't supported. Use JPG, PNG, HEIC, or HEIF.",
    };
  }

  if (file.size > MAX_UPLOAD_BYTES) {
    return {
      valid: false,
      message: "This image is too large to process. Please choose a photo smaller than 20 MB.",
    };
  }

  if (file.size === 0) {
    return { valid: false, message: "This image is empty. Please choose another photo." };
  }

  return { valid: true };
}
