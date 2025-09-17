import React, { useState, useEffect } from 'react';
import { FileText, Loader2, CheckCircle, AlertCircle, XCircle, Eye, Download, ZoomIn } from 'lucide-react';

const ResumePreviewComponent = ({ file, isLoading, results }) => {
  const [fileContent, setFileContent] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState(null);
  const [scanPosition, setScanPosition] = useState(0);

  useEffect(() => {
    if (file) {
      generatePreview(file);
    }
    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [file]);

  useEffect(() => {
    let scanInterval;
    if (isLoading) {
      // Start scanning animation
      scanInterval = setInterval(() => {
        setScanPosition(prev => (prev >= 100 ? 0 : prev + 2));
      }, 50);
    } else {
      setScanPosition(0);
    }

    return () => {
      if (scanInterval) clearInterval(scanInterval);
    };
  }, [isLoading]);

  const generatePreview = async (file) => {
    setIsLoadingPreview(true);
    setPreviewError(null);
    
    try {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      
      if (file.type === 'application/pdf') {
        setFileContent({ type: 'pdf', url });
      } 
      else if (file.type.includes('text')) {
        const text = await file.text();
        setFileContent({ type: 'text', content: text });
      }
      else {
        setFileContent({ 
          type: 'document', 
          name: file.name,
          size: file.size,
          url: url
        });
      }
    } catch (error) {
      setPreviewError('Failed to load preview');
      console.error('Preview error:', error);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  if (!file && !results) {
    return (
      <div className="bg-white p-6 rounded-lg border-2 border-green-500 h-96 flex items-center justify-center">
        <div className="text-center">
          <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <p className="text-gray-600">Upload a resume to see preview</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border-2 border-green-500 h-[600px]">
        {/* File Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center">
            <div className="relative">
              <FileText className="h-6 w-6 text-green-500" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-black">{file?.name || 'Resume'}</h3>
              <p className="text-xs text-gray-500">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Processing...'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center text-green-500 text-xs font-medium">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Scanning...
            </div>
          </div>
        </div>

        {/* Resume Preview with Scanning Animation */}
        <div className="relative h-[540px] overflow-hidden">
          {/* Resume Content Background */}
          <div className="absolute inset-0 p-6">
            {fileContent ? (
              <div className="h-full opacity-40">
                {fileContent.type === 'pdf' && (
                  <iframe 
                    src={fileContent.url}
                    className="w-full h-full border rounded bg-white"
                    title="Resume Preview"
                  />
                )}
                
                {fileContent.type === 'text' && (
                  <div className="h-full overflow-hidden bg-white border rounded">
                    <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono p-4 h-full overflow-hidden">
                      {fileContent.content}
                    </pre>
                  </div>
                )}
                
                {fileContent.type === 'document' && (
                  <div className="h-full flex flex-col bg-white border rounded p-6">
                    <div className="text-center mb-4">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <h3 className="text-lg font-semibold text-gray-700">{fileContent.name}</h3>
                    </div>
                    <div className="space-y-3 text-gray-600 text-sm">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                      <div className="h-4 bg-gray-200 rounded w-4/5"></div>
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full bg-white border rounded flex items-center justify-center">
                <div className="text-center opacity-40">
                  <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <div className="space-y-3 w-80">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6 mx-auto"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3 mx-auto"></div>
                    <div className="h-4 bg-gray-200 rounded w-4/5 mx-auto"></div>
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Scanning Line Animation */}
          <div className="absolute inset-0 pointer-events-none">
            <div 
              className="absolute left-0 right-0 h-1 bg-green-500 rounded-full shadow-lg shadow-green-400/50"
              style={{
                top: `${scanPosition}%`,
                transition: 'top 0.05s ease-out',
                zIndex: 10
              }}
            >
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-green-500 rounded-full"></div>
              <div className="absolute -top-1 left-1/4 transform -translate-x-1/2 w-2 h-2 bg-green-400 rounded-full"></div>
              <div className="absolute -top-1 left-3/4 transform -translate-x-1/2 w-2 h-2 bg-green-400 rounded-full"></div>
            </div>
          </div>

          {/* Scanning Overlay Effect */}
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              background: `linear-gradient(to bottom, 
                transparent 0%, 
                rgba(34, 197, 94, 0.1) ${Math.max(0, scanPosition - 10)}%, 
                rgba(34, 197, 94, 0.2) ${scanPosition}%, 
                rgba(34, 197, 94, 0.1) ${Math.min(100, scanPosition + 10)}%, 
                transparent 100%)`
            }}
          ></div>

          {/* Status Information */}
          <div className="absolute bottom-6 left-6 right-6">
            <div className="bg-white bg-opacity-95 backdrop-blur-sm rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <Loader2 className="h-5 w-5 text-green-500 animate-spin mr-2" />
                  <span className="text-black font-medium">Scanning Resume...</span>
                </div>
                <div className="text-sm text-gray-600">Analyzing ATS compatibility</div>
              </div>
              
              {/* Progress indicators */}
              <div className="grid grid-cols-3 gap-4 text-xs">
                <div className="flex items-center text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  Extracting content
                </div>
                <div className="flex items-center text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" style={{ animationDelay: '1s' }}></div>
                  Analyzing keywords
                </div>
                <div className="flex items-center text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" style={{ animationDelay: '2s' }}></div>
                  Calculating score
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (results) {
    return (
      <div className="space-y-4 max-h-screen overflow-y-auto">
        {/* ATS Score */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-black mb-2">{results.candidate_name}</h3>
            <div className="flex items-center justify-center space-x-2">
              <div className="text-4xl font-bold text-green-500">{results.ats_score}%</div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <p className="text-gray-600">ATS Score</p>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
          <h4 className="font-semibold text-black mb-4">Score Breakdown</h4>
          <div className="space-y-3">
            {Object.entries(results.score_breakdown).map(([key, value], index) => (
              <div key={key} className="flex justify-between items-center">
                <span className="text-black capitalize">{key.replace('_', ' ')}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-1000 ease-out" 
                      style={{ 
                        width: `${value}%`,
                        animationDelay: `${index * 0.2}s`
                      }}
                    ></div>
                  </div>
                  <span className="text-black font-medium w-8">{value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strengths */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
          <h4 className="font-semibold text-black mb-4 flex items-center">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            Strengths
          </h4>
          <ul className="space-y-2">
            {results.strengths.map((strength, index) => (
              <li key={index} className="flex items-start animate-slideIn" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-black text-sm">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Gaps */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.3s' }}>
          <h4 className="font-semibold text-black mb-4 flex items-center">
            <XCircle className="h-5 w-5 text-red-500 mr-2" />
            Areas for Improvement
          </h4>
          <ul className="space-y-2">
            {results.gaps.map((gap, index) => (
              <li key={index} className="flex items-start animate-slideIn" style={{ animationDelay: `${0.4 + index * 0.1}s` }}>
                <XCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-black text-sm">{gap}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Recommendations */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.4s' }}>
          <h4 className="font-semibold text-black mb-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-orange-500 mr-2" />
            Recommendations
          </h4>
          <ul className="space-y-2">
            {results.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start animate-slideIn" style={{ animationDelay: `${0.5 + index * 0.1}s` }}>
                <AlertCircle className="h-4 w-4 text-orange-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-black text-sm">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Keywords Analysis */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.5s' }}>
          <h4 className="font-semibold text-black mb-4">Keywords Analysis</h4>
          
          <div className="mb-4">
            <h5 className="font-medium text-black mb-2 flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Matching Keywords
            </h5>
            <div className="flex flex-wrap gap-2">
              {results.matching_keywords.map((keyword, index) => (
                <span 
                  key={index} 
                  className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full animate-fadeIn"
                  style={{ animationDelay: `${0.6 + index * 0.05}s` }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h5 className="font-medium text-black mb-2 flex items-center">
              <XCircle className="h-4 w-4 text-red-500 mr-2" />
              Missing Keywords
            </h5>
            <div className="flex flex-wrap gap-2">
              {results.missing_keywords.map((keyword, index) => (
                <span 
                  key={index} 
                  className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full animate-fadeIn"
                  style={{ animationDelay: `${0.7 + index * 0.05}s` }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Overall Assessment */}
        <div className="bg-white p-6 rounded-lg border-2 border-green-500 animate-fadeIn" style={{ animationDelay: '0.6s' }}>
          <h4 className="font-semibold text-black mb-4">Overall Assessment</h4>
          <p className="text-black text-sm leading-relaxed">{results.overall_assessment}</p>
        </div>
      </div>
    );
  }

  // Show actual file preview when file is uploaded but not yet scanning
  if (file && !isLoading && !results) {
    return (
      <div className="bg-white rounded-lg border-2 border-green-500 h-[600px] flex flex-col">
        {/* File Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center">
            <FileText className="h-6 w-6 text-green-500" />
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-black">{file.name}</h3>
              <p className="text-xs text-gray-500">
                {(file.size / 1024).toFixed(1)} KB • {file.type || 'Document'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Eye className="h-4 w-4 text-green-500" />
            <ZoomIn className="h-4 w-4 text-gray-400" />
            <Download className="h-4 w-4 text-gray-400" />
          </div>
        </div>

        {/* File Preview Content */}
        <div className="flex-1 p-4 h-[540px]">
          {isLoadingPreview ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Loader2 className="h-8 w-8 text-green-500 animate-spin mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Loading preview...</p>
              </div>
            </div>
          ) : previewError ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                <p className="text-red-600 text-sm">{previewError}</p>
              </div>
            </div>
          ) : fileContent ? (
            <div className="h-full">
              {fileContent.type === 'pdf' && (
                <iframe 
                  src={fileContent.url}
                  className="w-full h-full border rounded"
                  title="Resume Preview"
                />
              )}
              
              {fileContent.type === 'text' && (
                <div className="h-full overflow-y-auto">
                  <pre className="text-xs text-black whitespace-pre-wrap font-mono p-4 bg-gray-50 rounded">
                    {fileContent.content}
                  </pre>
                </div>
              )}
              
              {fileContent.type === 'document' && (
                <div className="h-full flex flex-col items-center justify-center bg-gray-50 rounded">
                  <div className="text-center">
                    <FileText className="h-16 w-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-black mb-2">{fileContent.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">
                      {(fileContent.size / 1024).toFixed(1)} KB
                    </p>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-700">Document ready for analysis</p>
                      <p className="text-xs text-gray-500">Add job description and click scan to analyze</p>
                    </div>
                    <a 
                      href={fileContent.url} 
                      download={fileContent.name}
                      className="inline-flex items-center mt-4 px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </a>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <CheckCircle className="w-16 h-16 bg-green-100 text-green-500 rounded-full p-4 mx-auto mb-4" />
                <p className="text-black font-medium mb-2">File Ready</p>
                <p className="text-gray-600 text-sm">Add job description and click scan</p>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return null;
};

export default ResumePreviewComponent;