import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle,
  AlertTriangle,
  FileText,
  Printer,
  Mail,
  Upload,
  Calendar,
  Building,
  User,
  X,
  Eye,
  RefreshCw,
  Sliders,
  Send,
  HelpCircle
} from 'lucide-react';
import {
  InboundDocument,
  ParsedCandidateFields,
  DepartmentResponse,
  OfficerResponse,
  FinancialYearResponse
} from '../types';
import { dartaService, inboundService, masterService } from '../services/apiServices';

interface UnifiedDocumentIntakeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialFile?: File | null;
  initialInboundDoc?: InboundDocument | null;
  intakeSource?: 'CANON_SCANNER' | 'RAW_UPLOAD' | 'SMTP_EMAIL';
}

export const UnifiedDocumentIntakeModal: React.FC<UnifiedDocumentIntakeModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialFile,
  initialInboundDoc,
  intakeSource = 'RAW_UPLOAD'
}) => {
  // Document state
  const [activeFile, setActiveFile] = useState<File | null>(initialFile || null);
  const [inboundDoc, setInboundDoc] = useState<InboundDocument | null>(initialInboundDoc || null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string>('');

  // Master Data
  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);
  const [officers, setOfficers] = useState<OfficerResponse[]>([]);
  const [financialYears, setFinancialYears] = useState<FinancialYearResponse[]>([]);

  // Form State
  const [sender, setSender] = useState('');
  const [senderEmail, setSenderEmail] = useState('');
  const [senderContact, setSenderContact] = useState('');
  const [dartaDate, setDartaDate] = useState(new Date().toISOString().split('T')[0]);
  const [dartaDateBs, setDartaDateBs] = useState('');
  const [financialYear, setFinancialYear] = useState<number>(1);
  const [topic, setTopic] = useState('');
  const [receiverDepartment, setReceiverDepartment] = useState<number | undefined>(undefined);
  const [receiverOfficer, setReceiverOfficer] = useState<number | undefined>(undefined);

  // Parsing & Confidence State
  const [isParsing, setIsParsing] = useState(false);
  const [parsedResults, setParsedResults] = useState<ParsedCandidateFields | null>(null);
  const [autoFilledFields, setAutoFilledFields] = useState<Set<string>>(new Set());
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchMasterData();
  }, []);

  useEffect(() => {
    if (initialFile) {
      setActiveFile(initialFile);
      const url = URL.createObjectURL(initialFile);
      setFilePreviewUrl(url);
      // Auto-trigger parsing attempt with high-threshold evaluation
      handleAutoParse(initialFile);
      return () => URL.revokeObjectURL(url);
    } else if (initialInboundDoc) {
      setInboundDoc(initialInboundDoc);
      if (initialInboundDoc.parsed_data) {
        applyParsedFields(initialInboundDoc.parsed_data);
      }
    }
  }, [initialFile, initialInboundDoc]);

  const fetchMasterData = async () => {
    try {
      const [deptRes, offiRes, fyRes] = await Promise.all([
        masterService.getDepartments().catch(() => []),
        masterService.getOfficers().catch(() => []),
        masterService.getFinancialYears().catch(() => []),
      ]);
      setDepartments(deptRes);
      setOfficers(offiRes);
      setFinancialYears(fyRes);
      if (fyRes.length > 0) setFinancialYear(fyRes[0].id);
    } catch (e) {
      console.error('Failed to load master data:', e);
    }
  };

  const applyParsedFields = (candidate: ParsedCandidateFields) => {
    setParsedResults(candidate);
    const filled = new Set<string>();

    if (candidate.sender) {
      setSender(candidate.sender);
      filled.add('sender');
    }
    if (candidate.sender_email) {
      setSenderEmail(candidate.sender_email);
      filled.add('sender_email');
    }
    if (candidate.sender_contact_number) {
      setSenderContact(candidate.sender_contact_number);
      filled.add('sender_contact_number');
    }
    if (candidate.darta_date) {
      setDartaDate(candidate.darta_date);
      filled.add('darta_date');
    }
    if (candidate.darta_date_bs) {
      setDartaDateBs(candidate.darta_date_bs);
      filled.add('darta_date_bs');
    }
    if (candidate.financial_year) {
      setFinancialYear(candidate.financial_year);
      filled.add('financial_year');
    }
    if (candidate.topic) {
      setTopic(candidate.topic);
      filled.add('topic');
    }
    if (candidate.suggested_department_id) {
      setReceiverDepartment(candidate.suggested_department_id);
      filled.add('receiver_department');
    }
    if (candidate.suggested_officer_id) {
      setReceiverOfficer(candidate.suggested_officer_id);
      filled.add('receiver_officer');
    }

    setAutoFilledFields(filled);
  };

  const handleAutoParse = async (fileToParse?: File) => {
    const target = fileToParse || activeFile;
    if (!target && !inboundDoc) {
      alert('No document attached to parse.');
      return;
    }

    setIsParsing(true);
    try {
      if (inboundDoc) {
        const updated = await inboundService.parse(inboundDoc.id);
        if (updated.parsed_data) {
          applyParsedFields(updated.parsed_data);
        }
      } else if (target) {
        const candidate = await inboundService.parseFile(target);
        applyParsedFields(candidate);
      }
    } catch (err) {
      console.error('Document auto-parsing failed:', err);
      alert('Could not auto-parse document. You can proceed by filling the fields manually.');
    } finally {
      setIsParsing(false);
    }
  };

  const handleSubmitRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFile && !inboundDoc) {
      alert('Please attach or scan a document.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (inboundDoc) {
        await inboundService.convertToDarta(inboundDoc.id, {
          sender,
          sender_email: senderEmail,
          sender_contact_number: senderContact || undefined,
          darta_date: dartaDate,
          darta_date_bs: dartaDateBs || undefined,
          financial_year: financialYear,
          topic,
          receiver_department: receiverDepartment,
          receiver_officer: receiverOfficer,
        });
      } else if (activeFile) {
        const formData = new FormData();
        formData.append('sender', sender);
        formData.append('sender_email', senderEmail);
        if (senderContact) formData.append('sender_contact_number', senderContact);
        formData.append('darta_date', dartaDate);
        if (dartaDateBs) formData.append('darta_date_bs', dartaDateBs);
        formData.append('financial_year', financialYear.toString());
        formData.append('topic', topic);
        if (receiverDepartment) formData.append('receiver_department', receiverDepartment.toString());
        if (receiverOfficer) formData.append('receiver_officer', receiverOfficer.toString());
        formData.append('file', activeFile);

        await dartaService.create(formData);
      }

      alert('Document verified & registered into Darta successfully!');
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Registration failed:', err);
      alert(err.response?.data?.detail || 'Failed to register document.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const sourceBadge = () => {
    if (intakeSource === 'CANON_SCANNER') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', backgroundColor: '#e0f2fe', color: '#0369a1', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          <Printer size={13} /> Scanned from Canon Scanner
        </span>
      );
    }
    if (intakeSource === 'SMTP_EMAIL') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', backgroundColor: '#fef3c7', color: '#b45309', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          <Mail size={13} /> Inbound SMTP Email Attachment
        </span>
      );
    }
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', backgroundColor: '#f1f5f9', color: '#475569', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
        <Upload size={13} /> Uploaded Raw PDF / Document
      </span>
    );
  };

  const confidenceScore = parsedResults?.confidence_score ?? 0;
  const isHighConfidence = parsedResults?.parsing_status === 'PASSED_THRESHOLD';

  return (
    <div className="modal-overlay" style={{ zIndex: 1100 }}>
      <div className="modal-content modal-xl" style={{ maxWidth: '1200px', maxHeight: '94vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div className="modal-header" style={{ borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h3 className="modal-title" style={{ fontSize: '1.2rem', fontWeight: 800, color: '#003b73' }}>
                Document Intake & Auto-Fill Verification
              </h3>
              {sourceBadge()}
            </div>
            <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
              Verify auto-parsed candidate values against the scanned document preview, or edit fields manually.
            </p>
          </div>
          <button onClick={onClose} className="close-btn"><X size={20} /></button>
        </div>

        {/* Confidence & Auto-Parse Status Banner */}
        {parsedResults && (
          <div style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: isHighConfidence ? '#f0fdf4' : '#fffbeb',
            borderBottom: `1px solid ${isHighConfidence ? '#bbf7d0' : '#fde68a'}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              {isHighConfidence ? (
                <CheckCircle size={18} color="#16a34a" />
              ) : (
                <AlertTriangle size={18} color="#d97706" />
              )}
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: isHighConfidence ? '#15803d' : '#92400e' }}>
                {isHighConfidence ? 'Auto-Parse Passed High Threshold (≥ 80%)' : 'Requires Human Verification (< 80% Confidence)'}
              </span>
              <span style={{ fontSize: '0.75rem', backgroundColor: isHighConfidence ? '#dcfce7' : '#fef3c7', color: isHighConfidence ? '#166534' : '#b45309', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700 }}>
                Score: {Math.round(confidenceScore * 100)}%
              </span>
            </div>

            <button
              type="button"
              onClick={() => handleAutoParse()}
              disabled={isParsing}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: '0.75rem' }}
            >
              <RefreshCw size={13} className={isParsing ? 'animate-spin' : ''} />
              Re-run Parsing
            </button>
          </div>
        )}

        {/* Modal Split View Body */}
        <div className="modal-body" style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'grid', gridTemplateColumns: '45% 55%', gap: '1.5rem' }}>
          {/* Left Pane: Document Preview */}
          <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column', color: '#ffffff', minHeight: '480px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#38bdf8' }}>
                <Eye size={16} /> Document Attachment Preview
              </span>
              <span style={{ fontSize: '0.725rem', color: '#94a3b8' }}>
                {activeFile?.name || inboundDoc?.file_name || 'Document'}
              </span>
            </div>

            <div style={{ flex: 1, backgroundColor: '#0f172a', borderRadius: '8px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              {filePreviewUrl ? (
                <img
                  src={filePreviewUrl}
                  alt="Scanned Document Preview"
                  style={{ maxWidth: '100%', maxHeight: '440px', objectFit: 'contain' }}
                />
              ) : inboundDoc ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                  <FileText size={48} color="#38bdf8" style={{ margin: '0 auto 0.75rem auto' }} />
                  <p style={{ fontSize: '0.9rem', color: '#e2e8f0', fontWeight: 600 }}>{inboundDoc.file_name}</p>
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>Inbound SMTP Email Attachment</p>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#64748b' }}>
                  <FileText size={40} style={{ margin: '0 auto 0.5rem auto' }} />
                  <p>No document attached</p>
                </div>
              )}
            </div>

              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => handleAutoParse()}
                  disabled={isParsing}
                  className="btn btn-accent btn-sm"
                  style={{ width: '100%' }}
                >
                  {isParsing ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" /> Scanning & Parsing...
                    </>
                  ) : (
                    <>
                      <Sparkles size={14} /> ⚡ Auto-Parse Document & Fill Form
                    </>
                  )}
                </button>
              </div>
          </div>

          {/* Right Pane: Auto-Fill Form */}
          <form onSubmit={handleSubmitRegistration} style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#003b73' }}>
                Darta Registration Fields
              </h4>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                Fields highlighted with <span style={{ color: '#0284c7', fontWeight: 700 }}>•</span> are auto-detected
              </span>
            </div>

            {/* Sender & Contact Row */}
            <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="form-group">
                <label style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Sender Organization / Name *</span>
                  {autoFilledFields.has('sender') && (
                    <span style={{ color: '#0284c7', fontSize: '0.7rem', fontWeight: 600 }}>Auto-detected</span>
                  )}
                </label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Ministry of Communications"
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  style={{ borderColor: autoFilledFields.has('sender') ? '#38bdf8' : undefined }}
                />
              </div>

              <div className="form-group">
                <label style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Sender Email *</span>
                  {autoFilledFields.has('sender_email') && (
                    <span style={{ color: '#0284c7', fontSize: '0.7rem', fontWeight: 600 }}>Auto-detected</span>
                  )}
                </label>
                <input
                  type="email"
                  required
                  className="form-control"
                  placeholder="sender@domain.np"
                  value={senderEmail}
                  onChange={(e) => setSenderEmail(e.target.value)}
                  style={{ borderColor: autoFilledFields.has('sender_email') ? '#38bdf8' : undefined }}
                />
              </div>
            </div>

            {/* Dates & Financial Year Row */}
            <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
              <div className="form-group">
                <label>Darta Date (AD) *</label>
                <input
                  type="date"
                  required
                  className="form-control"
                  value={dartaDate}
                  onChange={(e) => setDartaDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Darta Date (BS)</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="YYYY-MM-DD (e.g. 2081-05-09)"
                  value={dartaDateBs}
                  onChange={(e) => setDartaDateBs(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Financial Year *</label>
                <select
                  className="form-control"
                  value={financialYear}
                  onChange={(e) => setFinancialYear(Number(e.target.value))}
                >
                  {financialYears.map((fy) => (
                    <option key={fy.id} value={fy.id}>{fy.financial_year}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Letter Subject / Topic */}
            <div className="form-group">
              <label style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Letter Topic / Subject *</span>
                {autoFilledFields.has('topic') && (
                  <span style={{ color: '#0284c7', fontSize: '0.7rem', fontWeight: 600 }}>Auto-detected</span>
                )}
              </label>
              <textarea
                rows={2}
                required
                className="form-control"
                placeholder="Enter letter subject or key summary..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                style={{ borderColor: autoFilledFields.has('topic') ? '#38bdf8' : undefined }}
              />
            </div>

            {/* Target Department & Officer Row */}
            <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="form-group">
                <label style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Target Department</span>
                  {autoFilledFields.has('receiver_department') && (
                    <span style={{ color: '#0284c7', fontSize: '0.7rem', fontWeight: 600 }}>Suggested</span>
                  )}
                </label>
                <select
                  className="form-control"
                  value={receiverDepartment || ''}
                  onChange={(e) => setReceiverDepartment(e.target.value ? Number(e.target.value) : undefined)}
                  style={{ borderColor: autoFilledFields.has('receiver_department') ? '#38bdf8' : undefined }}
                >
                  <option value="">-- Select Department --</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Target Officer</label>
                <select
                  className="form-control"
                  value={receiverOfficer || ''}
                  onChange={(e) => setReceiverOfficer(e.target.value ? Number(e.target.value) : undefined)}
                >
                  <option value="">-- Select Officer --</option>
                  {officers.map((offi) => (
                    <option key={offi.id} value={offi.id}>{offi.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Footer Buttons */}
            <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" disabled={isSubmitting} className="btn btn-primary" style={{ minWidth: '180px' }}>
                {isSubmitting ? 'Registering...' : 'Verify & Register Darta'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
