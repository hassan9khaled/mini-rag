import React from 'react';
import { Header } from './components/Header/Header';
import { ProjectsSidebar } from './components/Sidebar/ProjectsSidebar';
import { ChatArea } from './components/Chat/ChatArea';
import { ResourcesSidebar } from './components/Resources/ResourcesSidebar';
import { useRAGSystem } from './hooks/useRAGSystem';
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import { ErrorBoundary } from './components/ErrorBoundary';
import { Toaster } from 'react-hot-toast';

function App() {
  const {
    projects,
    documents,
    selectedProject,
    selectedDocuments,
    messages,
    currentProject,
    projectSearchTerm,
    documentSearchTerm,
    handleSendMessage,
    handleSelectProject,
    handleDocumentSelect,
    setProjectSearchTerm,
    setDocumentSearchTerm,
    onCreateProject,
    onDeleteProject,
    fetchDocuments,
  } = useRAGSystem();

  // Show loading only if projects are undefined/null (not just empty)
  if (projects === undefined || projects === null) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        Loading...
      </div>
    );
  }

  // If there are no projects, clear selectedProject to hide chat/resources panels
  const noProjects = projects.length === 0;
  const noSelectedProject = !selectedProject || !projects.find(p => p.id === selectedProject);

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      <Header />
      <ErrorBoundary>
        <PanelGroup direction="horizontal" className="flex-1">
          <Panel defaultSize={20} minSize={15}>
            <ProjectsSidebar
              projects={projects}
              selectedProject={selectedProject}
              onSelectProject={handleSelectProject}
              searchTerm={projectSearchTerm}
              onSearchChange={setProjectSearchTerm}
              onCreateProject={onCreateProject}
              onDeleteProject={onDeleteProject}
            />
            <Toaster position="top-center" />
          </Panel>
          <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors cursor-ew-resize" />
          <Panel defaultSize={60} minSize={30}>
            {noProjects || noSelectedProject ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 text-lg">
                {/* Blank panel */}
              </div>
            ) : (
              <ChatArea
                messages={messages}
                selectedDocuments={selectedDocuments}
                projectName={currentProject?.name || 'Unknown Project'}
                onSendMessage={handleSendMessage}
              />
            )}
          </Panel>
          <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors cursor-ew-resize" />
          <Panel defaultSize={20} minSize={15}>
            {noProjects || noSelectedProject ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 text-lg">
                {/* Blank panel */}
              </div>
            ) : (
              <ResourcesSidebar
                documents={documents}
                selectedDocuments={selectedDocuments.map(d => d.id)}
                onDocumentSelect={handleDocumentSelect}
                searchTerm={documentSearchTerm}
                onSearchChange={setDocumentSearchTerm}
                selectedProject={selectedProject}
                fetchDocuments={fetchDocuments}
                />
              )
            }
            <Toaster position="top-center" />
          </Panel>
        </PanelGroup>
      </ErrorBoundary>
    </div>
  );
}

export default App;