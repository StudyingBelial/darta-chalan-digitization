import React, { useState, useEffect } from 'react';
import { History, Filter, Search } from 'lucide-react';
import { systemService } from '../services/apiServices';
import { LogResponse } from '../types';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<LogResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [logTypeFilter, setLogTypeFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (logTypeFilter) params.log_type = logTypeFilter;
      if (sourceFilter) params.source = sourceFilter;

      const data = await systemService.getLogs(params);
      setLogs(data);
    } catch (e) {
      console.error('Failed to fetch audit logs:', e);
    } finally {
      setLoading(false);
    }
  };

  const getLogTypeBadgeClass = (type: string) => {
    switch (type) {
      case 'ERROR':
      case 'CRITICAL':
        return 'btn-danger';
      case 'WARNING':
        return 'badge-forwarded';
      case 'INFO':
        return 'badge-registered';
      default:
        return 'badge-completed';
    }
  };

  return (
    <div>
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <History size={24} color="#003b73" /> System Audit & Security Trail
        </h2>
        <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
          Comprehensive record of system events, authentication, document forwardings, and administrative actions.
        </p>
      </div>

      {/* Filter Card */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.25rem' }}>
        <div className="form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Log Severity Level</label>
            <select
              className="form-control"
              value={logTypeFilter}
              onChange={(e) => setLogTypeFilter(e.target.value)}
            >
              <option value="">All Severity Levels</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="DEBUG">DEBUG</option>
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Log Source</label>
            <select
              className="form-control"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
            >
              <option value="">All Sources</option>
              <option value="USER">USER</option>
              <option value="SYSTEM">SYSTEM</option>
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <button onClick={fetchLogs} className="btn btn-accent" style={{ height: '38px' }}>
              <Search size={16} /> Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Timestamp</th>
                <th>Source</th>
                <th>Level</th>
                <th>User ID / Office</th>
                <th>Log Event Message</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    Loading audit trail logs...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    No audit logs matching current filter parameters.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td><strong>#{log.id}</strong></td>
                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td><strong>{log.source}</strong></td>
                    <td>
                      <span className={`badge ${getLogTypeBadgeClass(log.log_type)}`}>
                        {log.log_type}
                      </span>
                    </td>
                    <td>
                      {log.user_id ? `User #${log.user_id}` : 'System Agent'}
                      {log.office_id ? ` (Office #${log.office_id})` : ''}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {log.message}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
