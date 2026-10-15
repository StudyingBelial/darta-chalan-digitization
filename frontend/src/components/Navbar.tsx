import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Bell, Shield, Mail, Send, CheckCircle, ExternalLink, RefreshCw } from 'lucide-react';
import { NotificationItem, InboundDocument } from '../types';
import { notificationService, inboundService } from '../services/apiServices';
import { UnifiedDocumentIntakeModal } from './UnifiedDocumentIntakeModal';

interface NavbarProps {
  activeTab: string;
  setActiveTab?: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [selectedInboundDoc, setSelectedInboundDoc] = useState<InboundDocument | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 12000); // Check every 12s
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    try {
      const data = await notificationService.getNotifications(false, 15);
      setNotifications(data.items);
      setUnreadCount(data.unread_count);
    } catch (e) {
      // Quiet fail if not yet authenticated
    }
  };

  const handleNotificationClick = async (notif: NotificationItem) => {
    if (!notif.is_read) {
      await notificationService.markAsRead(notif.id).catch(() => {});
      fetchNotifications();
    }

    if (notif.inbound_doc_id) {
      try {
        const doc = await inboundService.getById(notif.inbound_doc_id);
        setSelectedInboundDoc(doc);
        setIsDropdownOpen(false);
      } catch (err) {
        console.error('Failed to open inbound doc:', err);
      }
    } else if (notif.darta_id && setActiveTab) {
      setActiveTab('darta');
      setIsDropdownOpen(false);
    } else if (notif.chalan_id && setActiveTab) {
      setActiveTab('chalan');
      setIsDropdownOpen(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      fetchNotifications();
    } catch (e) {
      console.error('Failed to mark all as read:', e);
    }
  };

  return (
    <header style={{
      height: '64px',
      backgroundColor: '#ffffff',
      borderBottom: '1px solid #e2e8f0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#003b73' }}>
          {activeTab.charAt(0).toUpperCase() + activeTab.slice(1).replace('-', ' ')}
        </h2>
        <span style={{
          backgroundColor: '#e6f0fa',
          color: '#003b73',
          fontSize: '0.75rem',
          padding: '0.2rem 0.6rem',
          borderRadius: '4px',
          fontWeight: 600
        }}>
          NTC Portal
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Notification Bell with Dropdown */}
        <div style={{ position: 'relative' }} ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: unreadCount > 0 ? '#003b73' : '#64748b',
              position: 'relative',
              padding: '0.4rem',
              borderRadius: '8px',
              backgroundColor: isDropdownOpen ? '#f1f5f9' : 'transparent',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Notifications & Incoming Mails"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '-2px',
                right: '-2px',
                minWidth: '18px',
                height: '18px',
                backgroundColor: '#ef4444',
                color: '#ffffff',
                fontSize: '0.65rem',
                fontWeight: 800,
                borderRadius: '9px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0 4px',
                boxShadow: '0 2px 4px rgba(239, 68, 68, 0.4)'
              }}>
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 8px)',
              right: 0,
              width: '360px',
              maxHeight: '480px',
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 10px 25px rgba(0, 59, 115, 0.15)',
              display: 'flex',
              flexDirection: 'column',
              zIndex: 1000,
              overflow: 'hidden'
            }}>
              {/* Header */}
              <div style={{
                padding: '0.85rem 1rem',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: '#f8fafc'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#003b73' }}>
                    Notifications & Inbound Alerts
                  </span>
                  {unreadCount > 0 && (
                    <span style={{ fontSize: '0.7rem', backgroundColor: '#fee2e2', color: '#991b1b', fontWeight: 700, padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                      {unreadCount} new
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    style={{ background: 'none', border: 'none', color: '#00a8cc', fontSize: '0.725rem', fontWeight: 600, cursor: 'pointer' }}
                  >
                    Mark all read
                  </button>
                )}
              </div>

              {/* Items List */}
              <div style={{ flex: 1, overflowY: 'auto', maxHeight: '360px' }}>
                {notifications.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8', fontSize: '0.825rem' }}>
                    No notifications right now.
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => handleNotificationClick(notif)}
                      style={{
                        padding: '0.75rem 1rem',
                        borderBottom: '1px solid #f1f5f9',
                        backgroundColor: notif.is_read ? '#ffffff' : '#f0f9ff',
                        cursor: 'pointer',
                        transition: 'background 0.15s ease',
                        display: 'flex',
                        gap: '0.75rem',
                        alignItems: 'flex-start'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#e0f2fe')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = notif.is_read ? '#ffffff' : '#f0f9ff')}
                    >
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        backgroundColor: notif.notification_type === 'INBOUND_EMAIL' ? '#e0f2fe' : '#fef3c7',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                      }}>
                        {notif.notification_type === 'INBOUND_EMAIL' ? (
                          <Mail size={16} color="#0284c7" />
                        ) : (
                          <Send size={16} color="#d97706" />
                        )}
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0f172a' }}>
                            {notif.title}
                          </span>
                          {!notif.is_read && (
                            <span style={{ width: '6px', height: '6px', backgroundColor: '#0284c7', borderRadius: '50%' }} />
                          )}
                        </div>
                        <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem', lineHeight: 1.3 }}>
                          {notif.message}
                        </p>
                        <span style={{ fontSize: '0.65rem', color: '#94a3b8', marginTop: '0.35rem', display: 'block' }}>
                          {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Footer */}
              {setActiveTab && (
                <div style={{
                  padding: '0.65rem',
                  borderTop: '1px solid #e2e8f0',
                  textAlign: 'center',
                  backgroundColor: '#f8fafc'
                }}>
                  <button
                    onClick={() => {
                      setActiveTab('inbound');
                      setIsDropdownOpen(false);
                    }}
                    className="btn btn-secondary btn-sm"
                    style={{ width: '100%', fontSize: '0.75rem' }}
                  >
                    View Inbound Mail & Queue
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <div style={{ width: '1px', height: '24px', backgroundColor: '#e2e8f0' }} />

        {/* User Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: '#003b73',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '0.9rem'
          }}>
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0f172a' }}>
              {user?.full_name || 'User'}
            </span>
            <span style={{ fontSize: '0.725rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <Shield size={10} color="#00a8cc" />
              {user?.user_type || 'STAFF'}
            </span>
          </div>
        </div>

        <button
          onClick={logout}
          className="btn btn-secondary btn-sm"
          title="Sign Out"
          style={{ marginLeft: '0.5rem' }}
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>

      {/* Direct Inbound Review Modal Triggered from Notifications */}
      {selectedInboundDoc && (
        <UnifiedDocumentIntakeModal
          isOpen={!!selectedInboundDoc}
          onClose={() => setSelectedInboundDoc(null)}
          onSuccess={() => {
            fetchNotifications();
            if (setActiveTab) setActiveTab('darta');
          }}
          initialInboundDoc={selectedInboundDoc}
          intakeSource={selectedInboundDoc.source as any}
        />
      )}
    </header>
  );
};
