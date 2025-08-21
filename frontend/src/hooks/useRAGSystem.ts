import { useState, useEffect } from 'react';
import { Project, Document, Message, ChatSession } from '../types';

const API_BASE_URL = "http://localhost:5000";

export const useRAGSystem = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [projectSearchTerm, setProjectSearchTerm] = useState('');
  const [documentSearchTerm, setDocumentSearchTerm] = useState('');

  // --- Chat history per project ---
  useEffect(() => {
    if (selectedProject) {
      const saved = localStorage.getItem(`chat_history_${selectedProject}`);
      setMessages(saved ? JSON.parse(saved) : []);
    }
  }, [selectedProject]);

  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem(`chat_history_${selectedProject}`, JSON.stringify(messages));
    }
  }, [messages, selectedProject]);

  // --- Clean chat only on reload ---
  useEffect(() => {
    if (performance.getEntriesByType("navigation")[0]?.type === "reload") {
      
      if (selectedProject) {
        localStorage.removeItem(`chat_history_${selectedProject}`);
        setMessages([]);
      }
    }
    // eslint-disable-next-line
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/data/projects/info`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const mappedProjects = Array.isArray(data.projects) ? mapApiProjects(data.projects) : [];
      setProjects(mappedProjects);
      if (mappedProjects.length > 0 && !selectedProject) {
        setSelectedProject(mappedProjects[0].id);
        
      }
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  // Fetch resources (assets) for the selected project
  const fetchDocuments = async (projectId: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/projects/assets`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_name: projectId }),
        }
      );
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const mappedDocs: Document[] = Array.isArray(data)
        ? data.map(asset => ({
            id: asset.asset_id,
            name: asset.asset_name,
            projectId: asset.asset_project_name,
            size: `${(asset.asset_size / (1024 * 1024)).toFixed(2)} MB`,
            type: asset.asset_name.split('.').pop() || 'file',
            status: 'processed',
            uploadDate: '', // set if available
            asset_path: asset.asset_path,
          }))
        : [];
      setDocuments(mappedDocs);

      // Update documentCount for each project
      setProjects(prev =>
        prev.map(p =>
          p.id === projectId
            ? { ...p, documentCount: mappedDocs.length }
            : p
        )
      );
    } catch (error) {
      console.error("Error fetching documents/assets:", error);
      setDocuments([]);
    }
  };

  // Fetch all assets and update document counts for all projects
  const fetchAllAssetsAndUpdateCounts = async (projectId: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/projects/assets`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_name: projectId }),
        }
      );
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      // Map assets to documents
      const allDocs: Document[] = Array.isArray(data)
        ? data.map(asset => ({
            id: asset.asset_id,
            name: asset.asset_name,
            projectId: asset.asset_project_name,
            size: `${(asset.asset_size / (1024 * 1024)).toFixed(2)} MB`,
            type: asset.asset_name.split('.').pop() || 'file',
            status: 'processed',
            uploadDate: '', // set if available
            asset_path: asset.asset_path,
          }))
        : [];
      // Update documentCount for each project
      setProjects(prev =>
        prev.map(p => ({
          ...p,
          documentCount: allDocs.filter(doc => doc.projectId === p.id).length,
        }))
      );
      // If a project is selected, update its documents
      if (selectedProject) {
        setDocuments(allDocs.filter(doc => doc.projectId === selectedProject));
      }
    } catch (error) {
      console.error("Error fetching all assets:", error);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchDocuments(selectedProject);
    } else {
      setDocuments([]);
    }
  }, [selectedProject]);

  const currentProject = projects.find(p => p.id === selectedProject);
  const selectedDocumentObjects = documents.filter(d => selectedDocuments.includes(d.id));

  const handleSendMessage = async (content: string) => {
    if (!selectedDocuments.length) return;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: timeString,
      projectId: selectedProject || undefined,
      selectedDocuments,
    };

    setMessages(prev => [...prev, userMessage]);

    const selectedAssetPaths = documents
      .filter(d => selectedDocuments.includes(d.id))
      .map(d => d.asset_path);

    if (selectedProject) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/nlp/index/answer/${selectedProject}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: content,
              assets: selectedAssetPaths,
            }),
          }
        );
        const data = await response.json();
        let aiContent = data.answer || "No answer received.";
        if (data.image_path) {
          aiContent += `\n[IMAGE:${data.image_path}]`;
        }
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: aiContent,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          }),
          projectId: selectedProject || undefined,
        };
        setMessages(prev => [...prev, aiMessage]);
      } catch (error) {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "Sorry, there was an error getting the answer.",
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          }),
          projectId: selectedProject || undefined,
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    }
  };

  const handleSelectProject = (projectId: string) => {
    setSelectedProject(projectId);
    setSelectedDocuments([]);
    setMessages([]);
    // Remove chat history for this project
    localStorage.removeItem(`chat_history_${projectId}`);
    // Fetch all assets and update document counts
    fetchDocuments(selectedProject);
  };

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocuments(prev => {
      if (prev.includes(documentId)) {
        return prev.filter(id => id !== documentId);
      } else {
        return [...prev, documentId];
      }
    });
  };

  const handleCreateProject = async (projectName: string) => {
    try {
      const url = `${API_BASE_URL}/api/v1/data/project/create/${projectName}`;
      const response = await fetch(url, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      await fetchProjects();
      // After creating, select the new project and reset its chat history
      setSelectedProject(projectName);
      setSelectedDocuments([]);
      setMessages([]);
      localStorage.removeItem(`chat_history_${projectName}`);
      // Fetch all assets and update document counts
      fetchDocuments(selectedProject);
      
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  const onDeleteProject = async (projectId: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/data/projects/delete`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_name: projectId }),
      });
      const data = await res.json();
      if (data.signal && data.signal.includes('deleted successfully')) {
        setProjects(prev => prev.filter(p => p.id !== projectId));
        // Remove chat history for this project
        localStorage.removeItem(`chat_history_${projectId}`);
        fetchDocuments(selectedProject);
      } else {
        console.error('Failed to delete project:', data);
      }
    } catch (err) {
      console.error('Error deleting project:', err);
    }
  };

  function mapApiProjects(apiProjects: string[]): Project[] {
    return apiProjects.map((name, idx) => ({
      id: name,
      name,
      color: 'blue',
      isStarred: false,
      documentCount: 0,
      lastUpdated: '',
    }));
  }

  return {
    projects,
    documents,
    selectedProject,
    selectedDocuments: selectedDocumentObjects,
    messages,
    currentProject,
    projectSearchTerm,
    documentSearchTerm,
    handleSendMessage,
    handleSelectProject,
    handleDocumentSelect,
    setProjectSearchTerm,
    setDocumentSearchTerm,
    onCreateProject: handleCreateProject,
    onDeleteProject,
    fetchDocuments,
  };
};
