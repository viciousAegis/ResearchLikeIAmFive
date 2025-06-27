import { ParsedAPIResponse } from "./types";

const sectionStyle = {
  marginTop: "2rem",
  borderTop: "1px solid var(--pico-muted-border-color)",
  paddingTop: "2rem",
};

interface SummaryDisplayProps {
  data: ParsedAPIResponse | null;
}

function SummaryDisplay({ data }: SummaryDisplayProps) {
  if (!data) return null;

  const { summary, title } = data;

  return (
    <article style={{ marginTop: "2rem" }}>
      <h1>{title}</h1>

      <div style={sectionStyle}>
        <h2>🎯 The Gist (1-Liner)</h2>
        <p>{summary.gist}</p>
      </div>

      <div style={sectionStyle}>
        <h2>💡 The Big Idea (Analogy)</h2>
        <p>{summary.analogy}</p>
      </div>

      {summary.experimental_details && (
        <div style={sectionStyle}>
          <h2>🔬 Experimental Details</h2>
          <p>{summary.experimental_details}</p>
        </div>
      )}

      <div style={sectionStyle}>
        <h2>📋 Key Findings</h2>
        <ul>
          {summary.key_findings.map((finding: string, index: number) => (
            <li key={index}>{finding}</li>
          ))}
        </ul>
      </div>

      <div style={sectionStyle}>
        <h2>🌍 Why It Matters</h2>
        <p>{summary.why_it_matters}</p>
      </div>

      <div style={sectionStyle}>
        <h2>📚 Key Terms</h2>
        <div>
          {summary.key_terms.map((item, index: number) => (
            <p key={index}>
              <strong>{item.term}:</strong> {item.definition}
            </p>
          ))}
        </div>
      </div>
    </article>
  );
}

export default SummaryDisplay;
