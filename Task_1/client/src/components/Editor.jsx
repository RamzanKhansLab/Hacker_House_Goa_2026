import { FORMATS } from "../constants";
import BuilderFields from "./BuilderFields";
import PreviewCanvas from "./PreviewCanvas";
import UploadDropzone from "./UploadDropzone";

function RangeControl({ label, value, min, max, step = 0.01, onChange, valueText, left, right }) {
  return (
    <label className="range-control">
      <span className="range-label"><strong>{label}</strong><output>{valueText}</output></span>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
      <span className="range-ends"><span>{left}</span><span>{right}</span></span>
    </label>
  );
}

export default function Editor({
  canvasRef,
  imageAsset,
  processing,
  onFile,
  format,
  onFormat,
  crop,
  onCrop,
  onReset,
  builder,
  onBuilderChange,
  onDownload,
  onShare,
  sharing,
  shareMessage,
}) {
  return (
    <section className="editor" aria-labelledby="editor-title">
      <div className="editor-heading">
        <p className="eyebrow">01 — COMPOSE</p>
        <h2 id="editor-title">Frame your builder energy.</h2>
        <p>Fine-tune the image locally, then take the graphic wherever builders are gathering.</p>
      </div>

      <div className="editor-grid">
        <div className="preview-column">
          <PreviewCanvas canvasRef={canvasRef} format={format} imageName={imageAsset.name} />
        </div>

        <div className="controls-column">
          <section className="control-section" aria-labelledby="format-label">
            <p className="control-kicker" id="format-label">OUTPUT FORMAT</p>
            <div className="format-selector" role="group" aria-labelledby="format-label">
              <button type="button" className={format === FORMATS.PFP ? "is-selected" : ""} onClick={() => onFormat(FORMATS.PFP)}>
                <span>PFP FRAME</span><small>Profile ready</small>
              </button>
              <button type="button" className={format === FORMATS.ID_CARD ? "is-selected" : ""} onClick={() => onFormat(FORMATS.ID_CARD)}>
                <span>BUILDER ID</span><small>Social card</small>
              </button>
            </div>
          </section>

          <UploadDropzone compact onFile={onFile} processing={processing} fileName={imageAsset.name} />

          <section className="control-section crop-section" aria-labelledby="crop-label">
            <div className="control-heading"><p className="control-kicker" id="crop-label">PHOTO POSITION</p><button type="button" className="text-button" onClick={onReset}>Reset</button></div>
            <RangeControl label="Zoom" value={crop.zoom} min={1} max={3} onChange={(value) => onCrop("zoom", value)} valueText={`${Math.round(crop.zoom * 100)}%`} left="100%" right="300%" />
            <RangeControl label="Horizontal" value={crop.position.x} min={-1} max={1} onChange={(value) => onCrop("x", value)} valueText={crop.position.x === 0 ? "Center" : crop.position.x < 0 ? "Left" : "Right"} left="Left" right="Right" />
            <RangeControl label="Vertical" value={crop.position.y} min={-1} max={1} onChange={(value) => onCrop("y", value)} valueText={crop.position.y === 0 ? "Center" : crop.position.y < 0 ? "Top" : "Bottom"} left="Top" right="Bottom" />
          </section>

          {format === FORMATS.ID_CARD && <BuilderFields builder={builder} onChange={onBuilderChange} />}

          <section className="action-bar" aria-label="Export actions">
            <button type="button" className="button button--secondary" onClick={onDownload}>Download PNG <span aria-hidden="true">↓</span></button>
            <button type="button" className="button button--primary" onClick={onShare} disabled={sharing}>{sharing ? "Preparing share…" : "Share to X ↗"}</button>
            {shareMessage && <p className="share-message" role="status">{shareMessage}</p>}
          </section>
        </div>
      </div>
    </section>
  );
}
