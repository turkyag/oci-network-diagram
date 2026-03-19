import { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, AlertCircle, Info } from 'lucide-react';

interface Warning {
  severity: string;
  code: string;
  message: string;
  affected_resources: string[];
}

interface WarningsBannerProps {
  warnings: Warning[];
}

function SeverityIcon({ severity }: { severity: string }) {
  switch (severity) {
    case 'error':
      return <AlertCircle size={12} className="warning-severity-icon error" />;
    case 'info':
      return <Info size={12} className="warning-severity-icon info" />;
    default:
      return <AlertTriangle size={12} className="warning-severity-icon warning" />;
  }
}

export function WarningsBanner({ warnings }: WarningsBannerProps) {
  const [expanded, setExpanded] = useState(false);

  if (!warnings || warnings.length === 0) return null;

  const errorCount = warnings.filter((w) => w.severity === 'error').length;
  const warningCount = warnings.filter((w) => w.severity === 'warning').length;
  const infoCount = warnings.filter((w) => w.severity === 'info').length;

  const summaryParts: string[] = [];
  if (errorCount > 0) summaryParts.push(`${errorCount} error${errorCount > 1 ? 's' : ''}`);
  if (warningCount > 0) summaryParts.push(`${warningCount} warning${warningCount > 1 ? 's' : ''}`);
  if (infoCount > 0) summaryParts.push(`${infoCount} info`);
  const summary = summaryParts.join(', ');

  return (
    <div className="warnings-banner">
      <div className="warnings-collapsed" onClick={() => setExpanded(!expanded)}>
        <AlertTriangle size={13} className="warnings-icon" />
        <span className="warnings-count">{summary}</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </div>

      {expanded && (
        <div className="warnings-list">
          {warnings.map((w, i) => (
            <div key={i} className={`warning-item ${w.severity}`}>
              <SeverityIcon severity={w.severity} />
              <span className="warning-code">{w.code}</span>
              <span className="warning-message">{w.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
