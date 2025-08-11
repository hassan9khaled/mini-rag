import React, { useState } from 'react';
import { Search, Plus, Star, FileText, Calendar, Trash } from 'lucide-react';
import { Project } from '../../types';
import { CreateProjectModal } from '../Projects/CreateProjectModal';
import toast from 'react-hot-toast';

interface ProjectsSidebarProps {
  projects: Project[];
  selectedProject: string | null;
  onSelectProject: (projectId: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
  onCreateProject: (projectName: string) => void;
  onDeleteProject: (projectId: string) => void;
}

export const ProjectsSidebar: React.FC<ProjectsSidebarProps> = ({
  projects,
  selectedProject,
  onSelectProject,
  searchTerm,
  onSearchChange,
  onCreateProject,
  onDeleteProject,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getColorClasses = (color: string, isSelected: boolean) => {
    const colorMap = {
      blue: isSelected ? 'bg-blue-50 border-blue-200' : 'hover:bg-blue-50',
      green: isSelected ? 'bg-green-50 border-green-200' : 'hover:bg-green-50',
      purple: isSelected ? 'bg-purple-50 border-purple-200' : 'hover:bg-purple-50',
      orange: isSelected ? 'bg-orange-50 border-orange-200' : 'hover:bg-orange-50',
      red: isSelected ? 'bg-red-50 border-red-200' : 'hover:bg-red-50',
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
  };

  const getIndicatorColor = (color: string) => {
    const colorMap = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      orange: 'bg-orange-500',
      red: 'bg-red-500',
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
  };

  const filteredProjects = projects.filter(
    (project) =>
      typeof project.name === 'string' &&
      project.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = (projectName: string) => {
    onCreateProject(projectName);
    toast.success(`Project "${projectName}" created successfully`);
    setIsModalOpen(false);
  };

  const handleDelete = (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation(); // Prevent selecting the project when deleting
    onDeleteProject(projectId);
    toast.success(`Project "${projectId}" deleted successfully`);
  };

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col flex-1 h-full">
      <div className="p-2 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Projects</h2>
          <button
            onClick={() => setIsModalOpen(true)}
            className="p-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredProjects.map((project) => (
          <div
            key={project.id}
            onClick={() => onSelectProject(project.id)}
            className={`p-4 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
              selectedProject === project.id
                ? `${getColorClasses(project.color, true)} border-2`
                : `${getColorClasses(project.color, false)} border-transparent hover:border-gray-200`
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getIndicatorColor(project.color)}`} />
                <h3 className="font-semibold text-gray-900 text-sm">{project.name}</h3>
                {project.isStarred && (
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                )}
              </div>
              <button
                onClick={(e) => handleDelete(e, project.id)}
                className="p-1 rounded-full hover:bg-gray-200 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
              <div className="flex items-center space-x-1">
                <FileText className="w-3 h-3" />
                <span>{project.documentCount ?? 0} docs</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>{project.lastUpdated}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreate={handleCreate}
      />
    </div>
  );
};