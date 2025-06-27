import { ParsedAPIResponse } from "./types";
import FigureDisplay from "./FigureDisplay";

interface SummaryDisplayProps {
  data: ParsedAPIResponse | null;
}

function SummaryDisplay({ data }: SummaryDisplayProps) {
  if (!data) return null;

  // Destructure for easier access
  const { summary, title, figures } = data;
  const { gist, analogy, key_findings, why_it_matters, key_terms } = summary;

  return (
    <div className="w-full">
      {/* Hero Title Section - Apple Style */}
      <div className="bg-gradient-to-br from-gray-900 via-black to-gray-800 py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-lg mb-8">
            <span className="text-2xl">📄</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
            {title}
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Simplified for everyone to understand
          </p>
        </div>
      </div>

      {/* Main Content with Apple-style sections */}
      <div className="bg-white">
        {/* The Gist - Hero Section */}
        <div className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8">
              The 
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {" "}Essence
              </span>
            </h2>
            <p className="text-2xl text-gray-700 leading-relaxed max-w-4xl mx-auto">
              {gist}
            </p>
          </div>
        </div>

        {/* The Big Idea - Analogy Section */}
        <div className="py-20 bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8">
                Think of it
                <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {" "}like this
                </span>
              </h2>
            </div>
            <div className="bg-white rounded-3xl shadow-2xl p-12">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-8">
                  <span className="text-3xl">💡</span>
                </div>
                <p className="text-xl text-gray-700 leading-relaxed">
                  {analogy}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Figures Section */}
        {figures && figures.length > 0 && summary.figures && (
          <FigureDisplay 
            extractedFigures={figures} 
            figureDescriptions={summary.figures} 
          />
        )}

        {/* Key Findings Section */}
        <div className="py-20 bg-gradient-to-br from-green-50 to-teal-50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8">
                Key
                <span className="bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
                  {" "}Discoveries
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {key_findings.map((finding, index) => (
                <div key={index} className="bg-white rounded-3xl shadow-xl p-8 transform transition-all duration-300 hover:scale-105">
                  <div className="flex items-center mb-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center">
                      <span className="text-white font-bold">{index + 1}</span>
                    </div>
                  </div>
                  <p className="text-lg text-gray-700 leading-relaxed">
                    {finding}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Why It Matters Section */}
        <div className="py-20 bg-gradient-to-br from-orange-50 to-red-50">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8">
                Why this
                <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  {" "}matters
                </span>
              </h2>
            </div>
            <div className="bg-white rounded-3xl shadow-2xl p-12">
              <div className="flex items-start gap-8">
                <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                  <span className="text-3xl">🌍</span>
                </div>
                <p className="text-xl text-gray-700 leading-relaxed">
                  {why_it_matters}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Terms Section */}
        <div className="py-20 bg-gradient-to-br from-indigo-50 to-blue-50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8">
                Key
                <span className="bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
                  {" "}Terms
                </span>
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                The essential vocabulary you need to understand this research
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {key_terms.map((item, index) => (
                <div key={index} className="bg-white rounded-3xl shadow-xl p-8 transform transition-all duration-300 hover:scale-105">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-2xl flex items-center justify-center">
                      <span className="text-white font-bold text-sm">
                        {item.term.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      {item.term}
                    </h3>
                  </div>
                  <p className="text-lg text-gray-700 leading-relaxed">
                    {item.definition}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SummaryDisplay;
