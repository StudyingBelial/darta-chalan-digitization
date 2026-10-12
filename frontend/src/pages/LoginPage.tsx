import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, Mail, UserCheck, AlertCircle } from 'lucide-react';
import { UserType } from '../types';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState<UserType>('STAFF');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login({
        email,
        password,
        user_type: userType,
      });
    } catch (err: any) {
      console.error('Login failed:', err);
      const msg = err.response?.data?.detail || 'Invalid email, password, or user role selected.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #001f3f 0%, #003b73 50%, #0f172a 100%)',
      padding: '1.5rem'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '440px',
        backgroundColor: '#ffffff',
        borderRadius: '20px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
        overflow: 'hidden'
      }}>
        {/* Top NTC Header */}
        <div style={{
          backgroundColor: '#003b73',
          padding: '2.5rem 2rem 2rem 2rem',
          textAlign: 'center',
          color: '#ffffff',
          position: 'relative'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #00a8cc, #00b4d8)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            boxShadow: '0 4px 15px rgba(0, 168, 204, 0.4)'
          }}>
            <ShieldCheck size={36} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '0.02em' }}>
            NEPAL TELECOM
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#a5f3fc', marginTop: '0.25rem' }}>
            Darta (Incoming) & Chalan (Outgoing) Digitization
          </p>
        </div>

        {/* Login Form */}
        <div style={{ padding: '2rem' }}>
          {error && (
            <div style={{
              padding: '0.75rem 1rem',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: '#991b1b',
              borderRadius: '8px',
              fontSize: '0.825rem',
              marginBottom: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Select User Role</label>
              <div style={{ position: 'relative' }}>
                <select
                  className="form-control"
                  style={{ paddingLeft: '2.5rem' }}
                  value={userType}
                  onChange={(e) => setUserType(e.target.value as UserType)}
                >
                  <option value="STAFF">Staff Officer</option>
                  <option value="OFFICE_ADMIN">Office Administrator</option>
                  <option value="SYSTEM_ADMIN">System Administrator</option>
                </select>
                <UserCheck size={18} color="#64748b" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              </div>
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  required
                  className="form-control"
                  style={{ paddingLeft: '2.5rem' }}
                  placeholder="e.g. officer@ntc.net.np"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <Mail size={18} color="#64748b" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label>Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  required
                  className="form-control"
                  style={{ paddingLeft: '2.5rem' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.75rem', fontSize: '0.95rem' }}
            >
              {isSubmitting ? 'Authenticating...' : 'Sign In to Portal'}
            </button>
          </form>

          <p style={{
            fontSize: '0.75rem',
            textAlign: 'center',
            color: '#94a3b8',
            marginTop: '1.75rem'
          }}>
            Authorized NTC Personnel Only • Nepal Telecom Corporation
          </p>
        </div>
      </div>
    </div>
  );
};
