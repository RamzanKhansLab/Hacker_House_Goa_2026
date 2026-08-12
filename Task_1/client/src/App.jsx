import { useCallback, useMemo, useState } from "react";
import { BUILDER_TITLES, FORMATS } from "./constants";
import Editor from "./components/Editor";
import Header from "./components/Header";
import UploadDropzone from "./components/UploadDropzone";
import { useCanvasRenderer } from "./hooks/useCanvasRenderer";
import { useImageUpload } from "./hooks/useImageUpload";
import { useShare } from "./hooks/useShare";

const initialCrop = { zoom: 1, position: { x: 0, y: 0 } };
const initialBuilder = {
  name: "",
  role: "",
  stack: "",
  builderTitle: BUILDER_TITLES[1],
};

function downloadBlob(blob, filename) {
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
}

export default function App() {
  const { imageAsset, processing, error, setError, selectFile } = useImageUpload();
  const [format, setFormat] = useState(FORMATS.PFP);
  const [crop, setCrop] = useState(initialCrop);
  const [builder, setBuilder] = useState(initialBuilder);
  const [exporting, setExporting] = useState(false);
  const { canvasRef, getBlob } = useCanvasRenderer({
    image: imageAsset?.image,
    format,
    crop,
    builder,
  });
  const { sharing, shareMessage, share } = useShare();

  const handleFile = useCallback(async (file) => {
    const wasLoaded = await selectFile(file);
    if (wasLoaded) setCrop(initialCrop);
  }, [selectFile]);

  const updateCrop = useCallback((key, value) => {
    setCrop((current) => {
      if (key === "zoom") return { ...current, zoom: value };
      return { ...current, position: { ...current.position, [key]: value } };
    });
  }, []);

  const updateBuilder = useCallback((key, value) => {
    setBuilder((current) => ({ ...current, [key]: value }));
  }, []);

  const download = useCallback(async () => {
    setExporting(true);
    setError("");
    try {
      const blob = await getBlob();
      downloadBlob(blob, format === FORMATS.ID_CARD ? "hh-goa-2026-builder.png" : "hh-goa-2026-pfp.png");
    } catch {
      setError("We couldn't export this graphic. Please try again.");
    } finally {
      setExporting(false);
    }
  }, [format, getBlob, setError]);

  const handleShare = useCallback(async () => {
    setError("");
    try {
      await share({ getBlob, format });
    } catch {
      // The share hook publishes a deliberate recovery message beside the action.
    }
  }, [format, getBlob, setError, share]);

  const explorerLabel = useMemo(() => format === FORMATS.ID_CARD ? "BUILDER ID" : "PFP FRAME", [format]);

  return (
    <div className="app-shell">
      <div className="ambient ambient--one" aria-hidden="true" />
      <div className="ambient ambient--two" aria-hidden="true" />
      <Header />
      <main id="generator">
        {!imageAsset ? (
          <section className="hero" aria-labelledby="hero-title">
            <div className="hero-grid" aria-hidden="true" />
            <p className="eyebrow">HACKER HOUSE GOA / 2026</p>
            <h1 id="hero-title">Your builder identity,<br /><em>framed for Goa.</em></h1>
            <p className="hero-copy">Upload a photo. We’ll compose a high-res frame on your device — ready for your profile, post, or next protocol.</p>
            <UploadDropzone onFile={handleFile} processing={processing} />
            <div className="hero-signals" aria-label="Product benefits">
              <span><i aria-hidden="true">01</i>ON-DEVICE RENDERING</span>
              <span><i aria-hidden="true">02</i>NO SIGN-UP</span>
              <span><i aria-hidden="true">03</i>1080PX EXPORT</span>
            </div>
          </section>
        ) : (
          <Editor
            canvasRef={canvasRef}
            imageAsset={imageAsset}
            processing={processing}
            onFile={handleFile}
            format={format}
            onFormat={setFormat}
            crop={crop}
            onCrop={updateCrop}
            onReset={() => setCrop(initialCrop)}
            builder={builder}
            onBuilderChange={updateBuilder}
            onDownload={download}
            onShare={handleShare}
            sharing={sharing || exporting}
            shareMessage={shareMessage}
          />
        )}

        {error && <p className="error-banner" role="alert">{error}</p>}
      </main>
      <footer className="site-footer">
        <span>HH GOA 2026</span>
        <span>{explorerLabel} / AI × CRYPTO × MULTICHAIN</span>
        <span>BUILT TO SHIP</span>
      </footer>
    </div>
  );
}
