/**
 * MobileMenu — bottom sheet that surfaces sidebar controls on small screens.
 */
import ModeToggle from "./ModeToggle";
import SubjectSelector from "./SubjectSelector";
import LanguageToggle from "./LanguageToggle";
import UploadPDF from "./UploadPDF";

export default function MobileMenu({
  open, onClose,
  mode, onModeChange,
  subject, onSubjectChange,
  language, onLanguageChange,
  apiUrl, onPdfLoaded,
  ragLoaded, ragMeta,
}) {
  return (
    <>
      {open && <div className="mobile-overlay" onClick={onClose} />}
      <div className={`mobile-sheet${open ? " open" : ""}`}>
        <div className="mobile-sheet-handle" />

        <div className="mobile-sheet-body">
          <div className="sidebar-section">
            <span className="section-label">Mode</span>
            <ModeToggle mode={mode} onChange={(m) => { onModeChange(m); onClose(); }} />
          </div>

          <div className="sidebar-section">
            <span className="section-label">Language</span>
            <LanguageToggle language={language} onChange={onLanguageChange} />
          </div>

          <div className="sidebar-section">
            <span className="section-label">Subject</span>
            <SubjectSelector subject={subject} onChange={onSubjectChange} />
          </div>

          <div className="sidebar-section">
            <span className="section-label">Study Material</span>
            <UploadPDF apiUrl={apiUrl} onLoaded={(m) => { onPdfLoaded(m); onClose(); }} />
            {ragLoaded && ragMeta && (
              <div className="rag-badge">
                ✓ {ragMeta.pages} pages · {ragMeta.chunks} chunks indexed
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
