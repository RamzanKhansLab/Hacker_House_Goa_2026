import { useRef, useState } from "react";

export default function UploadDropzone({ onFile, processing, compact = false, fileName }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const processFiles = (files) => {
    const firstFile = files?.[0];
    if (firstFile) onFile(firstFile);
  };

  const openPicker = () => {
    if (!processing) inputRef.current?.click();
  };

  return (
    <div
      className={`upload-dropzone ${compact ? "upload-dropzone--compact" : ""} ${dragging ? "is-dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        processFiles(event.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        accept=".jpg,.jpeg,.png,.heic,.heif,image/jpeg,image/png,image/heic,image/heif"
        capture="user"
        onChange={(event) => {
          processFiles(event.target.files);
          event.target.value = "";
        }}
      />
      <div className="upload-icon" aria-hidden="true">↗</div>
      <div className="upload-copy">
        <strong>{processing ? "Processing photo…" : compact ? "Replace photo" : "Drop your photo here"}</strong>
        <span>{processing ? "Preparing your local preview" : fileName || "or choose from your device"}</span>
      </div>
      <button type="button" className="button button--upload" onClick={openPicker} disabled={processing}>
        {processing ? "Working…" : compact ? "Choose photo" : "Upload photo"}
      </button>
      {!compact && <p className="upload-hint">JPG · PNG · HEIC · HEIF <span>·</span> Up to 20 MB</p>}
    </div>
  );
}
