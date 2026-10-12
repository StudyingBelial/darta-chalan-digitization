import React from 'react';
import {
  LayoutDashboard,
  Inbox,
  Send,
  Mail,
  Database,
  History,
  Users,
  User,
  ShieldCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const { user } = useAuth();
  const isAdmin = user?.user_type === 'SYSTEM_ADMIN' || user?.user_type === 'OFFICE_ADMIN';

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'inbound', label: 'Inbound Mail & Queue', icon: Mail },
    { id: 'darta', label: 'Darta (Incoming)', icon: Inbox },
    { id: 'chalan', label: 'Chalan (Outgoing)', icon: Send },
    { id: 'master', label: 'Master Setup', icon: Database },
    { id: 'logs', label: 'Audit Logs', icon: History },
  ];

  if (isAdmin) {
    menuItems.push({ id: 'users', label: 'User Management', icon: Users });
  }

  menuItems.push({ id: 'profile', label: 'My Account', icon: User });

  return (
    <aside style={{
      width: '260px',
      backgroundColor: '#003b73',
      color: '#ffffff',
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      boxShadow: '4px 0 15px rgba(0,0,0,0.05)'
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '1.5rem 1.5rem 1.25rem 1.5rem',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.85rem'
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #00a8cc, #00b4d8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 10px rgba(0, 168, 204, 0.4)'
        }}>
          <ShieldCheck size={24} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1rem', fontWeight: 800, letterSpacing: '0.02em', color: '#ffffff' }}>
            NEPAL TELECOM
          </h1>
          <p style={{ fontSize: '0.725rem', color: '#a5f3fc', fontWeight: 500 }}>
            Darta-Chalan Digitization
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ padding: '1.25rem 0.85rem', flex: 1 }}>
        <p style={{
          fontSize: '0.675rem',
          fontWeight: 700,
          color: '#94a3b8',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          padding: '0 0.75rem 0.65rem 0.75rem'
        }}>
          Main Navigation
        </p>
        <ul style={{ listStyle: 'none' }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id} style={{ marginBottom: '0.35rem' }}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                    padding: '0.75rem 0.9rem',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: isActive ? 'rgba(0, 168, 204, 0.2)' : 'transparent',
                    color: isActive ? '#38bdf8' : '#e2e8f0',
                    fontWeight: isActive ? 700 : 500,
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    borderLeft: isActive ? '4px solid #00a8cc' : '4px solid transparent'
                  }}
                >
                  <Icon size={18} color={isActive ? '#38bdf8' : '#94a3b8'} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer System Info */}
      <div style={{
        padding: '1.25rem',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        fontSize: '0.725rem',
        color: '#94a3b8',
        backgroundColor: '#002f5c'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
          <span>System Version:</span>
          <span style={{ color: '#38bdf8', fontWeight: 600 }}>v1.0.0</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Backend status:</span>
          <span style={{ color: '#4ade80', fontWeight: 600 }}>Connected</span>
        </div>
      </div>
    </aside>
  );
};
