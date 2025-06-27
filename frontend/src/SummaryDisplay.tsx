import { ParsedAPIResponse } from "./types";

interface SummaryDisplayProps {
  data: ParsedAPIResponse | null;
}

function SummaryDisplay({ data }: SummaryDisplayProps) {
  if (!data) return null;

  // Destructure for easier access
  const { summary, title } = data;
  const { gist, analogy, key_findings, why_it_matters, key_terms } = summary;

  return (
    // Main container with vertical padding
    <div className="w-full mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-12">
      
      {/* --- Paper Title (HIGH CONTRAST) --- */}
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
          {title}
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          A Simple Explanation
        </p>
      </div>

      {/* --- Main Summary Cards Section --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* The Gist Card */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">🎯</span>
              <h2 className="text-xl font-bold text-gray-800">The Gist</h2>
            </div>
            <p className="text-base text-gray-700 leading-relaxed">
              {gist}
            </p>
          </div>
        </div>

        {/* The Big Idea Card */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">💡</span>
              <h2 className="text-xl font-bold text-gray-800">The Big Idea</h2>
            </div>
            <p className="text-base text-gray-700 leading-relaxed">
              {analogy}
            </p>
          </div>
        </div>

        {/* Why It Matters Card */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">🌍</span>
              <h2 className="text-xl font-bold text-gray-800">Why It Matters</h2>
            </div>
            <p className="text-base text-gray-700 leading-relaxed">
              {why_it_matters}
            </p>
          </div>
        </div>
      </div>

      {/* --- Key Findings and Key Terms Section --- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* --- Key Findings Card --- */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200">
          <div className="p-6 border-b border-gray-200">
             <div className="flex items-center gap-4">
              <span className="text-3xl">📈</span>
              <h2 className="text-2xl font-bold text-gray-800">Key Findings</h2>
            </div>
          </div>
          <div className="p-6">
            <ul className="space-y-4">
              {key_findings.map((finding, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="text-blue-500 font-bold text-xl mt-1">▪</span>
                  <span className="text-lg text-gray-700 leading-relaxed">{finding}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* --- Key Terms Card --- */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-3xl">📚</span>
              <h2 className="text-2xl font-bold text-gray-800">Key Terms Explained</h2>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {key_terms.map((item, index) => (
              <div key={index} className="p-4">
                <h3 className="font-bold text-xl text-gray-900 mb-2">
                  {item.term}
                </h3>
                <p className="text-lg text-gray-700 leading-relaxed">
                  {item.definition}
                </p>
              </div>
            ))}
          </div>
        </div>
        
      </div>
    </div>
  );
}

export default SummaryDisplay;
