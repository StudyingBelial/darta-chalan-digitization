import React, { useState, useEffect } from 'react';
import { Users as UsersIcon, UserPlus, Shield, Lock, X, Edit, KeyRound, Building2 } from 'lucide-react';
import { masterService, userService } from '../services/apiServices';
import { UserResponse, UserType, OfficeResponse } from '../types';

export const UsersPage: React.FC = () => {
  const [usersList, setUsersList] = useState<UserResponse[]>([]);
  const [offices, setOffices] = useState<OfficeResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isResetPasswordModalOpen, setIsResetPasswordModalOpen] = useState(false);

  // Active User for Edit / Reset
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);

  // Create User Form State
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [userType, setUserType] = useState<UserType>('STAFF');
  const [userOffice, setUserOffice] = useState<number>(1);
  const [password, setPassword] = useState('');

  // Edit User Form State
  const [editFullName, setEditFullName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editUserType, setEditUserType] = useState<UserType>('STAFF');
  const [editUserOffice, setEditUserOffice] = useState<number>(1);

  // Reset Password State
  const [newAdminResetPassword, setNewAdminResetPassword] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchUsers();
    fetchOffices();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers();
      setUsersList(data);
    } catch (e) {
      console.error('Failed to fetch user list:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchOffices = async () => {
    try {
      const data = await masterService.getOffices();
      setOffices(data);
      if (data.length > 0) {
        setUserOffice(data[0].id);
        setEditUserOffice(data[0].id);
      }
    } catch (e) {
      console.error('Failed to fetch offices:', e);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await userService.createUser({
        full_name: fullName,
        email,
        user_type: userType,
        user_office: userOffice,
        password,
      });
      alert('User account created successfully!');
      setIsCreateModalOpen(false);
      setFullName('');
      setEmail('');
      setPassword('');
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to create user:', err);
      alert(err.response?.data?.detail || 'Failed to create user account.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModal = (user: UserResponse) => {
    setSelectedUser(user);
    setEditFullName(user.full_name);
    setEditEmail(user.email);
    setEditUserType(user.user_type);
    setEditUserOffice(user.user_office || (offices.length > 0 ? offices[0].id : 1));
    setIsEditModalOpen(true);
  };

  const handleEditUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) return;
    setIsSubmitting(true);
    try {
      await userService.updateUser(selectedUser.id, {
        full_name: editFullName,
        email: editEmail,
        user_type: editUserType,
        user_office: editUserOffice,
      });
      alert('User profile updated successfully!');
      setIsEditModalOpen(false);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to update user:', err);
      alert(err.response?.data?.detail || 'Failed to update user profile.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const openResetPasswordModal = (user: UserResponse) => {
    setSelectedUser(user);
    setNewAdminResetPassword('');
    setIsResetPasswordModalOpen(true);
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) return;
    setIsSubmitting(true);
    try {
      await userService.resetUserPassword(selectedUser.id, newAdminResetPassword);
      alert(`Password for ${selectedUser.full_name} has been reset successfully!`);
      setIsResetPasswordModalOpen(false);
      setNewAdminResetPassword('');
    } catch (err: any) {
      console.error('Failed to reset password:', err);
      alert(err.response?.data?.detail || 'Failed to reset user password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleUserStatus = async (userId: number, currentDisabled: boolean) => {
    try {
      await userService.updateUserStatus(userId, !currentDisabled);
      fetchUsers();
    } catch (e) {
      alert('Failed to update user status');
    }
  };

  const getOfficeName = (officeId?: number) => {
    if (!officeId) return 'N/A';
    const found = offices.find(o => o.id === officeId);
    return found ? found.name : `Office #${officeId}`;
  };

  return (
    <div>
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UsersIcon size={24} color="#003b73" /> User Account Management
            </h2>
            <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
              Administer user profiles, system roles, office assignments, password resets, and account access statuses.
            </p>
          </div>
          <button onClick={() => setIsCreateModalOpen(true)} className="btn btn-primary">
            <UserPlus size={16} /> Create User Account
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Full Name</th>
                <th>Email Address</th>
                <th>Role Type</th>
                <th>Assigned Office</th>
                <th>Account Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    Loading user directory...
                  </td>
                </tr>
              ) : usersList.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    No users found in directory.
                  </td>
                </tr>
              ) : (
                usersList.map((user) => (
                  <tr key={user.id}>
                    <td><strong>#{user.id}</strong></td>
                    <td><strong>{user.full_name}</strong></td>
                    <td>{user.email}</td>
                    <td>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <Shield size={12} color="#00a8cc" /> {user.user_type}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: '#475569', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Building2 size={13} color="#64748b" /> {getOfficeName(user.user_office)}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${user.is_disabled ? 'badge-archived' : 'badge-completed'}`}>
                        {user.is_disabled ? 'Disabled' : 'Active'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                        <button
                          onClick={() => openEditModal(user)}
                          className="btn btn-sm btn-secondary"
                          title="Edit User Profile"
                        >
                          <Edit size={13} /> Edit
                        </button>
                        <button
                          onClick={() => openResetPasswordModal(user)}
                          className="btn btn-sm btn-secondary"
                          title="Reset User Password"
                        >
                          <KeyRound size={13} color="#00a8cc" /> Reset Password
                        </button>
                        <button
                          onClick={() => toggleUserStatus(user.id, user.is_disabled)}
                          className={`btn btn-sm ${user.is_disabled ? 'btn-secondary' : 'btn-danger'}`}
                        >
                          {user.is_disabled ? 'Enable' : 'Disable'}
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

      {/* Create User Modal */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">Create New Staff / Admin User</h3>
              <button onClick={() => setIsCreateModalOpen(false)} className="close-btn"><X size={20} /></button>
            </div>
            <form onSubmit={handleCreateUser}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Ramesh Karki"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    required
                    className="form-control"
                    placeholder="ramesh@ntc.net.np"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>User Role *</label>
                  <select
                    className="form-control"
                    value={userType}
                    onChange={(e) => setUserType(e.target.value as UserType)}
                  >
                    <option value="STAFF">Staff Officer</option>
                    <option value="OFFICE_ADMIN">Office Administrator</option>
                    <option value="SYSTEM_ADMIN">System Administrator</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Assigned Office *</label>
                  <select
                    className="form-control"
                    value={userOffice}
                    onChange={(e) => setUserOffice(Number(e.target.value))}
                  >
                    {offices.map((o) => (
                      <option key={o.id} value={o.id}>{o.name} ({o.location})</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Initial Password *</label>
                  <input
                    type="password"
                    required
                    className="form-control"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => setIsCreateModalOpen(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  {isSubmitting ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {isEditModalOpen && selectedUser && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">Edit User (#{selectedUser.id} - {selectedUser.full_name})</h3>
              <button onClick={() => setIsEditModalOpen(false)} className="close-btn"><X size={20} /></button>
            </div>
            <form onSubmit={handleEditUser}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={editFullName}
                    onChange={(e) => setEditFullName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    required
                    className="form-control"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>User Role *</label>
                  <select
                    className="form-control"
                    value={editUserType}
                    onChange={(e) => setEditUserType(e.target.value as UserType)}
                  >
                    <option value="STAFF">Staff Officer</option>
                    <option value="OFFICE_ADMIN">Office Administrator</option>
                    <option value="SYSTEM_ADMIN">System Administrator</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Assigned Office *</label>
                  <select
                    className="form-control"
                    value={editUserOffice}
                    onChange={(e) => setEditUserOffice(Number(e.target.value))}
                  >
                    {offices.map((o) => (
                      <option key={o.id} value={o.id}>{o.name} ({o.location})</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => setIsEditModalOpen(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  {isSubmitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Admin Reset Password Modal */}
      {isResetPasswordModalOpen && selectedUser && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <KeyRound size={20} color="#003b73" />
                <h3 className="modal-title">Reset User Password</h3>
              </div>
              <button onClick={() => setIsResetPasswordModalOpen(false)} className="close-btn"><X size={20} /></button>
            </div>
            <form onSubmit={handleResetPassword}>
              <div className="modal-body">
                <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1rem' }}>
                  Setting a new password for <strong>{selectedUser.full_name}</strong> ({selectedUser.email}). The old password is not required.
                </p>
                <div className="form-group">
                  <label>New Password *</label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    className="form-control"
                    placeholder="Enter new password..."
                    value={newAdminResetPassword}
                    onChange={(e) => setNewAdminResetPassword(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => setIsResetPasswordModalOpen(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn btn-primary">
                  {isSubmitting ? 'Resetting...' : 'Reset Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
