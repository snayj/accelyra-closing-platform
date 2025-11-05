// Enums
export enum TransactionStage {
  OFFER_ACCEPTED = 'OFFER_ACCEPTED',
  TITLE_SEARCH = 'TITLE_SEARCH',
  UNDERWRITING = 'UNDERWRITING',
  CLEAR_TO_CLOSE = 'CLEAR_TO_CLOSE',
  FINAL_DOCUMENTS = 'FINAL_DOCUMENTS',
  FUNDING_SIGNING = 'FUNDING_SIGNING',
  RECORDING_COMPLETE = 'RECORDING_COMPLETE',
}

export enum EarnestMoneyStatus {
  PENDING = 'PENDING',
  DEPOSITED = 'DEPOSITED',
  CLEARED = 'CLEARED',
  REFUNDED = 'REFUNDED',
  APPLIED = 'APPLIED',
}

export enum TaskType {
  DOCUMENT_UPLOAD = 'DOCUMENT_UPLOAD',
  DOCUMENT_SIGN = 'DOCUMENT_SIGN',
  DOCUMENT_REVIEW = 'DOCUMENT_REVIEW',
  PAYMENT = 'PAYMENT',
  VERIFICATION = 'VERIFICATION',
  INSPECTION = 'INSPECTION',
  APPROVAL = 'APPROVAL',
  NOTIFICATION = 'NOTIFICATION',
  OTHER = 'OTHER',
}

export enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  BLOCKED = 'BLOCKED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  OVERDUE = 'OVERDUE',
}

export enum TaskPriority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export enum PartyRole {
  BUYER = 'BUYER',
  SELLER = 'SELLER',
  BUYER_AGENT = 'BUYER_AGENT',
  SELLER_AGENT = 'SELLER_AGENT',
  LOAN_OFFICER = 'LOAN_OFFICER',
  TITLE_OFFICER = 'TITLE_OFFICER',
  ESCROW_OFFICER = 'ESCROW_OFFICER',
  CLOSING_COORDINATOR = 'CLOSING_COORDINATOR',
  INSPECTOR = 'INSPECTOR',
  APPRAISER = 'APPRAISER',
}

export enum Priority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  URGENT = 'URGENT',
}

// Models
export interface Transaction {
  id: string;
  propertyAddress: string;
  propertyType?: string;
  propertySqft?: number;
  propertyBedrooms?: number;
  propertyBathrooms?: number;
  propertyYearBuilt?: number;
  purchasePrice: number;
  downPayment?: number;
  loanAmount?: number;
  earnestMoneyAmount?: number;
  earnestMoneyStatus: EarnestMoneyStatus;
  earnestMoneyDepositedAt?: string;
  earnestMoneyClearedAt?: string;
  fundsVerified: boolean;
  fundsVerifiedAt?: string;
  fundsVerifiedBy?: string;
  currentStage: TransactionStage;
  stageHistory: StageHistoryEntry[];
  stageStartedAt?: string;
  createdAt: string;
  estimatedClosingDate?: string;
  actualClosingDate?: string;
  buyerId?: string;
  buyer?: Party;
  sellerId?: string;
  seller?: Party;
  buyerAgentId?: string;
  buyerAgent?: Party;
  sellerAgentId?: string;
  sellerAgent?: Party;
  loanOfficerId?: string;
  loanOfficer?: Party;
  titleOfficerId?: string;
  titleOfficer?: Party;
  tasks?: Task[];
  documents?: Document[];
  notes?: string;
  priority: Priority;
}

export interface StageHistoryEntry {
  stage: TransactionStage | string;
  enteredAt: string;
  notes?: string;
  event?: string;
  [key: string]: any;
}

export interface Task {
  id: string;
  transactionId: string;
  title: string;
  description?: string;
  taskType: TaskType;
  assignedTo?: string;
  assignedBy?: string;
  assignedAt: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate?: string;
  startedAt?: string;
  completedAt?: string;
  completedBy?: string;
  isBlocking: boolean;
  dependsOn: string[];
  blockedReason?: string;
  relatedDocumentId?: string;
  relatedStage?: string;
  completionData: Record<string, any>;
  completionNotes?: string;
  lastReminderSentAt?: string;
  reminderCount: number;
  createdAt: string;
  updatedAt: string;
  notes?: string;
}

export interface Party {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: PartyRole;
  company?: string;
  licenseNumber?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  createdAt: string;
  lastContactedAt?: string;
  notes?: string;
}

export interface Document {
  id: string;
  transactionId: string;
  documentType: string;
  status: string;
  filename: string;
  filePath?: string;
  fileSize?: number;
  mimeType?: string;
  pageCount?: number;
  uploadedBy?: string;
  uploadedAt?: string;
  ocrText?: string;
  extractedData: Record<string, any>;
  validationPerformed: boolean;
  validationPerformedAt?: string;
  validationResults: any[];
  validationPassed?: boolean;
  approvedBy?: string;
  approvedAt?: string;
  rejectedBy?: string;
  rejectedAt?: string;
  rejectionReason?: string;
  version: number;
  supersededBy?: string;
  replaces?: string;
  createdAt: string;
  updatedAt: string;
  notes?: string;
  tags: string[];
}

export interface TransactionProgress {
  currentStage: TransactionStage;
  stageProgress: number;
  stageIndex: number;
  totalStages: number;
  totalTasks: number;
  completedTasks: number;
  taskProgress: number;
  estimatedClosingDate?: string;
  actualClosingDate?: string;
}

// Form types for creating/updating
export interface CreateTransactionInput {
  propertyAddress: string;
  propertyType?: string;
  propertySqft?: number;
  propertyBedrooms?: number;
  propertyBathrooms?: number;
  propertyYearBuilt?: number;
  purchasePrice: number;
  downPayment?: number;
  loanAmount?: number;
  earnestMoneyAmount?: number;
  buyerId?: string;
  sellerId?: string;
  buyerAgentId?: string;
  sellerAgentId?: string;
  loanOfficerId?: string;
  titleOfficerId?: string;
  priority?: Priority;
  notes?: string;
}

export interface CreateTaskInput {
  transactionId: string;
  title: string;
  description?: string;
  taskType: TaskType;
  assignedTo?: string;
  priority?: TaskPriority;
  dueDate?: string;
  isBlocking?: boolean;
  relatedStage?: string;
}

export interface CreatePartyInput {
  name: string;
  email: string;
  phone?: string;
  role: PartyRole;
  company?: string;
  licenseNumber?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  notes?: string;
}
