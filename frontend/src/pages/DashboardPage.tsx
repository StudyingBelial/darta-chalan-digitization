import React, { useState, useEffect } from 'react';
import {
  Inbox,
  Send,
  Cpu,
  Activity,
  Calendar,
  CheckCircle,
  PlusCircle,
  FileSpreadsheet
} from 'lucide-react';
import { systemService, dartaService, chalanService } from '../services/apiServices';
import { SystemStats, DartaResponse, ChalanResponse } from '../types';

interface DashboardPageProps {
  setActiveTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ setActiveTab }) => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [recentDarta, setRecentDarta] = useState<DartaResponse[]>([]);
  const [recentChalan, setRecentChalan] = useState<ChalanResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, healthRes, dartaRes, chalanRes] = await Promise.all([
        systemService.getStats().catch(() => ({})),
        systemService.getHealth().catch(() => ({ status: 'healthy' })),
        dartaService.search({ order_direction: 'desc' }).catch(() => []),
        chalanService.search({ order_direction: 'desc' }).catch(() => []),
      ]);

      setStats(statsRes);
      setHealth(healthRes);
      setRecentDarta(dartaRes.slice(0, 5));
      setRecentChalan(chalanRes.slice(0, 5));
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  const totalDarta = stats?.total_darta ?? recentDarta.length;
  const totalChalan = stats?.total_chalan ?? recentChalan.length;

  return (
    <div>
      {/* Banner / Header */}
      <div style={{
        background: 'linear-gradient(135deg, #003b73 0%, #00509d 100%)',
        color: '#ffffff',
        padding: '1.75rem 2rem',
        borderRadius: '16px',
        marginBottom: '1.75rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 8px 20px rgba(0, 59, 115, 0.15)'
      }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            System Overview & Metrics
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#a5f3fc', marginTop: '0.25rem' }}>
            Nepal Telecom Central Document Digitization Engine
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={() => setActiveTab('darta')} className="btn btn-accent">
            <PlusCircle size={16} /> Register Darta
          </button>
          <button onClick={() => setActiveTab('chalan')} className="btn btn-secondary" style={{ color: '#003b73' }}>
            <PlusCircle size={16} /> Register Chalan
          </button>
        </div>
      </div>

      {/* Analytics Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1.25rem',
        marginBottom: '1.75rem'
      }}>
        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Total Darta (Incoming)</span>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#003b73', marginTop: '0.25rem' }}>
                {loading ? '...' : totalDarta}
              </h3>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: '#e6f0fa',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Inbox size={26} color="#003b73" />
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Total Chalan (Outgoing)</span>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#00a8cc', marginTop: '0.25rem' }}>
                {loading ? '...' : totalChalan}
              </h3>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: '#e0f7fa',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Send size={26} color="#00a8cc" />
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Pending Forwardings</span>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f59e0b', marginTop: '0.25rem' }}>
                {loading ? '...' : (stats?.pending_forwardings ?? 0)}
              </h3>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: '#fef3c7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Send size={26} color="#d97706" />
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>OCR Processor</span>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10b981', marginTop: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <CheckCircle size={18} /> Active (Tesseract)
              </h3>
            </div>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: '#d1fae5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Cpu size={26} color="#059669" />
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Section for Recent Darta & Recent Chalan */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Recent Darta */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Inbox size={20} color="#003b73" /> Recent Darta (Incoming)
            </h3>
            <button onClick={() => setActiveTab('darta')} className="btn btn-secondary btn-sm">
              View All
            </button>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Darta #</th>
                  <th>Sender</th>
                  <th>Topic</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentDarta.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem' }}>
                      No Darta records available.
                    </td>
                  </tr>
                ) : (
                  recentDarta.map((item) => (
                    <tr key={item.id || item.darta_id}>
                      <td><strong>#{item.darta_id}</strong></td>
                      <td>{item.sender}</td>
                      <td>{item.topic}</td>
                      <td><span className="badge badge-registered">{item.status || 'REGISTERED'}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Chalan */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Send size={20} color="#00a8cc" /> Recent Chalan (Outgoing)
            </h3>
            <button onClick={() => setActiveTab('chalan')} className="btn btn-secondary btn-sm">
              View All
            </button>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Chalan #</th>
                  <th>Receiver</th>
                  <th>Topic</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentChalan.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem' }}>
                      No Chalan records available.
                    </td>
                  </tr>
                ) : (
                  recentChalan.map((item) => (
                    <tr key={item.id || item.chalan_id}>
                      <td><strong>#{item.chalan_id}</strong></td>
                      <td>{item.receiver?.name || 'N/A'}</td>
                      <td>{item.topic}</td>
                      <td><span className="badge badge-registered">{item.status || 'REGISTERED'}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
