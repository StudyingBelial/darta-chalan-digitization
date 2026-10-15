export type UserType = 'OFFICE_ADMIN' | 'STAFF' | 'SYSTEM_ADMIN';
export type LogType = 'TRACE' | 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
export type LogSource = 'SYSTEM' | 'USER';
export type DocumentStatus = 'REGISTERED' | 'FORWARDED' | 'UNDER_REVIEW' | 'ACTION_TAKEN' | 'COMPLETED' | 'ARCHIVED';
export type InboundSource = 'SMTP_EMAIL' | 'CANON_SCANNER' | 'DIRECT_UPLOAD' | 'API_INTAKE';
export type ParsingStatus = 'PENDING' | 'PASSED_THRESHOLD' | 'REQUIRES_HUMAN_REVIEW' | 'FAILED';

export interface UserResponse {
  id: number;
  full_name: string;
  email: string;
  user_type: UserType;
  user_office?: number;
  is_disabled: boolean;
}

export interface UserLogin {
  email: string;
  user_type: UserType;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: UserResponse;
}

export interface DartaFinancialYear {
  financial_year_id?: number;
  financial_year?: string;
}

export interface DartaDepartment {
  receiver_department_id?: number;
  receiver_department?: string;
}

export interface DartaOfficer {
  receiver_officer_id?: number;
  receiver_officer?: string;
}

export interface DartaResponse {
  id?: number;
  darta_id: number;
  sender: string;
  sender_email: string;
  sender_contact_number?: string;
  darta_date: string;
  darta_date_bs?: string;
  topic: string;
  file_name: string;
  extracted_ocr_text?: string;
  status?: DocumentStatus;
  financial_year?: DartaFinancialYear;
  department?: DartaDepartment;
  officer?: DartaOfficer;
}

export interface CreateDarta {
  darta_id?: number;
  sender: string;
  sender_email: string;
  sender_contact_number?: string;
  darta_date: string;
  darta_date_bs?: string;
  financial_year: number;
  topic: string;
  file_name?: string;
  receiver_department?: number;
  receiver_officer?: number;
  extracted_ocr_text?: string;
  status?: DocumentStatus;
}

export interface ChalanReceiver {
  name: string;
  email: string;
  contact_number?: string;
}

export interface ChalanSender {
  email: string;
  department_id?: number;
  department?: string;
  officer_id?: number;
  officer?: string;
}

export interface ChalanResponse {
  id?: number;
  chalan_id: number;
  chalan_date: string;
  chalan_date_bs?: string;
  topic: string;
  file_name: string;
  extracted_ocr_text?: string;
  status?: DocumentStatus;
  receiver: ChalanReceiver;
  sender: ChalanSender;
}

export interface CreateChalan {
  chalan_id?: number;
  sender_email: string;
  receiver: string;
  receiver_email: string;
  receiver_contact_number?: string;
  chalan_date: string;
  chalan_date_bs?: string;
  topic: string;
  file_name?: string;
  sender_department?: number;
  sender_officer?: number;
  extracted_ocr_text?: string;
  status?: DocumentStatus;
}

export interface ForwardingCreate {
  document_type: 'DARTA' | 'CHALAN';
  document_id: number;
  forwarded_to_office?: number;
  forwarded_to_department?: number;
  forwarded_to_officer?: number;
  remarks?: string;
}

export interface ForwardingResponse {
  id: number;
  document_type: string;
  document_id: number;
  forwarded_by_user: number;
  forwarded_to_office?: number;
  forwarded_to_department?: number;
  forwarded_to_officer?: number;
  remarks?: string;
  status: string;
  timestamp: string;
}

export interface OfficeResponse {
  id: number;
  name: string;
  location: string;
  is_disabled: boolean;
}

export interface DepartmentResponse {
  id: number;
  name: string;
  is_disabled: boolean;
}

export interface OfficerResponse {
  id: number;
  name: string;
  department?: number;
  office?: number;
  is_disabled: boolean;
}

export interface FinancialYearResponse {
  id: number;
  financial_year: string;
}

export interface LogResponse {
  id: number;
  user_id?: number;
  office_id?: number;
  source: LogSource;
  log_type: LogType;
  timestamp: string;
  message: string;
}

export interface SystemStats {
  total_darta?: number;
  total_chalan?: number;
  pending_forwardings?: number;
  active_users?: number;
  ocr_processed_count?: number;
  [key: string]: any;
}

// Inbound & Document Auto-Parsing Types
export interface FieldConfidence {
  value?: any;
  confidence: number;
  is_high_confidence: boolean;
  source: string;
}

export interface ParsedCandidateFields {
  sender?: string;
  sender_email?: string;
  sender_contact_number?: string;
  darta_date?: string;
  darta_date_bs?: string;
  financial_year?: number;
  topic?: string;
  suggested_department_id?: number;
  suggested_department_name?: string;
  suggested_officer_id?: number;
  suggested_officer_name?: string;
  confidence_score: number;
  parsing_status: ParsingStatus;
  threshold: number;
  field_confidences: Record<string, FieldConfidence>;
  extracted_text_snippet?: string;
  detected_language?: string;
}

export interface InboundDocument {
  id: number;
  source: InboundSource;
  sender_email?: string;
  sender_name?: string;
  subject?: string;
  file_name: string;
  confidence_score?: number;
  parsing_status: ParsingStatus;
  status: string;
  parsed_data?: ParsedCandidateFields;
  extracted_ocr_text?: string;
  target_office_id?: number;
  target_department_id?: number;
  assigned_to_user_id?: number;
  converted_darta_id?: number;
  converted_chalan_id?: number;
  received_at: string;
}

export interface InboundDocumentFilter {
  status?: string;
  source?: string;
  parsing_status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface ConvertInboundToDarta {
  sender: string;
  sender_email: string;
  sender_contact_number?: string;
  darta_date: string;
  darta_date_bs?: string;
  financial_year: number;
  topic: string;
  receiver_department?: number;
  receiver_officer?: number;
}

export interface SimulateEmailRequest {
  sender_email: string;
  sender_name: string;
  subject: string;
  body?: string;
  file_content_base64?: string;
  file_name?: string;
  target_office_id?: number;
}

// Notification Types
export interface NotificationItem {
  id: number;
  user_id?: number;
  target_office_id?: number;
  target_role?: string;
  title: string;
  message: string;
  notification_type: 'INBOUND_EMAIL' | 'DOCUMENT_FORWARDED' | 'SCAN_INTAKE' | 'SYSTEM_ALERT';
  inbound_doc_id?: number;
  darta_id?: number;
  chalan_id?: number;
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  unread_count: number;
  total_count: number;
}

// Physical Scanner Types (Canon & Universal)
export interface ScannerDevice {
  id: string;
  name: string;
  type: 'CANON_USB' | 'CANON_NETWORK' | 'TWAIN_WIA' | 'SANE_ESCL';
  isDefault?: boolean;
}

export interface ScannerConfig {
  deviceId: string;
  source: 'ADF' | 'FLATBED';
  resolutionDpi: 150 | 300 | 600;
  colorMode: 'COLOR' | 'GRAYSCALE' | 'BLACK_WHITE';
  duplex: boolean;
  pageSize: 'A4' | 'LEGAL' | 'LETTER';
  autoDeskew: boolean;
  enhanceContrast: boolean;
}

export interface ScannedPage {
  id: string;
  pageNumber: number;
  dataUrl: string;
  rotation: number; // 0, 90, 180, 270
  isEnhanced: boolean;
}
