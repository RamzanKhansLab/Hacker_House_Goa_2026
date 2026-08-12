import { useCallback, useEffect, useRef, useState } from "react";
import { prepareImage } from "../utils/imageProcessor";
import { validateImageFile } from "../utils/fileValidation";

const friendlyErrors = {
  HEIC_PROCESSING_FAILED: "We couldn't process this HEIC image. Try another photo.",
  IMAGE_LOAD_FAILED: "We couldn't read this image. Try another photo.",
};

export function useImageUpload() {
  const [imageAsset, setImageAsset] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const activeUrlRef = useRef(null);

  const releaseCurrentUrl = useCallback(() => {
    if (activeUrlRef.current) {
      URL.revokeObjectURL(activeUrlRef.current);
      activeUrlRef.current = null;
    }
  }, []);

  const selectFile = useCallback(async (file) => {
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setError(validation.message);
      return false;
    }

    setError("");
    setProcessing(true);
    try {
      const prepared = await prepareImage(file);
      releaseCurrentUrl();
      activeUrlRef.current = prepared.sourceUrl;
      setImageAsset(prepared);
      return true;
    } catch (caughtError) {
      const errorCode = caughtError instanceof Error ? caughtError.message : "";
      setError(friendlyErrors[errorCode] || "We couldn't process this photo. Try another image.");
      return false;
    } finally {
      setProcessing(false);
    }
  }, [releaseCurrentUrl]);

  const clearImage = useCallback(() => {
    releaseCurrentUrl();
    setImageAsset(null);
    setError("");
  }, [releaseCurrentUrl]);

  useEffect(() => releaseCurrentUrl, [releaseCurrentUrl]);

  return {
    imageAsset,
    processing,
    error,
    setError,
    selectFile,
    clearImage,
  };
}
