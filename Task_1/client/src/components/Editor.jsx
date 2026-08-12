import { FORMATS } from "../constants";
import BuilderFields from "./BuilderFields";
import PreviewCanvas from "./PreviewCanvas";
import UploadDropzone from "./UploadDropzone";

function RangeControl({ label, value, min, max, onChange, valueText, left, right }) {
  return <label className="range-control"><span className="range-label"><strong>{label}</strong><output>{valueText}</output></span><input type="range" min={min} max={max} step="0.01" value={value} onChange={(event) => onChange(Number(event.target.value))} /><span className="range-ends"><span>{left}</span><span>{right}</span></span></label>;
}

export default function Editor({ canvasRef, imageAsset, processing, onFile, format, onFormat, crop, onCrop, onReset, builder, onBuilderChange, onDownload, onShare, sharing, shareMessage, downloaded }) {
  return (
    <section className="editor" aria-label="Builder ID editor">
      <div className="editor-grid">
        <div className="preview-column"><PreviewCanvas canvasRef={canvasRef} format={format} imageName={imageAsset.name} /></div>
        <div className="controls-column">
          <section className="control-section" aria-labelledby="format-label">
            <p className="control-kicker" id="format-label">01 / SELECT YOUR OUTPUT</p>
            <div className="format-selector" role="group" aria-labelledby="format-label">
              <button type="button" className={format === FORMATS.PFP ? "is-selected" : ""} onClick={() => onFormat(FORMATS.PFP)}><span>PFP FRAME</span><small>Profile-ready signal</small></button>
              <button type="button" className={format === FORMATS.ID_CARD ? "is-selected" : ""} onClick={() => onFormat(FORMATS.ID_CARD)}><span>BUILDER ID</span><small>Your builder passport</small></button>
            </div>
          </section>
          <UploadDropzone compact onFile={onFile} processing={processing} fileName={imageAsset.name} />
          <section className="control-section crop-section" aria-labelledby="crop-label">
            <div className="control-heading"><p className="control-kicker" id="crop-label">02 / SET YOUR PORTRAIT</p><button type="button" className="text-button" onClick={onReset}>RESET CROP</button></div>
            <RangeControl label="Zoom" value={crop.zoom} min={1} max={3} onChange={(value) => onCrop("zoom", value)} valueText={`${Math.round(crop.zoom * 100)}%`} left="100%" right="300%" />
            <RangeControl label="Horizontal" value={crop.position.x} min={-1} max={1} onChange={(value) => onCrop("x", value)} valueText={crop.position.x === 0 ? "Center" : crop.position.x < 0 ? "Left" : "Right"} left="Left" right="Right" />
            <RangeControl label="Vertical" value={crop.position.y} min={-1} max={1} onChange={(value) => onCrop("y", value)} valueText={crop.position.y === 0 ? "Center" : crop.position.y < 0 ? "Top" : "Bottom"} left="Top" right="Bottom" />
          </section>
          {format === FORMATS.ID_CARD && <BuilderFields builder={builder} onChange={onBuilderChange} />}
          <section className="action-bar" aria-label="Export actions">
            <button type="button" className="button button--secondary" onClick={onDownload}>{downloaded ? "PNG READY ↓" : "DOWNLOAD PNG ↓"}</button>
            <button type="button" className="button button--primary" onClick={onShare} disabled={sharing}>{sharing ? "PREPARING…" : "SHARE TO X ↗"}</button>
            {shareMessage && <p className="share-message" role="status">{shareMessage}</p>}
          </section>
          <aside className="crew-note"><span>04 / CREW MODE</span><strong>One frame. More builders.</strong><p>Pass this ID around the team — every builder gets their own signal.</p></aside>
        </div>
      </div>
    </section>
  );
}
