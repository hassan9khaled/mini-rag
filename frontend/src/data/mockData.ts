import { Project, Document, Message } from '../types';

export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'AI Research Project',
    description: 'Machine learning research papers and documentation',
    documentCount: 4,
    lastUpdated: '2024-01-15',
    color: 'blue',
    isStarred: true,
  },
  {
    id: '2',
    name: 'Product Documentation',
    description: 'User guides, API docs, and technical specifications',
    documentCount: 4,
    lastUpdated: '2024-01-14',
    color: 'green',
    isStarred: false,
  },
  {
    id: '3',
    name: 'Legal Documents',
    description: 'Contracts, policies, and compliance documents',
    documentCount: 4,
    lastUpdated: '2024-01-12',
    color: 'purple',
    isStarred: true,
  },
];

export const mockDocuments: Document[] = [
  {
    id: '1',
    name: 'Research Paper.pdf',
    type: 'PDF',
    status: 'processed',
    size: '2.3 MB',
    uploadDate: '2024-01-15',
    projectId: '1',
  },
  {
    id: '2',
    name: 'Neural Networks.pdf',
    type: 'PDF',
    status: 'processed',
    size: '3.1 MB',
    uploadDate: '2024-01-14',
    projectId: '1',
  },
  {
    id: '3',
    name: 'Training Data.csv',
    type: 'CSV',
    status: 'processing',
    size: '15.2 MB',
    uploadDate: '2024-01-13',
    projectId: '1',
  },
  {
    id: '4',
    name: 'Model Architecture.docx',
    type: 'DOCX',
    status: 'processed',
    size: '890 KB',
    uploadDate: '2024-01-12',
    projectId: '1',
  },
];

export const mockMessages: Message[] = [
  {
    id: '1',
    content: 'What are the main findings in this research paper?',
    sender: 'user',
    timestamp: '10:30 AM',
    projectId: '1',
    selectedDocuments: ['1'],
  },
  {
    id: '2',
    content: `Based on the research paper, the main findings include:

**Key Results**
1. **Improved Performance**
   The proposed method shows a 15% improvement in accuracy compared to baseline approaches.

2. **Reduced Computational Cost**
   The algorithm reduces processing time by 40% while maintaining similar accuracy.

3. **Scalability**
   The solution scales effectively to larger datasets without significant performance degradation.

4. **Real-world Applications**
   The method has been successfully tested in three different industrial scenarios.`,
    sender: 'ai',
    timestamp: '10:31 AM',
    projectId: '1',
  },
];