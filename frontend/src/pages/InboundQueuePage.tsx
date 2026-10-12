import React, { useState, useEffect } from 'react';
import {
  Mail,
  Printer,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Eye,
  PlusCircle,
  Clock,
  Filter,
  Send,
  FileText
} from 'lucide-react';
import { InboundDocument } from '../types';
import { inboundService } from '../services/apiServices';
import { UnifiedDocumentIntakeModal } from '../components/UnifiedDocumentIntakeModal';

export const InboundQueuePage: React.FC = () => {
  const [documents, setDocuments] = useState<InboundDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [selectedDocForReview, setSelectedDocForReview] = useState<InboundDocument | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isSendingRealSMTP, setIsSendingRealSMTP] = useState(false);
  const [smtpStatus, setSmtpStatus] = useState<{
    running: boolean;
    host: string;
    port: number;
    messages_processed: number;
    last_message_at?: string;
    last_sender?: string;
    allowed_domains?: string[];
  } | null>(null);

  useEffect(() => {
    fetchInboundDocuments();
    fetchSMTPStatus();
  }, [statusFilter, sourceFilter]);

  const fetchSMTPStatus = async () => {
    try {
      const status = await inboundService.getSMTPStatus();
      setSmtpStatus(status);
    } catch (e) {
      console.warn('Could not fetch SMTP scanner status:', e);
    }
  };

  const fetchInboundDocuments = async () => {
    setLoading(true);
    try {
      const data = await inboundService.list({
        status: statusFilter || undefined,
        source: sourceFilter || undefined,
      });
      setDocuments(data);
    } catch (e) {
      console.error('Failed to fetch inbound documents:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRealSMTPScan = async () => {
    setIsSendingRealSMTP(true);
    try {
      const res = await inboundService.sendSMTPTestScan({
        sender_email: 'scanner.canon@ntc.net.np',
        sender_name: 'Canon imageRUNNER ADVANCE C3530i (Head Office)',
        subject: 'Official Scanned Dispatch - Network Rollout 2081/82',
        file_name: 'canon_scan_rollout_2081.pdf',
      });
      alert(res.message || 'Hardware scan received via SMTP socket successfully!');
      await fetchInboundDocuments();
      await fetchSMTPStatus();
    } catch (e: any) {
      console.error('Real SMTP scan delivery failed:', e);
      alert(e.response?.data?.detail || 'Failed to deliver scan via SMTP socket.');
    } finally {
      setIsSendingRealSMTP(false);
    }
  };

  const handleSimulateEmail = async () => {
    setIsSimulating(true);
    try {
      await inboundService.simulateEmail({
        sender_email: 'ministry.it@gov.np',
        sender_name: 'Ministry of Communications & IT',
        subject: 'Directives regarding Broadband Network Expansion Phase II',
        file_name: 'gov_directive_2081.pdf',
      });
      alert('Simulated inbound SMTP email received successfully! Check notification badge & queue.');
      fetchInboundDocuments();
      fetchSMTPStatus();
    } catch (e) {
      console.error('Simulation failed:', e);
      alert('Failed to simulate incoming email.');
    } finally {
      setIsSimulating(false);
    }
  };

  const renderStatusBadge = (doc: InboundDocument) => {
    if (doc.status === 'CONVERTED_TO_DARTA') {
      return <span className="badge badge-completed">CONVERTED (DARTA #{doc.converted_darta_id})</span>;
    }
    if (doc.parsing_status === 'PASSED_THRESHOLD') {
      return (
        <span style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
          <CheckCircle size={13} /> Auto-Parsed (≥80%)
        </span>
      );
    }
    return (
      <span style={{ backgroundColor: '#fef3c7', color: '#b45309', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
        <AlertTriangle size={13} /> Needs Human Review
      </span>
    );
  };

  return (
    <div>
      {/* Header Banner */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Mail size={24} color="#00a8cc" /> Inbound Mail & Hardware Scan Queue
            </h2>
            <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
              Real-time ingestion for Canon/MFP network scanners and inter-office emails. Auto-extracts fields with OCR confidence scoring before registering into Darta.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={handleRealSMTPScan}
              disabled={isSendingRealSMTP}
              className="btn btn-primary"
              title="Test real RFC 5321 ESMTP socket scan ingestion"
              style={{ backgroundColor: '#003b73', borderColor: '#003b73' }}
            >
              {isSendingRealSMTP ? <RefreshCw size={16} className="animate-spin" /> : <Printer size={16} />}
              <span>Trigger Hardware SMTP Scan</span>
            </button>
            <button
              onClick={handleSimulateEmail}
              disabled={isSimulating}
              className="btn btn-secondary"
              title="Simulate incoming SMTP email with PDF attachment"
            >
              {isSimulating ? <RefreshCw size={16} className="animate-spin" /> : <Mail size={16} color="#00a8cc" />}
              <span>Simulate Email</span>
            </button>
            <button onClick={() => { fetchInboundDocuments(); fetchSMTPStatus(); }} className="btn btn-secondary">
              <RefreshCw size={16} /> Refresh
            </button>
          </div>
        </div>

        {/* Live SMTP Scanner Telemetry Pill */}
        {smtpStatus && (
          <div style={{
            marginTop: '1rem',
            padding: '0.65rem 1rem',
            backgroundColor: smtpStatus.running ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${smtpStatus.running ? '#bbf7d0' : '#fecaca'}`,
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
            fontSize: '0.8rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: smtpStatus.running ? '#22c55e' : '#ef4444',
                display: 'inline-block',
                boxShadow: smtpStatus.running ? '0 0 8px #22c55e' : 'none'
              }} />
              <strong style={{ color: smtpStatus.running ? '#15803d' : '#b91c1c' }}>
                {smtpStatus.running ? 'ESMTP Scanner Receiver Active' : 'SMTP Scanner Inactive'}
              </strong>
              <span style={{ color: '#64748b' }}>
                Listening on <code>{smtpStatus.host}:{smtpStatus.port}</code>
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', color: '#475569' }}>
              <span>Total Ingested: <strong>{smtpStatus.messages_processed}</strong></span>
              {smtpStatus.last_message_at && (
                <span>Last Scan: <strong>{new Date(smtpStatus.last_message_at).toLocaleTimeString()}</strong> ({smtpStatus.last_sender})</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.25rem' }}>
        <div className="form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Registration Status</label>
            <select
              className="form-control"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="PENDING_REVIEW">Pending Review</option>
              <option value="PARSED">Parsed / Ready</option>
              <option value="CONVERTED_TO_DARTA">Converted to Darta</option>
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Intake Source</label>
            <select
              className="form-control"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
            >
              <option value="">All Ingestion Vectors</option>
              <option value="SMTP_EMAIL">Inbound SMTP Email</option>
              <option value="CANON_SCANNER">Canon Hardware Scanner</option>
              <option value="DIRECT_UPLOAD">Direct File Upload</option>
            </select>
          </div>
        </div>
      </div>

      {/* Inbound Queue Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Source</th>
                <th>Sender / Email</th>
                <th>Subject / Topic</th>
                <th>Attachment</th>
                <th>Confidence & Status</th>
                <th>Received At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    Loading inbound document queue...
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                    No incoming emails or pending scans found. Click "Simulate Inbound SMTP Email" to test the intake flow.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.3rem',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: doc.source === 'SMTP_EMAIL' ? '#0284c7' : '#059669'
                      }}>
                        {doc.source === 'SMTP_EMAIL' ? <Mail size={14} /> : <Printer size={14} />}
                        {doc.source.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      <div><strong>{doc.sender_name || 'N/A'}</strong></div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.sender_email || 'No email provided'}</div>
                    </td>
                    <td><strong>{doc.subject || 'Document Review'}</strong></td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <FileText size={14} /> {doc.file_name}
                      </span>
                    </td>
                    <td>{renderStatusBadge(doc)}</td>
                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {new Date(doc.received_at).toLocaleString()}
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedDocForReview(doc)}
                        className="btn btn-primary btn-sm"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                      >
                        <Sparkles size={14} />
                        <span>Review & Auto-Fill</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Unified Document Intake Modal */}
      {selectedDocForReview && (
        <UnifiedDocumentIntakeModal
          isOpen={!!selectedDocForReview}
          onClose={() => setSelectedDocForReview(null)}
          onSuccess={fetchInboundDocuments}
          initialInboundDoc={selectedDocForReview}
          intakeSource={selectedDocForReview.source as any}
        />
      )}
    </div>
  );
};
