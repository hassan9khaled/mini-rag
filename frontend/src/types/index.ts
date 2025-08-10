export interface Project {
  id: string;
  name: string;
  description: string;
  documentCount: number;
  lastUpdated: string;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red';
  isStarred: boolean;
}

export interface Document {
  id: string;
  name: string;
  type: 'PDF' | 'CSV' | 'DOCX' | 'TXT';
  status: 'processed' | 'processing' | 'failed';
  size: string;
  uploadDate: string;
  projectId: string;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: string;
  projectId?: string;
  selectedDocuments?: string[];
}

export interface ChatSession {
  id: string;
  projectId: string;
  messages: Message[];
  selectedDocuments: string[];
}