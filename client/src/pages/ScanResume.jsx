import React, { useState } from 'react';
import ResumePreviewComponent from '../components/ResumeScanner/resumePreviewComponent';
import ResumeUploadComponent from '../components/ResumeScanner/resumeUploadComponent';

const ScanResume = () => {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileUpload = (uploadedFile, jd) => {
    // If called with both parameters (from submit button)
    if (jd !== undefined) {
      scanResume(uploadedFile, jd);
    } else {
      // Just setting the file
      setFile(uploadedFile);
    }
  };

  const handleJdChange = (jd) => {
    setJobDescription(jd);
  };

  const scanResume = async (resumeFile, jd) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', resumeFile);
      formData.append('job_description', jd);

      const response = await fetch('http://localhost:5000/scan-resume/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        console.error('Error scanning resume:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-black mb-8 text-center">
          Resume ATS Scanner
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left side - Upload components */}
          <div className="space-y-6">
            <ResumeUploadComponent 
              onFileUpload={handleFileUpload}
              onJdChange={handleJdChange}
              isLoading={isLoading}
            />
          </div>

          {/* Right side - Preview and results */}
          <div className="space-y-6">
            <ResumePreviewComponent 
              file={file}
              isLoading={isLoading}
              results={results}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanResume;