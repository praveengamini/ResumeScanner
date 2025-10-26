import React, { useState } from 'react';
import { Upload } from 'lucide-react';

const ResumeUploadComponent = ({ onFileUpload, onJdChange, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      onFileUpload(droppedFile);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      onFileUpload(selectedFile);
    }
  };

  const handleJdChange = (e) => {
    setJd(e.target.value);
    onJdChange(e.target.value);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h2 className="text-xl font-semibold text-black mb-4">Upload Resume</h2>
        
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive ? 'border-green-500 bg-green-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleChange}
            className="hidden"
            id="file-upload"
            disabled={isLoading}
          />
          
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <p className="text-black font-medium mb-2">
              {file ? file.name : 'Drop your resume here or click to browse'}
            </p>
            <p className="text-gray-600 text-sm">
              Supports PDF, DOC, DOCX files
            </p>
          </label>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h2 className="text-xl font-semibold text-black mb-4">Job Description</h2>
        <textarea
          value={jd}
          onChange={handleJdChange}
          placeholder="Paste the job description here..."
          className="w-full h-40 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-black"
          disabled={isLoading}
        />
      </div>

      <button
        onClick={() => onFileUpload(file, jd)}
        disabled={!file || !jd.trim() || isLoading}
        className="w-full bg-green-500 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Scanning Resume...' : 'Scan Resume'}
      </button>
    </div>
  );
};

export default ResumeUploadComponent;