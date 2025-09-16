const ResultsComponent = ({ results }) => {
  if (!results) {
    return (
      <div className="bg-white p-6 rounded-lg border-2 border-green-500 h-96 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <p className="text-gray-600">Results will appear here after scanning</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-screen overflow-y-auto">
      {/* ATS Score */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
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
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4">Score Breakdown</h4>
        <div className="space-y-3">
          {Object.entries(results.score_breakdown).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center">
              <span className="text-black capitalize">{key.replace('_', ' ')}</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${value}%` }}
                  ></div>
                </div>
                <span className="text-black font-medium w-8">{value}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4 flex items-center">
          <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
          Strengths
        </h4>
        <ul className="space-y-2">
          {results.strengths.map((strength, index) => (
            <li key={index} className="flex items-start">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-black text-sm">{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Gaps */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4 flex items-center">
          <XCircle className="h-5 w-5 text-red-500 mr-2" />
          Areas for Improvement
        </h4>
        <ul className="space-y-2">
          {results.gaps.map((gap, index) => (
            <li key={index} className="flex items-start">
              <XCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-black text-sm">{gap}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4 flex items-center">
          <AlertCircle className="h-5 w-5 text-orange-500 mr-2" />
          Recommendations
        </h4>
        <ul className="space-y-2">
          {results.recommendations.map((recommendation, index) => (
            <li key={index} className="flex items-start">
              <AlertCircle className="h-4 w-4 text-orange-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-black text-sm">{recommendation}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Keywords Analysis */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4">Keywords Analysis</h4>
        
        <div className="mb-4">
          <h5 className="font-medium text-black mb-2 flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            Matching Keywords
          </h5>
          <div className="flex flex-wrap gap-2">
            {results.matching_keywords.map((keyword, index) => (
              <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
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
              <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Overall Assessment */}
      <div className="bg-white p-6 rounded-lg border-2 border-green-500">
        <h4 className="font-semibold text-black mb-4">Overall Assessment</h4>
        <p className="text-black text-sm leading-relaxed">{results.overall_assessment}</p>
      </div>
    </div>
  );
};

export { ResumePreviewComponent, ResultsComponent };