import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Plus,
  Search,
  Eye,
  FileSpreadsheet,
  X,
  Printer,
  Upload,
  Sparkles
} from 'lucide-react';
import { chalanService, masterService, systemService } from '../services/apiServices';
import { ChalanResponse, DepartmentResponse, OfficerResponse } from '../types';
import { OCRViewerModal } from '../components/OCRViewerModal';
import { ForwardingModal } from '../components/ForwardingModal';
import { DocumentScannerModal } from '../components/DocumentScannerModal';

export const ChalanPage: React.FC = () => {
  const [chalanList, setChalanList] = useState<ChalanResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchTopic, setSearchTopic] = useState('');
  const [searchReceiver, setSearchReceiver] = useState('');
  const [searchOcrKeyword, setSearchOcrKeyword] = useState('');
  const [fromDateBs, setFromDateBs] = useState('');
  const [toDateBs, setToDateBs] = useState('');

  // Master Data
  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);
  const [officers, setOfficers] = useState<OfficerResponse[]>([]);

  // Modals
  const [isScannerModalOpen, setIsScannerModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedChalanForOcr, setSelectedChalanForOcr] = useState<ChalanResponse | null>(null);
  const [selectedChalanForForwarding, setSelectedChalanForForwarding] = useState<ChalanResponse | null>(null);

  // Form State
  const [newSenderEmail, setNewSenderEmail] = useState('');
  const [newReceiver, setNewReceiver] = useState('');
  const [newReceiverEmail, setNewReceiverEmail] = useState('');
  const [newReceiverContact, setNewReceiverContact] = useState('');
  const [newChalanDate, setNewChalanDate] = useState(new Date().toISOString().split('T')[0]);
  const [newChalanDateBs, setNewChalanDateBs] = useState('');
  const [newTopic, setNewTopic] = useState('');
  const [newSenderDepartment, setNewSenderDepartment] = useState<number | undefined>(undefined);
  const [newSenderOfficer, setNewSenderOfficer] = useState<number | undefined>(undefined);
  const [newFile, setNewFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const rawFileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchChalanList();
    fetchMasterData();
  }, []);

  const fetchChalanList = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (searchTopic) params.topic = searchTopic;
      if (searchReceiver) params.receiver = searchReceiver;
      if (searchOcrKeyword) params.ocr_keyword = searchOcrKeyword;
      if (fromDateBs) params.from_date_bs = fromDateBs;
      if (toDateBs) params.to_date_bs = toDateBs;

      const data = await chalanService.search(params);
      setChalanList(data);
    } catch (e) {
      console.error('Failed to fetch Chalan documents:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [deptRes, offiRes] = await Promise.all([
        masterService.getDepartments().catch(() => []),
        masterService.getOfficers().catch(() => []),
      ]);
      setDepartments(deptRes);
      setOfficers(offiRes);
    } catch (e) {
      console.error('Failed to fetch master data:', e);
    }
  };

  const handleScanCompleted = (scannedFile: File) => {
    setNewFile(scannedFile);
    setIsScannerModalOpen(false);
    setIsCreateModalOpen(true);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFile) {
      alert('Please select or scan a document file to attach.');
      return;
    }

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('sender_email', newSenderEmail);
      formData.append('receiver', newReceiver);
      formData.append('receiver_email', newReceiverEmail);
      if (newReceiverContact) formData.append('receiver_contact_number', newReceiverContact);
      formData.append('chalan_date', newChalanDate);
      if (newChalanDateBs) formData.append('chalan_date_bs', newChalanDateBs);
      formData.append('topic', newTopic);
      if (newSenderDepartment) formData.append('sender_department', newSenderDepartment.toString());
      if (newSenderOfficer) formData.append('sender_officer', newSenderOfficer.toString());
      formData.append('file', newFile);

      await chalanService.create(formData);
      alert('Chalan dispatch registered successfully!');
      setIsCreateModalOpen(false);
      resetForm();
      fetchChalanList();
    } catch (err: any) {
      console.error('Failed to register Chalan:', err);
      alert(err.response?.data?.detail || 'Failed to register Chalan dispatch.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setNewSenderEmail('');
    setNewReceiver('');
    setNewReceiverEmail('');
    setNewReceiverContact('');
    setNewChalanDate(new Date().toISOString().split('T')[0]);
    setNewChalanDateBs('');
    setNewTopic('');
    setNewSenderDepartment(undefined);
    setNewSenderOfficer(undefined);
    setNewFile(null);
  };

  const handleExportCsv = async () => {
    try {
      await systemService.exportChalanCsv({
        topic: searchTopic || undefined,
        receiver: searchReceiver || undefined,
        ocr_keyword: searchOcrKeyword || undefined,
        from_date_bs: fromDateBs || undefined,
        to_date_bs: toDateBs || undefined,
      });
    } catch (err) {
      console.error('Failed to export Chalan CSV:', err);
      alert('Failed to export Chalan CSV file.');
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
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            setNewFile(e.target.files[0]);
            setIsCreateModalOpen(true);
          }
          e.target.value = '';
        }}
      />

      {/* Top Header Card */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#00a8cc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Send size={24} color="#00a8cc" /> Chalan (Outgoing Dispatch) Management
            </h2>
            <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
              Issue outgoing dispatch numbers, scan dispatch drafts with Canon scanners, run OCR text extraction, and track dispatch history.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            <button onClick={handleExportCsv} className="btn btn-secondary">
              <FileSpreadsheet size={16} /> Export CSV
            </button>
            <button
              onClick={() => rawFileInputRef.current?.click()}
              className="btn btn-secondary"
            >
              <Upload size={16} color="#00a8cc" /> Upload Dispatch Letter
            </button>
            <button
              onClick={() => setIsScannerModalOpen(true)}
              className="btn btn-accent"
              title="Scan outgoing letter from Canon hardware scanner"
            >
              <Printer size={16} /> Scan from Canon Scanner
            </button>
            <button onClick={() => setIsCreateModalOpen(true)} className="btn btn-primary">
              <Plus size={16} /> Issue New Chalan
            </button>
          </div>
        </div>
      </div>

      {/* Filter Card */}
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
            <label>Receiver Name / Email</label>
            <input
              type="text"
              className="form-control"
              placeholder="Filter by receiver..."
              value={searchReceiver}
              onChange={(e) => setSearchReceiver(e.target.value)}
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
            <button onClick={fetchChalanList} className="btn btn-accent" style={{ height: '38px' }}>
              <Search size={16} /> Filter Results
            </button>
          </div>
        </div>
      </div>

      {/* Chalan Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Chalan #</th>
                <th>Receiver</th>
                <th>Topic</th>
                <th>Date (AD / BS)</th>
                <th>Sender Department</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    Loading Chalan dispatch records...
                  </td>
                </tr>
              ) : chalanList.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                    No Chalan records found. Click "Issue New Chalan" or "Scan from Canon Scanner" to register a dispatch.
                  </td>
                </tr>
              ) : (
                chalanList.map((item) => (
                  <tr key={item.id || item.chalan_id}>
                    <td><strong style={{ color: '#00a8cc' }}>#{item.chalan_id}</strong></td>
                    <td>
                      <div><strong>{item.receiver?.name || 'N/A'}</strong></div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.receiver?.email || ''}</div>
                    </td>
                    <td><strong>{item.topic}</strong></td>
                    <td>
                      {item.chalan_date}
                      {item.chalan_date_bs && <div style={{ fontSize: '0.725rem', color: '#64748b' }}>{item.chalan_date_bs} BS</div>}
                    </td>
                    <td>
                      <div style={{ fontSize: '0.825rem' }}>{item.sender?.department || 'General'}</div>
                      <div style={{ fontSize: '0.725rem', color: '#64748b' }}>{item.sender?.officer || ''}</div>
                    </td>
                    <td><span className="badge badge-registered">{item.status || 'REGISTERED'}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        <button
                          onClick={() => setSelectedChalanForOcr(item)}
                          className="btn btn-secondary btn-sm"
                          title="View OCR & File Details"
                        >
                          <Eye size={14} color="#003b73" /> OCR
                        </button>
                        <button
                          onClick={() => setSelectedChalanForForwarding(item)}
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

      {/* Canon Scanner Modal */}
      {isScannerModalOpen && (
        <DocumentScannerModal
          isOpen={isScannerModalOpen}
          onClose={() => setIsScannerModalOpen(false)}
          onScanComplete={handleScanCompleted}
          initialTitle="Canon Scanner: Outgoing Dispatch Letter"
        />
      )}

      {/* New Chalan Modal */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content modal-lg">
            <div className="modal-header">
              <h3 className="modal-title">Issue New Chalan (Outgoing Dispatch)</h3>
              <button onClick={() => setIsCreateModalOpen(false)} className="close-btn"><X size={20} /></button>
            </div>
            <form onSubmit={handleCreateSubmit}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Receiver Organization / Name *</label>
                    <input
                      type="text"
                      required
                      className="form-control"
                      placeholder="e.g. Nepal Rastra Bank"
                      value={newReceiver}
                      onChange={(e) => setNewReceiver(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Receiver Email *</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      placeholder="receiver@nrb.org.np"
                      value={newReceiverEmail}
                      onChange={(e) => setNewReceiverEmail(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Contact Number</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="+977-98xxxxxxxx"
                      value={newReceiverContact}
                      onChange={(e) => setNewReceiverContact(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label>Sender Email *</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      placeholder="dispatch@ntc.net.np"
                      value={newSenderEmail}
                      onChange={(e) => setNewSenderEmail(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Chalan Date (AD) *</label>
                    <input
                      type="date"
                      required
                      className="form-control"
                      value={newChalanDate}
                      onChange={(e) => setNewChalanDate(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Chalan Date (BS)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="YYYY-MM-DD (e.g. 2081-04-20)"
                      value={newChalanDateBs}
                      onChange={(e) => setNewChalanDateBs(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Letter Subject / Dispatch Topic *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="Enter dispatch topic..."
                    value={newTopic}
                    onChange={(e) => setNewTopic(e.target.value)}
                  />
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label>Sender Department</label>
                    <select
                      className="form-control"
                      value={newSenderDepartment || ''}
                      onChange={(e) => setNewSenderDepartment(e.target.value ? Number(e.target.value) : undefined)}
                    >
                      <option value="">-- Select Department --</option>
                      {departments.map((dept) => (
                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Sender Officer</label>
                    <select
                      className="form-control"
                      value={newSenderOfficer || ''}
                      onChange={(e) => setNewSenderOfficer(e.target.value ? Number(e.target.value) : undefined)}
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
                  {newFile ? (
                    <div style={{
                      padding: '0.65rem 0.85rem',
                      backgroundColor: '#f0f9ff',
                      border: '1px solid #bae6fd',
                      borderRadius: '8px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span style={{ fontSize: '0.825rem', fontWeight: 600, color: '#0369a1' }}>
                        📎 {newFile.name} ({(newFile.size / 1024).toFixed(1)} KB)
                      </span>
                      <button
                        type="button"
                        onClick={() => setNewFile(null)}
                        className="btn btn-secondary btn-sm"
                        style={{ fontSize: '0.725rem' }}
                      >
                        Remove / Replace
                      </button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="file"
                        required
                        accept=".pdf,.png,.jpg,.jpeg"
                        className="form-control"
                        onChange={(e) => setNewFile(e.target.files ? e.target.files[0] : null)}
                      />
                      <button
                        type="button"
                        onClick={() => setIsScannerModalOpen(true)}
                        className="btn btn-secondary"
                        style={{ whiteSpace: 'nowrap' }}
                      >
                        <Printer size={16} /> Scan
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => setIsCreateModalOpen(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  {isSubmitting ? 'Registering...' : 'Dispatch Chalan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* OCR Viewer Modal */}
      {selectedChalanForOcr && (
        <OCRViewerModal
          isOpen={!!selectedChalanForOcr}
          onClose={() => setSelectedChalanForOcr(null)}
          documentType="CHALAN"
          documentData={selectedChalanForOcr}
          onOcrUpdated={fetchChalanList}
        />
      )}

      {/* Forwarding Modal */}
      {selectedChalanForForwarding && (
        <ForwardingModal
          isOpen={!!selectedChalanForForwarding}
          onClose={() => setSelectedChalanForForwarding(null)}
          documentType="CHALAN"
          documentId={selectedChalanForForwarding.id || selectedChalanForForwarding.chalan_id}
          onForwardedSuccess={fetchChalanList}
        />
      )}
    </div>
  );
};
