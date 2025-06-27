import { ParsedAPIResponse } from "./types";

interface SummaryDisplayProps {
  data: ParsedAPIResponse | null;
}

function SummaryDisplay({ data }: SummaryDisplayProps) {
  if (!data) return null;

  const { summary, title } = data;

  const sections = [
    {
      icon: "🎯",
      title: "The Gist (1-Liner)",
      content: summary.gist,
      bgColor: "from-blue-50 to-indigo-50",
      borderColor: "border-blue-200"
    },
    {
      icon: "💡",
      title: "The Big Idea (Analogy)",
      content: summary.analogy,
      bgColor: "from-purple-50 to-pink-50",
      borderColor: "border-purple-200"
    },
    ...(summary.experimental_details ? [{
      icon: "🔬",
      title: "Experimental Details",
      content: summary.experimental_details,
      bgColor: "from-green-50 to-emerald-50",
      borderColor: "border-green-200"
    }] : []),
    {
      icon: "🌍",
      title: "Why It Matters",
      content: summary.why_it_matters,
      bgColor: "from-orange-50 to-red-50",
      borderColor: "border-orange-200"
    }
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Paper Title */}
      <div className="bg-white/80 backdrop-blur-sm border border-white/20 rounded-3xl shadow-xl p-8 mb-8 text-center">
        <div className="inline-flex items-center gap-3 mb-4">
          <span className="text-3xl">📄</span>
          <h1 className="text-2xl font-bold text-slate-800">Paper Summary</h1>
        </div>
        <h2 className="text-xl font-semibold text-slate-700 leading-relaxed">
          {title}
        </h2>
      </div>

      {/* Summary Sections */}
      <div className="grid gap-6 mb-8">
        {sections.map((section, index) => (
          <div 
            key={index}
            className="bg-white/80 backdrop-blur-sm border border-white/20 rounded-3xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className={`p-6 bg-gradient-to-r ${section.bgColor} border-b ${section.borderColor}`}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">{section.icon}</span>
                <h3 className="text-xl font-semibold text-slate-800">
                  {section.title}
                </h3>
              </div>
            </div>
            <div className="p-6">
              <p className="text-slate-700 leading-relaxed text-lg">
                {section.content}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Key Findings */}
      <div className="bg-white/80 backdrop-blur-sm border border-white/20 rounded-3xl shadow-xl overflow-hidden mb-8 hover:shadow-2xl transition-all duration-300" style={{ animationDelay: '400ms' }}>
        <div className="p-6 bg-gradient-to-r from-teal-50 to-cyan-50 border-b border-teal-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📋</span>
            <h3 className="text-xl font-semibold text-slate-800">
              Key Findings
            </h3>
          </div>
        </div>
        <div className="p-6">
          <ul className="space-y-3">
            {summary.key_findings.map((finding: string, index: number) => (
              <li key={index} className="flex items-start gap-3">
                <span className="text-teal-500 text-lg font-bold mt-1">•</span>
                <span className="text-slate-700 leading-relaxed">{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Key Terms */}
      <div className="bg-white/80 backdrop-blur-sm border border-white/20 rounded-3xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300" style={{ animationDelay: '500ms' }}>
        <div className="p-6 bg-gradient-to-r from-violet-50 to-purple-50 border-b border-violet-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📚</span>
            <h3 className="text-xl font-semibold text-slate-800">
              Key Terms
            </h3>
          </div>
        </div>
        <div className="p-6">
          <div className="grid gap-4">
            {summary.key_terms.map((item, index: number) => (
              <div key={index} className="bg-white/60 rounded-2xl p-4 border border-violet-100">
                <h4 className="font-semibold text-violet-700 mb-2">
                  {item.term}
                </h4>
                <p className="text-slate-700 leading-relaxed">
                  {item.definition}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center mt-12 p-6">
        <p className="text-slate-500 text-sm">
          ✨ Simplified by AI • Made for curious minds
        </p>
      </div>
    </div>
  );
}

export default SummaryDisplay;
