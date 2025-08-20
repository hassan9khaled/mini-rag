import React, { useState, useRef } from 'react';
import { Search, Upload, Filter, FileText, X, Check, Loader, AlertCircle } from 'lucide-react';
import { Document } from '../../types';
import toast from 'react-hot-toast';

interface ResourcesSidebarProps {
  documents: Document[];
  selectedDocuments: string[];
  onDocumentSelect: (documentId: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
  selectedProject?: string | null;
  fetchDocuments?: (projectName: string) => void;
}
const API_BASE_URL = "http://localhost:5000";
export const ResourcesSidebar: React.FC<ResourcesSidebarProps> = ({
  documents,
  selectedDocuments,
  onDocumentSelect,
  searchTerm,
  onSearchChange,
  selectedProject,
  fetchDocuments,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [processingFiles, setProcessingFiles] = useState<{ [fileId: string]: boolean }>({});
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [fileTypeFilter, setFileTypeFilter] = useState<string | null>(null);
  const documentTypes = Array.from(new Set(documents.map(doc => doc.type)));
  const getFileIcon = (type: string) => {
    return <FileText className="w-4 h-4" />;
  };

  const getStatusIcon = (status: string, docId: string) => {
    if (processingFiles[docId]) {
      return <Loader className="w-3 h-3 text-blue-600 animate-spin" />;
    }
    switch (status) {
      case 'processed':
        return <Check className="w-3 h-3 text-green-600" />;
      case 'processing':
        return <Loader className="w-3 h-3 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-3 h-3 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

const filteredDocuments = documents
  .filter(doc => doc.name.toLowerCase().includes(searchTerm.toLowerCase()))
  .filter(doc => !fileTypeFilter || doc.type === fileTypeFilter);


  const selectedCount = selectedDocuments.length;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    // Handle file drop logic here
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ''; // reset file input
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !selectedProject) return;
    setUploadStatus(null);
    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await fetch(
        `http://localhost:5000/api/v1/data/upload/${selectedProject}`,
        {
          method: 'POST',
          body: formData,
        }
      );
      const uploadData = await uploadRes.json();
      if (!uploadRes.ok || uploadData.signal !== 'file_uploaded_success') {
        throw new Error('Upload failed');
      }
      if (uploadData.csv_signal == 'you_csv_file_exceed_the_records_limit')
        setUploadStatus('Your file has excedded the limit of records only' + uploadData.num_of_records + "will be used");
      toast.success(`File uploaded successfully!`);

      // Start processing
      const fileIdName = uploadData.file_name;
      setProcessingFiles(prev => ({ ...prev, [fileIdName]: true }));

      const processRes = await fetch(
        `http://localhost:5000/api/v1/data/process/${selectedProject}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            file_id: fileIdName,
            chunk_size: 200,
            overlap_size: 30,
            do_reset: 1,
          }),
        }
      );
      const processData = await processRes.json();
      
      // After processing, push to index
      if (processData.signal === 'processing_success') {
        await fetch(
          `http://localhost:5000/api/v1/nlp/index/push/${selectedProject}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              asset_name: fileIdName,
              do_reset: 1,
            }),
          }
        );
        setProcessingFiles(prev => {
          const updated = { ...prev };
          delete updated[fileIdName];
          return updated;
        });
        toast.success(`File processed and pushed successfully!`);
        if (fetchDocuments) fetchDocuments(selectedProject);
      } else {
        toast.error(`Failed process file.`);
      }
    } catch (err) {
      toast.error("Failed to upload the file.")
    }
    setTimeout(() => setUploadStatus(null), 3000);
  };

  return (
    <div className="bg-white border-l border-gray-200 flex flex-col flex-1 h-full">
      <div className="p-2 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-semibold text-gray-900">Resources</h2>
            {selectedCount > 0 && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {selectedCount} selected
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            onClick={() => setShowFilters(prev => !prev)}>
              
              <Filter className="w-4 h-4" />
            </button>
            <button
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={handleUploadClick}
              type="button"
            >
              <Upload className="w-4 h-4" />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
          </div>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        {showFilters && (
      <div className="mt-2 flex space-x-2">
        {documentTypes.map(type => (
          <button
            key={type}
            className={`px-3 py-1 rounded-xl border ${
              fileTypeFilter === type ? 'bg-blue-500 text-white' : 'bg-gray-100'
            }`}
            onClick={() => setFileTypeFilter(fileTypeFilter === type ? null : type)}
          >
            {type}
          </button>
        ))}
      </div>
    )}

                    
        {uploadStatus && (
          <div className="mt-2 text-xs text-center text-green-600">{uploadStatus}</div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3 mb-6">
          {filteredDocuments.filter(doc => !fileTypeFilter || doc.type === fileTypeFilter).map((document) => (
            <div
              key={document.id}
              onClick={() => onDocumentSelect(document.id)}
              className={`p-4 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
                selectedDocuments.includes(document.id)
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getFileIcon(document.type)}
                  <span className="font-medium text-gray-900 text-sm">{document.name}</span>
                </div>
                {selectedDocuments.includes(document.id) && (
                  <div className="p-1 bg-blue-600 rounded-full">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between mb-2">
                <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-xl border">
                  {document.type}
                </span>
                <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs border ${getStatusColor(document.status)}`}>
                  {getStatusIcon(document.status, document.name)}
                  <span className="capitalize">
                    {processingFiles[document.name] ? 'processing' : document.status}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{document.uploadDate}</span>
                <span>{document.size}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};