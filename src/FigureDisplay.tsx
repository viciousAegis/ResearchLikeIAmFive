import { useState } from 'react';
import { ExtractedFigure, Figure } from './types';

interface FigureDisplayProps {
  extractedFigures: ExtractedFigure[];
  figureDescriptions: Figure[];
}

function FigureDisplay({ extractedFigures, figureDescriptions }: FigureDisplayProps) {
  const [selectedFigure, setSelectedFigure] = useState<number | null>(null);
  const [imageErrors, setImageErrors] = useState<{ [key: number]: boolean }>({});

  if (!extractedFigures.length) return null;

  // Match extracted figures with their descriptions
  const matchedFigures = extractedFigures.map((extracted, index) => {
    const description = figureDescriptions.find(fig => fig.figure_index === index) || {
      caption: `Figure ${index + 1}`,
      importance: "This figure provides visual context for the research.",
      figure_index: index
    };
    return { ...extracted, ...description };
  });

  const handleImageError = (index: number) => {
    setImageErrors(prev => ({ ...prev, [index]: true }));
  };

  return (
    <div className="w-full py-16 bg-gradient-to-br from-gray-900 via-black to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header - Apple Style */}
        <div className="text-center mb-16">
          <h2 className="text-5xl sm:text-6xl font-bold text-white mb-6">
            Visual
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {" "}Insights
            </span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Key figures from the research that tell the story of discovery
          </p>
        </div>

        {/* Figure Grid - Apple Demo Style */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
          {matchedFigures.map((figure, index) => (
            <div
              key={index}
              className="group cursor-pointer"
              onClick={() => setSelectedFigure(selectedFigure === index ? null : index)}
            >
              {/* Figure Card */}
              <div className="bg-white rounded-3xl p-8 shadow-2xl transform transition-all duration-500 hover:scale-105 hover:shadow-3xl">
                {/* Figure Image */}
                <div className="relative overflow-hidden rounded-2xl mb-6 bg-gray-50">
                  {imageErrors[index] ? (
                    <div className="w-full h-64 flex items-center justify-center bg-gray-100 text-gray-500">
                      <div className="text-center">
                        <span className="text-4xl mb-2 block">📊</span>
                        <p className="text-sm">Figure preview unavailable</p>
                      </div>
                    </div>
                  ) : (
                    <img
                      src={figure.data}
                      alt={figure.caption}
                      className="w-full h-64 object-contain transition-transform duration-700 group-hover:scale-110"
                      onError={() => handleImageError(index)}
                    />
                  )}
                  <div className="absolute top-4 right-4 bg-black/20 backdrop-blur-sm rounded-full px-3 py-1">
                    <span className="text-white text-sm font-medium">Fig {index + 1}</span>
                  </div>
                </div>

                {/* Figure Info */}
                <div className="space-y-4">
                  <h3 className="text-xl font-bold text-gray-900 leading-tight">
                    {figure.caption}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {figure.importance}
                  </p>
                </div>

                {/* Expand Indicator */}
                <div className="flex items-center justify-center mt-6">
                  <div className={`w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center transform transition-transform duration-300 ${selectedFigure === index ? 'rotate-180' : ''}`}>
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Expanded Figure Modal - Apple Style */}
        {selectedFigure !== null && (
          <div 
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in"
            onClick={() => setSelectedFigure(null)}
          >
            <div 
              className="relative max-w-6xl w-full max-h-[90vh] bg-white rounded-3xl overflow-hidden shadow-2xl transform transition-all duration-500 scale-100"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedFigure(null)}
                className="absolute top-6 right-6 z-10 w-10 h-10 bg-black/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-black/30 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Modal Content */}
              <div className="flex flex-col lg:flex-row h-full">
                {/* Image Section */}
                <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
                  <img
                    src={matchedFigures[selectedFigure].data}
                    alt={matchedFigures[selectedFigure].caption}
                    className="max-w-full max-h-full object-contain"
                  />
                </div>

                {/* Description Section */}
                <div className="lg:w-96 p-8 flex flex-col justify-center space-y-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
                      <span className="text-white font-bold">Fig {selectedFigure + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Figure {selectedFigure + 1}</p>
                      <p className="text-xs text-gray-400">Page {matchedFigures[selectedFigure].page}</p>
                    </div>
                  </div>

                  <h3 className="text-2xl font-bold text-gray-900 leading-tight">
                    {matchedFigures[selectedFigure].caption}
                  </h3>

                  <p className="text-gray-600 leading-relaxed">
                    {matchedFigures[selectedFigure].importance}
                  </p>

                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-500">
                      Tap anywhere outside to close
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FigureDisplay;
