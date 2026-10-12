import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { InboundQueuePage } from './pages/InboundQueuePage';
import { DartaPage } from './pages/DartaPage';
import { ChalanPage } from './pages/ChalanPage';
import { MasterDataPage } from './pages/MasterDataPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { UsersPage } from './pages/UsersPage';
import { ProfilePage } from './pages/ProfilePage';
import { ShieldCheck } from 'lucide-react';

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#003b73',
        color: '#ffffff'
      }}>
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '14px',
          background: 'linear-gradient(135deg, #00a8cc, #00b4d8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.25rem',
          boxShadow: '0 4px 15px rgba(0, 168, 204, 0.4)'
        }}>
          <ShieldCheck size={32} color="#ffffff" />
        </div>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, letterSpacing: '0.02em' }}>
          Nepal Telecom Digitization Portal
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#a5f3fc', marginTop: '0.35rem' }}>
          Initializing session and backend API connection...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage setActiveTab={setActiveTab} />;
      case 'inbound':
        return <InboundQueuePage />;
      case 'darta':
        return <DartaPage />;
      case 'chalan':
        return <ChalanPage />;
      case 'master':
        return <MasterDataPage />;
      case 'logs':
        return <AuditLogsPage />;
      case 'users':
        return <UsersPage />;
      case 'profile':
        return <ProfilePage />;
      default:
        return <DashboardPage setActiveTab={setActiveTab} />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderActivePage()}
    </Layout>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
