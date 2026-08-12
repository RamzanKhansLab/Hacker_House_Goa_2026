import { useCallback, useEffect, useRef } from "react";
import { canvasToBlob, renderGraphic } from "../renderer/canvasRenderer";

export function useCanvasRenderer({ image, format, crop, builder }) {
  const canvasRef = useRef(null);

  const render = useCallback(() => {
    if (!canvasRef.current || !image) return false;
    return renderGraphic(canvasRef.current, { image, format, crop, builder });
  }, [image, format, crop, builder]);

  useEffect(() => {
    if (!image) return undefined;
    const frame = window.requestAnimationFrame(render);
    return () => window.cancelAnimationFrame(frame);
  }, [image, render]);

  const getBlob = useCallback(async () => {
    if (!canvasRef.current || !image) throw new Error("NO_GRAPHIC");
    render();
    return canvasToBlob(canvasRef.current);
  }, [image, render]);

  return { canvasRef, render, getBlob };
}
