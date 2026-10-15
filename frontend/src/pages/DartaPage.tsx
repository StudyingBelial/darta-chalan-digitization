import React, { useState, useEffect, useRef } from 'react';
import {
  Inbox,
  Plus,
  Search,
  Download,
  Eye,
  Send,
  Cpu,
  FileSpreadsheet,
  Filter,
  X,
  Printer,
  Upload,
  Sparkles
} from 'lucide-react';
import { dartaService, masterService, systemService } from '../services/apiServices';
import { DartaResponse, DepartmentResponse, OfficerResponse, FinancialYearResponse } from '../types';
import { OCRViewerModal } from '../components/OCRViewerModal';
import { ForwardingModal } from '../components/ForwardingModal';
import { DocumentScannerModal } from '../components/DocumentScannerModal';
import { UnifiedDocumentIntakeModal } from '../components/UnifiedDocumentIntakeModal';

export const DartaPage: React.FC = () => {
  const [dartaList, setDartaList] = useState<DartaResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [searchTopic, setSearchTopic] = useState('');
  const [searchSender, setSearchSender] = useState('');
  const [searchOcrKeyword, setSearchOcrKeyword] = useState('');
  const [fromDateBs, setFromDateBs] = useState('');
  const [toDateBs, setToDateBs] = useState('');
  const [selectedFy, setSelectedFy] = useState<number | undefined>(undefined);

  // Master Data state for modal
  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);
  const [officers, setOfficers] = useState<OfficerResponse[]>([]);
  const [financialYears, setFinancialYears] = useState<FinancialYearResponse[]>([]);

  // Modals state
  const [isScannerModalOpen, setIsScannerModalOpen] = useState(false);
  const [isIntakeModalOpen, setIsIntakeModalOpen] = useState(false);
  const [intakeFile, setIntakeFile] = useState<File | null>(null);
  const [intakeSource, setIntakeSource] = useState<'CANON_SCANNER' | 'RAW_UPLOAD'>('CANON_SCANNER');

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedDartaForOcr, setSelectedDartaForOcr] = useState<DartaResponse | null>(null);
  const [selectedDartaForForwarding, setSelectedDartaForForwarding] = useState<DartaResponse | null>(null);

  // Hidden file input for direct raw upload
  const rawFileInputRef = useRef<HTMLInputElement>(null);

  // Create Form State (Classic modal fallback)
  const [newSender, setNewSender] = useState('');
  const [newSenderEmail, setNewSenderEmail] = useState('');
  const [newSenderContact, setNewSenderContact] = useState('');
  const [newDartaDate, setNewDartaDate] = useState(new Date().toISOString().split('T')[0]);
  const [newDartaDateBs, setNewDartaDateBs] = useState('');
  const [newFinancialYear, setNewFinancialYear] = useState<number>(1);
  const [newTopic, setNewTopic] = useState('');
  const [newReceiverDepartment, setNewReceiverDepartment] = useState<number | undefined>(undefined);
  const [newReceiverOfficer, setNewReceiverOfficer] = useState<number | undefined>(undefined);
  const [newFile, setNewFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchDartaList();
    fetchMasterData();
  }, []);

  const fetchDartaList = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (searchTopic) params.topic = searchTopic;
      if (searchSender) params.sender = searchSender;
      if (searchOcrKeyword) params.ocr_keyword = searchOcrKeyword;
      if (fromDateBs) params.from_date_bs = fromDateBs;
      if (toDateBs) params.to_date_bs = toDateBs;
      if (selectedFy) params.financial_year = selectedFy;

      const data = await dartaService.search(params);
      setDartaList(data);
    } catch (e) {
      console.error('Failed to fetch Darta documents:', e);
    } finally {
      setLoading(false);
    }
  };

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
      if (fyRes.length > 0) setNewFinancialYear(fyRes[0].id);
    } catch (e) {
      console.error('Failed to fetch master data:', e);
    }
  };

  const handleScanCompleted = (file: File) => {
    setIntakeFile(file);
    setIntakeSource('CANON_SCANNER');
    setIsScannerModalOpen(false);
    setIsIntakeModalOpen(true);
  };

  const handleRawFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setIntakeFile(file);
      setIntakeSource('RAW_UPLOAD');
      setIsIntakeModalOpen(true);
    }
    // reset input so same file can be chosen again
    e.target.value = '';
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFile) {
      alert('Please select a document file to attach.');
      return;
    }

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('sender', newSender);
      formData.append('sender_email', newSenderEmail);
      if (newSenderContact) formData.append('sender_contact_number', newSenderContact);
      formData.append('darta_date', newDartaDate);
      if (newDartaDateBs) formData.append('darta_date_bs', newDartaDateBs);
      formData.append('financial_year', newFinancialYear.toString());
      formData.append('topic', newTopic);
      if (newReceiverDepartment) formData.append('receiver_department', newReceiverDepartment.toString());
      if (newReceiverOfficer) formData.append('receiver_officer', newReceiverOfficer.toString());
      formData.append('file', newFile);

      await dartaService.create(formData);
      alert('Darta registered successfully!');
      setIsCreateModalOpen(false);
      resetForm();
      fetchDartaList();
    } catch (err: any) {
      console.error('Failed to register Darta:', err);
      alert(err.response?.data?.detail || 'Failed to register Darta document.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setNewSender('');
    setNewSenderEmail('');
    setNewSenderContact('');
    setNewDartaDate(new Date().toISOString().split('T')[0]);
    setNewDartaDateBs('');
    setNewTopic('');
    setNewReceiverDepartment(undefined);
    setNewReceiverOfficer(undefined);
    setNewFile(null);
  };

  const handleExportCsv = async () => {
    try {
      await systemService.exportDartaCsv({
        topic: searchTopic || undefined,
        sender: searchSender || undefined,
        ocr_keyword: searchOcrKeyword || undefined,
        from_date_bs: fromDateBs || undefined,
        to_date_bs: toDateBs || undefined,
      });
    } catch (err) {
      console.error('Failed to export Darta CSV:', err);
      alert('Failed to export Darta CSV file.');
    }
  };

  return (
    <div>
      {/* Hidden File Input for Raw PDF Upload */}
      <input
        type="file"
        ref={rawFileInputRef}
        accept=".pdf,.png,.jpg,.jpeg"
        style={{ display: 'none' }}
        onChange={handleRawFileSelected}
      />

      {/* Top Action Header */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Inbox size={24} color="#003b73" /> Darta (Incoming Letters) Management
            </h2>
            <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
              Scan directly from Canon hardware, upload raw PDFs, auto-parse with high confidence, and register official entries.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            <button onClick={handleExportCsv} className="btn btn-secondary">
              <FileSpreadsheet size={16} /> Export CSV
            </button>
            <button
              onClick={() => rawFileInputRef.current?.click()}
              className="btn btn-secondary"
              title="Upload PDF and auto-parse form fields"
            >
              <Upload size={16} color="#00a8cc" /> Upload & Auto-Parse
            </button>
            <button
              onClick={() => setIsScannerModalOpen(true)}
              className="btn btn-accent"
              title="Acquire document scan from Canon or connected hardware scanner"
            >
              <Printer size={16} /> Scan from Canon Scanner
            </button>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn btn-primary"
            >
              <Plus size={16} /> Quick Manual Register
            </button>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.25rem' }}>
        <div className="form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Topic / Subject</label>
            <input
              type="text"
              className="form-control"
              placeholder="Filter by topic..."
              value={searchTopic}
              onChange={(e) => setSearchTopic(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Sender Name / Email</label>
            <input
              type="text"
              className="form-control"
              placeholder="Filter by sender..."
              value={searchSender}
              onChange={(e) => setSearchSender(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>From Date (B.S.)</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. 2081-01-01"
              value={fromDateBs}
              onChange={(e) => setFromDateBs(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>To Date (B.S.)</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. 2081-12-30"
              value={toDateBs}
              onChange={(e) => setToDateBs(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>OCR Keyword</label>
            <input
              type="text"
              className="form-control"
              placeholder="Search inside OCR..."
              value={searchOcrKeyword}
              onChange={(e) => setSearchOcrKeyword(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <button onClick={fetchDartaList} className="btn btn-accent" style={{ height: '38px' }}>
              <Search size={16} /> Filter Results
            </button>
          </div>
        </div>
      </div>

      {/* Darta Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Darta #</th>
                <th>Sender</th>
                <th>Topic</th>
                <th>Date (AD / BS)</th>
                <th>Department / Officer</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    Loading Darta register records...
                  </td>
                </tr>
              ) : dartaList.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                    No Darta records found. Click "Scan from Canon Scanner" or "Upload & Auto-Parse" to add one.
                  </td>
                </tr>
              ) : (
                dartaList.map((item) => (
                  <tr key={item.id || item.darta_id}>
                    <td><strong style={{ color: '#003b73' }}>#{item.darta_id}</strong></td>
                    <td>
                      <div><strong>{item.sender}</strong></div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.sender_email}</div>
                    </td>
                    <td><strong>{item.topic}</strong></td>
                    <td>
                      {item.darta_date}
                      {item.darta_date_bs && <div style={{ fontSize: '0.725rem', color: '#64748b' }}>{item.darta_date_bs} BS</div>}
                    </td>
                    <td>
                      <div style={{ fontSize: '0.825rem' }}>{item.department?.receiver_department || 'Unassigned'}</div>
                      <div style={{ fontSize: '0.725rem', color: '#64748b' }}>{item.officer?.receiver_officer || ''}</div>
                    </td>
                    <td><span className="badge badge-registered">{item.status || 'REGISTERED'}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        <button
                          onClick={() => setSelectedDartaForOcr(item)}
                          className="btn btn-secondary btn-sm"
                          title="View OCR & File Details"
                        >
                          <Eye size={14} color="#003b73" /> OCR
                        </button>
                        <button
                          onClick={() => setSelectedDartaForForwarding(item)}
                          className="btn btn-secondary btn-sm"
                          title="Forward Document"
                        >
                          <Send size={14} color="#00a8cc" /> Forward
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Canon / Document Scanner Modal */}
      {isScannerModalOpen && (
        <DocumentScannerModal
          isOpen={isScannerModalOpen}
          onClose={() => setIsScannerModalOpen(false)}
          onScanComplete={handleScanCompleted}
          initialTitle="Canon Document Scanner Acquisition"
        />
      )}

      {/* Unified Document Intake & Auto-Fill Modal */}
      {isIntakeModalOpen && (
        <UnifiedDocumentIntakeModal
          isOpen={isIntakeModalOpen}
          onClose={() => setIsIntakeModalOpen(false)}
          onSuccess={fetchDartaList}
          initialFile={intakeFile}
          intakeSource={intakeSource}
        />
      )}

      {/* Classic New Darta Modal */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content modal-lg">
            <div className="modal-header">
              <h3 className="modal-title">Register New Darta (Manual Quick Form)</h3>
              <button onClick={() => setIsCreateModalOpen(false)} className="close-btn"><X size={20} /></button>
            </div>
            <form onSubmit={handleCreateSubmit}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Sender Name *</label>
                    <input
                      type="text"
                      required
                      className="form-control"
                      placeholder="e.g. Ministry of Communications"
                      value={newSender}
                      onChange={(e) => setNewSender(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Sender Email *</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      placeholder="sender@domain.np"
                      value={newSenderEmail}
                      onChange={(e) => setNewSenderEmail(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Contact Number</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="+977-98xxxxxxxx"
                      value={newSenderContact}
                      onChange={(e) => setNewSenderContact(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label>Darta Date (AD) *</label>
                    <input
                      type="date"
                      required
                      className="form-control"
                      value={newDartaDate}
                      onChange={(e) => setNewDartaDate(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Darta Date (BS Bikram Sambat)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="YYYY-MM-DD (e.g. 2081-04-20)"
                      value={newDartaDateBs}
                      onChange={(e) => setNewDartaDateBs(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Financial Year *</label>
                    <select
                      className="form-control"
                      value={newFinancialYear}
                      onChange={(e) => setNewFinancialYear(Number(e.target.value))}
                    >
                      {financialYears.map((fy) => (
                        <option key={fy.id} value={fy.id}>{fy.financial_year}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Letter Topic / Subject *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="Enter letter summary or subject..."
                    value={newTopic}
                    onChange={(e) => setNewTopic(e.target.value)}
                  />
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label>Target Receiver Department</label>
                    <select
                      className="form-control"
                      value={newReceiverDepartment || ''}
                      onChange={(e) => setNewReceiverDepartment(e.target.value ? Number(e.target.value) : undefined)}
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
                      value={newReceiverOfficer || ''}
                      onChange={(e) => setNewReceiverOfficer(e.target.value ? Number(e.target.value) : undefined)}
                    >
                      <option value="">-- Select Officer --</option>
                      {officers.map((offi) => (
                        <option key={offi.id} value={offi.id}>{offi.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group" style={{ marginTop: '0.5rem' }}>
                  <label>Document File Attachment (PDF / Image) *</label>
                  <input
                    type="file"
                    required
                    accept=".pdf,.png,.jpg,.jpeg"
                    className="form-control"
                    onChange={(e) => setNewFile(e.target.files ? e.target.files[0] : null)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => setIsCreateModalOpen(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  {isSubmitting ? 'Registering...' : 'Register Darta'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* OCR Viewer Modal */}
      {selectedDartaForOcr && (
        <OCRViewerModal
          isOpen={!!selectedDartaForOcr}
          onClose={() => setSelectedDartaForOcr(null)}
          documentType="DARTA"
          documentData={selectedDartaForOcr}
          onOcrUpdated={fetchDartaList}
        />
      )}

      {/* Forwarding Modal */}
      {selectedDartaForForwarding && (
        <ForwardingModal
          isOpen={!!selectedDartaForForwarding}
          onClose={() => setSelectedDartaForForwarding(null)}
          documentType="DARTA"
          documentId={selectedDartaForForwarding.id || selectedDartaForForwarding.darta_id}
          onForwardedSuccess={fetchDartaList}
        />
      )}
    </div>
  );
};
