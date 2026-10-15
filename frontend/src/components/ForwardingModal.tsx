import React, { useState, useEffect } from 'react';
import { X, Send, History, Building2, User, FileSpreadsheet } from 'lucide-react';
import { masterService, forwardingService } from '../services/apiServices';
import { OfficeResponse, DepartmentResponse, OfficerResponse, ForwardingResponse } from '../types';

interface ForwardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentType: 'DARTA' | 'CHALAN';
  documentId: number;
  onForwardedSuccess?: () => void;
}

export const ForwardingModal: React.FC<ForwardingModalProps> = ({
  isOpen,
  onClose,
  documentType,
  documentId,
  onForwardedSuccess,
}) => {
  const [offices, setOffices] = useState<OfficeResponse[]>([]);
  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);
  const [officers, setOfficers] = useState<OfficerResponse[]>([]);
  const [history, setHistory] = useState<ForwardingResponse[]>([]);

  const [selectedOffice, setSelectedOffice] = useState<number | undefined>(undefined);
  const [selectedDepartment, setSelectedDepartment] = useState<number | undefined>(undefined);
  const [selectedOfficer, setSelectedOfficer] = useState<number | undefined>(undefined);
  const [remarks, setRemarks] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'FORM' | 'HISTORY'>('FORM');

  useEffect(() => {
    if (isOpen && documentId) {
      loadMasterData();
      loadHistory();
    }
  }, [isOpen, documentId]);

  const loadMasterData = async () => {
    try {
      const [offRes, deptRes, offiRes] = await Promise.all([
        masterService.getOffices(),
        masterService.getDepartments(),
        masterService.getOfficers(),
      ]);
      setOffices(offRes);
      setDepartments(deptRes);
      setOfficers(offiRes);
    } catch (e) {
      console.error('Failed to load master data for forwarding:', e);
    }
  };

  const loadHistory = async () => {
    try {
      const hist = await forwardingService.getHistory(documentType, documentId);
      setHistory(hist);
    } catch (e) {
      console.error('Failed to load forwarding history:', e);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await forwardingService.create({
        document_type: documentType,
        document_id: documentId,
        forwarded_to_office: selectedOffice,
        forwarded_to_department: selectedDepartment,
        forwarded_to_officer: selectedOfficer,
        remarks,
      });
      setRemarks('');
      await loadHistory();
      if (onForwardedSuccess) onForwardedSuccess();
      alert('Document forwarded successfully!');
      onClose();
    } catch (err: any) {
      console.error('Failed to forward document:', err);
      alert(err.response?.data?.detail || 'Failed to forward document');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Send size={20} color="#003b73" />
            <h3 className="modal-title">Forward Document ({documentType} #{documentId})</h3>
          </div>
          <button onClick={onClose} className="close-btn"><X size={20} /></button>
        </div>

        <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0', padding: '0 1.5rem', backgroundColor: '#f8fafc' }}>
          <button
            onClick={() => setActiveTab('FORM')}
            style={{
              padding: '0.75rem 1rem',
              border: 'none',
              background: 'none',
              fontWeight: activeTab === 'FORM' ? 700 : 500,
              color: activeTab === 'FORM' ? '#003b73' : '#64748b',
              borderBottom: activeTab === 'FORM' ? '3px solid #003b73' : '3px solid transparent',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Forward Action
          </button>
          <button
            onClick={() => setActiveTab('HISTORY')}
            style={{
              padding: '0.75rem 1rem',
              border: 'none',
              background: 'none',
              fontWeight: activeTab === 'HISTORY' ? 700 : 500,
              color: activeTab === 'HISTORY' ? '#003b73' : '#64748b',
              borderBottom: activeTab === 'HISTORY' ? '3px solid #003b73' : '3px solid transparent',
              cursor: 'pointer',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <History size={14} /> History Trail ({history.length})
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'FORM' ? (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Target Office</label>
                <select
                  className="form-control"
                  value={selectedOffice || ''}
                  onChange={(e) => setSelectedOffice(e.target.value ? Number(e.target.value) : undefined)}
                >
                  <option value="">-- Select Office --</option>
                  {offices.map((off) => (
                    <option key={off.id} value={off.id}>{off.name} ({off.location})</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Target Department</label>
                <select
                  className="form-control"
                  value={selectedDepartment || ''}
                  onChange={(e) => setSelectedDepartment(e.target.value ? Number(e.target.value) : undefined)}
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
                  value={selectedOfficer || ''}
                  onChange={(e) => setSelectedOfficer(e.target.value ? Number(e.target.value) : undefined)}
                >
                  <option value="">-- Select Officer --</option>
                  {officers.map((offi) => (
                    <option key={offi.id} value={offi.id}>{offi.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Remarks / Instructions</label>
                <textarea
                  className="form-control"
                  rows={3}
                  placeholder="Enter dispatch notes, directives, or remarks..."
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                />
              </div>

              <div className="modal-footer" style={{ padding: '1rem 0 0 0', backgroundColor: 'transparent' }}>
                <button type="button" onClick={onClose} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  <Send size={16} /> {isSubmitting ? 'Forwarding...' : 'Confirm Forwarding'}
                </button>
              </div>
            </form>
          ) : (
            <div>
              {history.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#64748b', padding: '2rem 0' }}>
                  No forwarding history recorded for this document.
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {history.map((record) => (
                    <div
                      key={record.id}
                      style={{
                        padding: '0.85rem 1rem',
                        borderRadius: '8px',
                        backgroundColor: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderLeft: '4px solid #003b73'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem', fontSize: '0.8rem' }}>
                        <span style={{ fontWeight: 700, color: '#003b73' }}>
                          Forwarded by User #{record.forwarded_by_user}
                        </span>
                        <span style={{ color: '#64748b' }}>
                          {new Date(record.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: '#334155' }}>
                        <strong>Remarks:</strong> {record.remarks || 'No remarks provided.'}
                      </p>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem', display: 'flex', gap: '0.75rem' }}>
                        <span>Status: <strong style={{ color: '#10b981' }}>{record.status}</strong></span>
                        {record.forwarded_to_office && <span>Office ID: {record.forwarded_to_office}</span>}
                        {record.forwarded_to_department && <span>Dept ID: {record.forwarded_to_department}</span>}
                        {record.forwarded_to_officer && <span>Officer ID: {record.forwarded_to_officer}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
