import { isHeicFile } from "./fileValidation";

function loadImage(sourceUrl) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.decoding = "async";
    image.onload = async () => {
      try {
        if (typeof image.decode === "function") await image.decode();
        resolve(image);
      } catch {
        // Some Safari builds report decode errors after an already usable onload event.
        resolve(image);
      }
    };
    image.onerror = () => reject(new Error("IMAGE_LOAD_FAILED"));
    image.src = sourceUrl;
  });
}

function convertedName(name) {
  return name.replace(/\.(heic|heif)$/i, ".jpg");
}

export async function prepareImage(file) {
  let workingFile = file;

  if (isHeicFile(file)) {
    try {
      // HEIC decoding is an exception to the small-bundle rule. Loading it only
      // when needed keeps the normal JPG/PNG first load fast.
      const { default: heic2any } = await import("heic2any");
      const conversion = await heic2any({
        blob: file,
        toType: "image/jpeg",
        quality: 0.92,
      });
      const convertedBlob = Array.isArray(conversion) ? conversion[0] : conversion;
      workingFile = new File([convertedBlob], convertedName(file.name), {
        type: "image/jpeg",
        lastModified: Date.now(),
      });
    } catch (error) {
      console.warn("HEIC conversion failed", error);
      throw new Error("HEIC_PROCESSING_FAILED");
    }
  }

  const sourceUrl = URL.createObjectURL(workingFile);
  try {
    const image = await loadImage(sourceUrl);
    if (!image.naturalWidth || !image.naturalHeight) {
      throw new Error("IMAGE_LOAD_FAILED");
    }
    return {
      image,
      sourceUrl,
      width: image.naturalWidth,
      height: image.naturalHeight,
      name: workingFile.name,
    };
  } catch (error) {
    URL.revokeObjectURL(sourceUrl);
    throw error;
  }
}
