export default function PreviewCanvas({ canvasRef, format, imageName }) {
  return (
    <section className="preview-panel" aria-label="Generated graphic preview">
      <div className="preview-meta">
        <span className="live-indicator"><i aria-hidden="true" />LIVE PREVIEW</span>
        <span>1080 × 1080 PNG</span>
      </div>
      <div className={`canvas-shell ${format === "id-card" ? "canvas-shell--id" : ""}`}>
        <canvas
          ref={canvasRef}
          className="preview-canvas"
          role="img"
          aria-label={`Live ${format === "id-card" ? "builder ID card" : "profile frame"} preview for ${imageName || "your photo"}`}
        />
      </div>
      <p className="preview-note">Your original photo stays on this device. Only the final PNG is used if you choose the share-link fallback.</p>
    </section>
  );
}
