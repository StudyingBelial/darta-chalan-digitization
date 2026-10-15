import React, { useState, useEffect } from 'react';
import { Database, Plus, Building2, Layers, UserCheck, Calendar } from 'lucide-react';
import { masterService } from '../services/apiServices';
import { OfficeResponse, DepartmentResponse, OfficerResponse, FinancialYearResponse } from '../types';

export const MasterDataPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'offices' | 'departments' | 'officers' | 'financialYears'>('offices');

  const [offices, setOffices] = useState<OfficeResponse[]>([]);
  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);
  const [officers, setOfficers] = useState<OfficerResponse[]>([]);
  const [financialYears, setFinancialYears] = useState<FinancialYearResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Office Form
  const [newOfficeName, setNewOfficeName] = useState('');
  const [newOfficeLocation, setNewOfficeLocation] = useState('');

  // Department Form
  const [newDeptName, setNewDeptName] = useState('');

  // Officer Form
  const [newOfficerName, setNewOfficerName] = useState('');
  const [selectedOfficerDept, setSelectedOfficerDept] = useState<number | undefined>(undefined);
  const [selectedOfficerOffice, setSelectedOfficerOffice] = useState<number | undefined>(undefined);

  // Financial Year Form
  const [newFyName, setNewFyName] = useState('');

  useEffect(() => {
    loadAllMasterData();
  }, []);

  const loadAllMasterData = async () => {
    setLoading(true);
    try {
      const [offRes, deptRes, offiRes, fyRes] = await Promise.all([
        masterService.getOffices().catch(() => []),
        masterService.getDepartments().catch(() => []),
        masterService.getOfficers().catch(() => []),
        masterService.getFinancialYears().catch(() => []),
      ]);
      setOffices(offRes);
      setDepartments(deptRes);
      setOfficers(offiRes);
      setFinancialYears(fyRes);
    } catch (e) {
      console.error('Error loading master data:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOffice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await masterService.createOffice({ name: newOfficeName, location: newOfficeLocation });
      setNewOfficeName('');
      setNewOfficeLocation('');
      loadAllMasterData();
      alert('Office added successfully');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create office');
    }
  };

  const handleCreateDepartment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await masterService.createDepartment({ name: newDeptName });
      setNewDeptName('');
      loadAllMasterData();
      alert('Department added successfully');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create department');
    }
  };

  const handleCreateOfficer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOfficerDept || !selectedOfficerOffice) {
      alert('Please select both department and office');
      return;
    }
    try {
      await masterService.createOfficer({
        name: newOfficerName,
        department: selectedOfficerDept,
        office: selectedOfficerOffice,
      });
      setNewOfficerName('');
      loadAllMasterData();
      alert('Officer added successfully');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create officer');
    }
  };

  const handleCreateFinancialYear = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await masterService.createFinancialYear({ financial_year: newFyName });
      setNewFyName('');
      loadAllMasterData();
      alert('Financial Year added successfully');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create financial year');
    }
  };

  return (
    <div>
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#003b73', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={24} color="#003b73" /> Master Configuration & Setup
        </h2>
        <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
          Manage organizational units, offices, departments, officer roles, and fiscal year configurations.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        <button
          onClick={() => setActiveTab('offices')}
          className={`btn ${activeTab === 'offices' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Building2 size={16} /> Offices ({offices.length})
        </button>
        <button
          onClick={() => setActiveTab('departments')}
          className={`btn ${activeTab === 'departments' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Layers size={16} /> Departments ({departments.length})
        </button>
        <button
          onClick={() => setActiveTab('officers')}
          className={`btn ${activeTab === 'officers' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <UserCheck size={16} /> Officers ({officers.length})
        </button>
        <button
          onClick={() => setActiveTab('financialYears')}
          className={`btn ${activeTab === 'financialYears' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Calendar size={16} /> Financial Years ({financialYears.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'offices' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
          <div className="card">
            <h3 className="card-title" style={{ marginBottom: '1rem' }}><Plus size={18} /> Add New Office</h3>
            <form onSubmit={handleCreateOffice}>
              <div className="form-group">
                <label>Office Name *</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. NTC Central Office"
                  value={newOfficeName}
                  onChange={(e) => setNewOfficeName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Location *</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Bhadrakali, Kathmandu"
                  value={newOfficeLocation}
                  onChange={(e) => setNewOfficeLocation(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
                Save Office
              </button>
            </form>
          </div>
          <div className="card">
            <h3 className="card-title">Configured Offices</h3>
            <div className="table-responsive" style={{ marginTop: '1rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Office Name</th>
                    <th>Location</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {offices.map((off) => (
                    <tr key={off.id}>
                      <td><strong>#{off.id}</strong></td>
                      <td>{off.name}</td>
                      <td>{off.location}</td>
                      <td>
                        <span className={`badge ${off.is_disabled ? 'badge-archived' : 'badge-completed'}`}>
                          {off.is_disabled ? 'Disabled' : 'Active'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'departments' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
          <div className="card">
            <h3 className="card-title" style={{ marginBottom: '1rem' }}><Plus size={18} /> Add New Department</h3>
            <form onSubmit={handleCreateDepartment}>
              <div className="form-group">
                <label>Department Name *</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Finance & Accounting"
                  value={newDeptName}
                  onChange={(e) => setNewDeptName(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
                Save Department
              </button>
            </form>
          </div>
          <div className="card">
            <h3 className="card-title">Configured Departments</h3>
            <div className="table-responsive" style={{ marginTop: '1rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Department Name</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((dept) => (
                    <tr key={dept.id}>
                      <td><strong>#{dept.id}</strong></td>
                      <td>{dept.name}</td>
                      <td>
                        <span className={`badge ${dept.is_disabled ? 'badge-archived' : 'badge-completed'}`}>
                          {dept.is_disabled ? 'Disabled' : 'Active'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'officers' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
          <div className="card">
            <h3 className="card-title" style={{ marginBottom: '1rem' }}><Plus size={18} /> Add New Officer</h3>
            <form onSubmit={handleCreateOfficer}>
              <div className="form-group">
                <label>Officer Name *</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Er. Rajesh Sharma"
                  value={newOfficerName}
                  onChange={(e) => setNewOfficerName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Department *</label>
                <select
                  required
                  className="form-control"
                  value={selectedOfficerDept || ''}
                  onChange={(e) => setSelectedOfficerDept(Number(e.target.value))}
                >
                  <option value="">-- Select Department --</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Office *</label>
                <select
                  required
                  className="form-control"
                  value={selectedOfficerOffice || ''}
                  onChange={(e) => setSelectedOfficerOffice(Number(e.target.value))}
                >
                  <option value="">-- Select Office --</option>
                  {offices.map((o) => (
                    <option key={o.id} value={o.id}>{o.name}</option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
                Save Officer
              </button>
            </form>
          </div>
          <div className="card">
            <h3 className="card-title">Configured Officers</h3>
            <div className="table-responsive" style={{ marginTop: '1rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Officer Name</th>
                    <th>Dept ID</th>
                    <th>Office ID</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {officers.map((offi) => (
                    <tr key={offi.id}>
                      <td><strong>#{offi.id}</strong></td>
                      <td>{offi.name}</td>
                      <td>{offi.department || 'N/A'}</td>
                      <td>{offi.office || 'N/A'}</td>
                      <td>
                        <span className={`badge ${offi.is_disabled ? 'badge-archived' : 'badge-completed'}`}>
                          {offi.is_disabled ? 'Disabled' : 'Active'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'financialYears' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
          <div className="card">
            <h3 className="card-title" style={{ marginBottom: '1rem' }}><Plus size={18} /> Add Financial Year</h3>
            <form onSubmit={handleCreateFinancialYear}>
              <div className="form-group">
                <label>Financial Year Code *</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. 2081/2082"
                  value={newFyName}
                  onChange={(e) => setNewFyName(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
                Save Financial Year
              </button>
            </form>
          </div>
          <div className="card">
            <h3 className="card-title">Configured Financial Years</h3>
            <div className="table-responsive" style={{ marginTop: '1rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Financial Year</th>
                  </tr>
                </thead>
                <tbody>
                  {financialYears.map((fy) => (
                    <tr key={fy.id}>
                      <td><strong>#{fy.id}</strong></td>
                      <td><strong>{fy.financial_year}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
