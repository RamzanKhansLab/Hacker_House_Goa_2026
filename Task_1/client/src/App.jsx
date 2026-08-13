import { useCallback, useMemo, useState } from "react";
import { BUILDER_TITLES, FORMATS } from "./constants";
import Editor from "./components/Editor";
import Header from "./components/Header";
import UploadDropzone from "./components/UploadDropzone";
import { useCanvasRenderer } from "./hooks/useCanvasRenderer";
import { useImageUpload } from "./hooks/useImageUpload";
import { useShare } from "./hooks/useShare";
import { useButtonSounds } from "./hooks/useButtonSounds";

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
  useButtonSounds();
  const { imageAsset, processing, error, setError, selectFile } = useImageUpload();
  const [format, setFormat] = useState(FORMATS.PFP);
  const [crop, setCrop] = useState(initialCrop);
  const [builder, setBuilder] = useState(initialBuilder);
  const [exporting, setExporting] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
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
      setDownloaded(true);
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
            <p className="eyebrow">GOA, INDIA · 28—31 OCT 2026</p>
            <div className="signal-orbit" aria-hidden="true"><span>247</span><i>BUILD · SHIP · REPEAT · </i></div>
            <h1 id="hero-title"><span>CLAIM YOUR</span><em>BUILDER ID.</em><b>HH GOA / 2026</b></h1>
            <p className="hero-copy">Your beachside builder passport. Upload a portrait, claim your class, and take the signal to the timeline.</p>
            <UploadDropzone onFile={handleFile} processing={processing} />
            <div className="hero-signals" aria-label="Product benefits">
              <span><i aria-hidden="true">01</i>LOCAL RENDER</span>
              <span><i aria-hidden="true">02</i>NO SIGN-UP</span>
              <span><i aria-hidden="true">03</i>POST READY</span>
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
            downloaded={downloaded}
          />
        )}

        {error && <p className="error-banner" role="alert">{error}</p>}
      </main>
      <section className="journey" aria-labelledby="journey-title">
        <p className="journey-kicker">FROM CAMERA ROLL TO TIMELINE</p>
        <h2 id="journey-title">ONE PHOTO.<br /><em>FULL SIGNAL.</em></h2>
        <div className="journey-steps">
          <article><span>01</span><h3>UPLOAD</h3><p>Choose any clear photo. Portrait, landscape or slightly off-centre — the crop is ready for it.</p></article>
          <article><span>02</span><h3>MAKE IT YOURS</h3><p>Pick a frame, shape your portrait and add the builder details that make it yours.</p></article>
          <article><span>03</span><h3>PUT IT OUT</h3><p>Download a crisp PNG or share straight to X with <strong>#FrameInGoa</strong> pre-filled.</p></article>
        </div>
      </section>
      <footer className="site-footer">
        <span>HH GOA / 2026</span>
        <span>{explorerLabel} · 28—31 OCT · GOA, INDIA</span>
        <span>LESS NOISE. MORE SIGNAL.</span>
      </footer>
    </div>
  );
}
