import { apiClient } from './apiClient';
import {
  TokenResponse,
  UserLogin,
  UserResponse,
  DartaResponse,
  ChalanResponse,
  ForwardingCreate,
  ForwardingResponse,
  OfficeResponse,
  DepartmentResponse,
  OfficerResponse,
  FinancialYearResponse,
  LogResponse,
  SystemStats,
  InboundDocument,
  InboundDocumentFilter,
  ConvertInboundToDarta,
  SimulateEmailRequest,
  ParsedCandidateFields,
  NotificationListResponse,
  NotificationItem,
} from '../types';

// Auth Services
export const authService = {
  login: async (credentials: UserLogin): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return res.data;
  },
  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken });
    return res.data;
  },
  logout: async (refreshToken?: string): Promise<void> => {
    await apiClient.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
  },
  getCurrentUser: async (): Promise<UserResponse> => {
    const res = await apiClient.get<UserResponse>('/users/me');
    return res.data;
  },
};

// Darta Services
export const dartaService = {
  search: async (params?: Record<string, any>): Promise<DartaResponse[]> => {
    const res = await apiClient.get<DartaResponse[]>('/darta', { params });
    return res.data;
  },
  getById: async (id: number): Promise<DartaResponse> => {
    const res = await apiClient.get<DartaResponse>(`/darta/${id}`);
    return res.data;
  },
  create: async (formData: FormData): Promise<DartaResponse> => {
    const res = await apiClient.post<DartaResponse>('/darta', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  triggerOCR: async (id: number): Promise<DartaResponse> => {
    const res = await apiClient.post<DartaResponse>(`/darta/${id}/ocr`);
    return res.data;
  },
  downloadFile: async (id: number, filename?: string): Promise<void> => {
    await downloadAuthenticatedBlob(`/darta/${id}/download`, filename || `darta_${id}_attachment.pdf`);
  },
  getDownloadUrl: (id: number): string => {
    return `${apiClient.defaults.baseURL}/darta/${id}/download`;
  },
};

// Chalan Services
export const chalanService = {
  search: async (params?: Record<string, any>): Promise<ChalanResponse[]> => {
    const res = await apiClient.get<ChalanResponse[]>('/chalan', { params });
    return res.data;
  },
  getById: async (id: number): Promise<ChalanResponse> => {
    const res = await apiClient.get<ChalanResponse>(`/chalan/${id}`);
    return res.data;
  },
  create: async (formData: FormData): Promise<ChalanResponse> => {
    const res = await apiClient.post<ChalanResponse>('/chalan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  triggerOCR: async (id: number): Promise<ChalanResponse> => {
    const res = await apiClient.post<ChalanResponse>(`/chalan/${id}/ocr`);
    return res.data;
  },
  downloadFile: async (id: number, filename?: string): Promise<void> => {
    await downloadAuthenticatedBlob(`/chalan/${id}/download`, filename || `chalan_${id}_attachment.pdf`);
  },
  getDownloadUrl: (id: number): string => {
    return `${apiClient.defaults.baseURL}/chalan/${id}/download`;
  },
};

// Forwarding Services
export const forwardingService = {
  create: async (data: ForwardingCreate): Promise<ForwardingResponse> => {
    const res = await apiClient.post<ForwardingResponse>('/forwarding', data);
    return res.data;
  },
  getById: async (id: number): Promise<ForwardingResponse> => {
    const res = await apiClient.get<ForwardingResponse>(`/forwarding/${id}`);
    return res.data;
  },
  getHistory: async (docType: 'DARTA' | 'CHALAN', docId: number): Promise<ForwardingResponse[]> => {
    const res = await apiClient.get<ForwardingResponse[]>(`/forwarding/document/${docType}/${docId}`);
    return res.data;
  },
};

// Inbound Email & Document Auto-Parsing Services
export const inboundService = {
  list: async (params?: InboundDocumentFilter): Promise<InboundDocument[]> => {
    const res = await apiClient.get<InboundDocument[]>('/inbound', { params });
    return res.data;
  },
  getById: async (id: number): Promise<InboundDocument> => {
    const res = await apiClient.get<InboundDocument>(`/inbound/${id}`);
    return res.data;
  },
  parse: async (id: number): Promise<InboundDocument> => {
    const res = await apiClient.post<InboundDocument>(`/inbound/${id}/parse`);
    return res.data;
  },
  parseFile: async (file: File): Promise<ParsedCandidateFields> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<ParsedCandidateFields>('/inbound/parse-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  convertToDarta: async (id: number, payload: ConvertInboundToDarta): Promise<DartaResponse> => {
    const res = await apiClient.post<DartaResponse>(`/inbound/${id}/convert-darta`, payload);
    return res.data;
  },
  simulateEmail: async (payload: SimulateEmailRequest): Promise<InboundDocument> => {
    const res = await apiClient.post<InboundDocument>('/inbound/simulate-email', payload);
    return res.data;
  },
  getSMTPStatus: async (): Promise<{
    running: boolean;
    host: string;
    port: number;
    uptime_seconds: number;
    messages_processed: number;
    last_message_at?: string;
    last_sender?: string;
    last_subject?: string;
    last_error?: string;
    max_message_mb: number;
    allowed_domains: string[];
  }> => {
    const res = await apiClient.get('/inbound/smtp/status');
    return res.data;
  },
  sendSMTPTestScan: async (payload?: {
    sender_email?: string;
    sender_name?: string;
    subject?: string;
    file_name?: string;
  }): Promise<{ success: boolean; message: string; sender: string; subject: string }> => {
    const res = await apiClient.post('/inbound/smtp/test-send', payload || {});
    return res.data;
  },
  toggleSMTPScanner: async (enable: boolean): Promise<any> => {
    const res = await apiClient.post('/inbound/smtp/toggle', { enable });
    return res.data;
  },
  downloadFile: async (id: number, filename?: string): Promise<void> => {
    await downloadAuthenticatedBlob(`/inbound/${id}/download`, filename || `inbound_${id}_attachment.pdf`);
  },
  getDownloadUrl: (id: number): string => {
    return `${apiClient.defaults.baseURL}/inbound/${id}/download`;
  },
};

// Staff Notification Services
export const notificationService = {
  getNotifications: async (unreadOnly = false, limit = 50, offset = 0): Promise<NotificationListResponse> => {
    const res = await apiClient.get<NotificationListResponse>('/notifications', {
      params: { unread_only: unreadOnly, limit, offset },
    });
    return res.data;
  },
  markAsRead: async (id: number): Promise<NotificationItem> => {
    const res = await apiClient.patch<NotificationItem>(`/notifications/${id}/read`);
    return res.data;
  },
  markAllAsRead: async (): Promise<{ message: string; updated_count: number }> => {
    const res = await apiClient.post<{ message: string; updated_count: number }>('/notifications/mark-all-read');
    return res.data;
  },
};

// Master Setup Services
export const masterService = {
  getOffices: async (): Promise<OfficeResponse[]> => {
    const res = await apiClient.get<OfficeResponse[]>('/offices');
    return res.data;
  },
  createOffice: async (data: { name: string; location: string }): Promise<OfficeResponse> => {
    const res = await apiClient.post<OfficeResponse>('/offices', data);
    return res.data;
  },
  getDepartments: async (): Promise<DepartmentResponse[]> => {
    const res = await apiClient.get<DepartmentResponse[]>('/departments');
    return res.data;
  },
  createDepartment: async (data: { name: string }): Promise<DepartmentResponse> => {
    const res = await apiClient.post<DepartmentResponse>('/departments', data);
    return res.data;
  },
  getOfficers: async (): Promise<OfficerResponse[]> => {
    const res = await apiClient.get<OfficerResponse[]>('/officers');
    return res.data;
  },
  createOfficer: async (data: { name: string; department: number; office: number }): Promise<OfficerResponse> => {
    const res = await apiClient.post<OfficerResponse>('/officers', data);
    return res.data;
  },
  getFinancialYears: async (): Promise<FinancialYearResponse[]> => {
    const res = await apiClient.get<FinancialYearResponse[]>('/financial-years');
    return res.data;
  },
  createFinancialYear: async (data: { financial_year: string }): Promise<FinancialYearResponse> => {
    const res = await apiClient.post<FinancialYearResponse>('/financial-years', data);
    return res.data;
  },
};

// Logs & System Services
export const systemService = {
  getLogs: async (params?: Record<string, any>): Promise<LogResponse[]> => {
    const res = await apiClient.get<LogResponse[]>('/logs', { params });
    return res.data;
  },
  getHealth: async (): Promise<any> => {
    const res = await apiClient.get('/system/health');
    return res.data;
  },
  getStats: async (): Promise<SystemStats> => {
    const res = await apiClient.get<SystemStats>('/system/stats');
    return res.data;
  },
  exportDartaCsv: async (params?: Record<string, any>): Promise<void> => {
    await downloadAuthenticatedBlob('/export/darta', 'darta_export.csv', params);
  },
  exportChalanCsv: async (params?: Record<string, any>): Promise<void> => {
    await downloadAuthenticatedBlob('/export/chalan', 'chalan_export.csv', params);
  },
};

// User Management Services
export const userService = {
  getUsers: async (params?: Record<string, any>): Promise<UserResponse[]> => {
    const res = await apiClient.get<UserResponse[]>('/users', { params });
    return res.data;
  },
  getUserById: async (id: number): Promise<UserResponse> => {
    const res = await apiClient.get<UserResponse>(`/users/${id}`);
    return res.data;
  },
  createUser: async (data: any): Promise<UserResponse> => {
    const res = await apiClient.post<UserResponse>('/users', data);
    return res.data;
  },
  updateUser: async (id: number, data: any): Promise<UserResponse> => {
    const res = await apiClient.put<UserResponse>(`/users/${id}`, data);
    return res.data;
  },
  updateUserStatus: async (id: number, isDisabled: boolean): Promise<UserResponse> => {
    const res = await apiClient.patch<UserResponse>(`/users/${id}/status`, {
      user_id: id,
      user_status: isDisabled,
    });
    return res.data;
  },
  resetUserPassword: async (id: number, newPassword: string): Promise<any> => {
    const res = await apiClient.put(`/users/${id}/password`, { new_password: newPassword });
    return res.data;
  },
  updateProfile: async (data: { full_name?: string; email?: string }): Promise<UserResponse> => {
    const res = await apiClient.put<UserResponse>('/users/me', data);
    return res.data;
  },
  changePassword: async (data: any): Promise<any> => {
    const res = await apiClient.put('/users/me/password', data);
    return res.data;
  },
};

// Helper function for downloading binary files with Authorization token attached
export const downloadAuthenticatedBlob = async (endpoint: string, defaultFilename: string, params?: Record<string, any>): Promise<void> => {
  const response = await apiClient.get(endpoint, { responseType: 'blob', params });
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = blobUrl;
  link.setAttribute('download', defaultFilename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
};
