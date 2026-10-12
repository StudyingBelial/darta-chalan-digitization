import React, { useState } from 'react';
import { X, Copy, Download, FileText, Check, Cpu } from 'lucide-react';
import { dartaService, chalanService } from '../services/apiServices';

interface OCRViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentType: 'DARTA' | 'CHALAN';
  documentData: any;
  onOcrUpdated?: () => void;
}

export const OCRViewerModal: React.FC<OCRViewerModalProps> = ({
  isOpen,
  onClose,
  documentType,
  documentData,
  onOcrUpdated,
}) => {
  const [isCopied, setIsCopied] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrText, setOcrText] = useState<string>(documentData?.extracted_ocr_text || '');

  if (!isOpen || !documentData) return null;

  const docId = documentData.id || (documentType === 'DARTA' ? documentData.darta_id : documentData.chalan_id);
  const docTitle = documentType === 'DARTA'
    ? `Darta #${documentData.darta_id}`
    : `Chalan #${documentData.chalan_id}`;

  const handleCopyText = () => {
    if (ocrText) {
      navigator.clipboard.writeText(ocrText);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const handleRunOcr = async () => {
    setIsProcessing(true);
    try {
      let updated;
      if (documentType === 'DARTA') {
        updated = await dartaService.triggerOCR(docId);
      } else {
        updated = await chalanService.triggerOCR(docId);
      }
      setOcrText(updated.extracted_ocr_text || '');
      if (onOcrUpdated) onOcrUpdated();
    } catch (err) {
      console.error('OCR processing failed:', err);
      alert('Failed to process OCR. Ensure OCR service is active on backend.');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadUrl = documentType === 'DARTA'
    ? dartaService.getDownloadUrl(docId)
    : chalanService.getDownloadUrl(docId);

  return (
    <div className="modal-overlay">
      <div className="modal-content modal-lg">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FileText size={22} color="#003b73" />
            <div>
              <h3 className="modal-title">{docTitle} - Document Details & OCR Reader</h3>
              <p style={{ fontSize: '0.75rem', color: '#64748b' }}>
                Topic: {documentData.topic} | File: {documentData.file_name}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="close-btn"><X size={20} /></button>
        </div>

        <div className="modal-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Metadata Column */}
          <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#003b73', marginBottom: '1rem' }}>
              Document Metadata
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div>
                <strong style={{ color: '#475569' }}>Date (AD / BS):</strong>
                <p>{documentType === 'DARTA' ? documentData.darta_date : documentData.chalan_date} {documentData.darta_date_bs || documentData.chalan_date_bs ? `(${documentData.darta_date_bs || documentData.chalan_date_bs} BS)` : ''}</p>
              </div>
              {documentType === 'DARTA' ? (
                <>
                  <div>
                    <strong style={{ color: '#475569' }}>Sender Information:</strong>
                    <p>{documentData.sender} ({documentData.sender_email})</p>
                  </div>
                  <div>
                    <strong style={{ color: '#475569' }}>Target Officer/Dept:</strong>
                    <p>{documentData.officer?.receiver_officer || 'N/A'} - {documentData.department?.receiver_department || 'N/A'}</p>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <strong style={{ color: '#475569' }}>Receiver Information:</strong>
                    <p>{documentData.receiver?.name} ({documentData.receiver?.email})</p>
                  </div>
                  <div>
                    <strong style={{ color: '#475569' }}>Sender Dept / Officer:</strong>
                    <p>{documentData.sender?.department || 'N/A'} - {documentData.sender?.officer || 'N/A'}</p>
                  </div>
                </>
              )}
              <div>
                <strong style={{ color: '#475569' }}>Status:</strong>
                <p><span className="badge badge-registered">{documentData.status || 'REGISTERED'}</span></p>
              </div>
              <div style={{ marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      if (documentType === 'DARTA') {
                        await dartaService.downloadFile(docId, documentData.file_name);
                      } else {
                        await chalanService.downloadFile(docId, documentData.file_name);
                      }
                    } catch (e) {
                      console.error('Download failed:', e);
                      alert('Failed to download document attachment.');
                    }
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ width: '100%' }}
                >
                  <Download size={14} /> Download Original Attachment
                </button>
              </div>
            </div>
          </div>

          {/* OCR Extracted Text Column */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#003b73' }}>
                Extracted OCR Text
              </h4>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={handleRunOcr}
                  disabled={isProcessing}
                  className="btn btn-accent btn-sm"
                  title="Run Tesseract OCR"
                >
                  <Cpu size={14} /> {isProcessing ? 'Processing...' : 'Run OCR'}
                </button>
                <button
                  onClick={handleCopyText}
                  disabled={!ocrText}
                  className="btn btn-secondary btn-sm"
                  title="Copy Text"
                >
                  {isCopied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  {isCopied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <textarea
              readOnly
              value={ocrText || 'No OCR text extracted yet. Click "Run OCR" to process this document.'}
              style={{
                width: '100%',
                height: '240px',
                padding: '0.75rem',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                backgroundColor: ocrText ? '#ffffff' : '#f8fafc',
                color: ocrText ? '#0f172a' : '#64748b',
                resize: 'none',
                lineHeight: '1.6'
              }}
            />
          </div>
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  );
};
