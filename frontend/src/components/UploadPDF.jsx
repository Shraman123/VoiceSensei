/**
 * UploadPDF — drag-and-drop or click to upload study material.
 * Calls the /upload endpoint to ingest into FAISS.
 */
import { useRef, useState } from "react";

export default function UploadPDF({ apiUrl, onLoaded }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState("");

  const handleFile = async (file) => {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }
    setError("");
    setUploading(true);

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch(`${apiUrl}/upload`, { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Upload failed (${res.status})`);
      }
      const data = await res.json();
      setUploadedFiles((prev) => [...prev, data.filename]);
      onLoaded(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <button
        className="upload-area"
        onClick={() => inputRef.current?.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files?.[0]); }}
        onDragOver={(e) => e.preventDefault()}
        disabled={uploading}
        style={{ opacity: uploading ? 0.6 : 1 }}
      >
        <span className="upload-icon">{uploading ? "⏳" : "📄"}</span>
        {uploading ? "Uploading…" : "Upload PDF notes"}
        <span className="upload-hint">NCERT · JEE · UPSC · Any PDF</span>
      </button>

      <input ref={inputRef} type="file" accept=".pdf" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files?.[0])} />

      {error && <p style={{ fontSize: 11, color: "var(--danger)", marginTop: 6, padding: "0 4px" }}>{error}</p>}

      {uploadedFiles.map((f) => (
        <div key={f} style={{
          fontSize: 11, color: "var(--success)", marginTop: 4,
          padding: "4px 8px", background: "var(--success-dim)",
          borderRadius: 4, display: "flex", alignItems: "center", gap: 4,
        }}>
          ✓ {f.length > 22 ? f.slice(0, 20) + "…" : f}
        </div>
      ))}
    </div>
  );
}
