import { useState, useCallback, useRef } from 'react';
import { Search, X } from 'lucide-react';

interface SearchNode {
  id: string;
  data: {
    label: string;
    resource_type: string;
    properties?: Record<string, unknown>;
  };
}

interface SearchBarProps {
  nodes: SearchNode[];
  onHighlight: (nodeIds: string[]) => void;
}

export function SearchBar({ nodes, onHighlight }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Array<{ id: string; label: string; type: string }>>([]);
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = useCallback((q: string) => {
    setQuery(q);
    if (!q.trim()) {
      setResults([]);
      onHighlight([]);
      return;
    }
    const lower = q.toLowerCase();
    const matched = nodes.filter(n => {
      const label = (n.data.label || '').toLowerCase();
      const type = (n.data.resource_type || '').toLowerCase();
      const cidr = (
        (n.data.properties?.cidr_block || n.data.properties?.cidr_blocks || '') as string
      ).toString().toLowerCase();
      return label.includes(lower) || type.includes(lower) || cidr.includes(lower);
    });
    setResults(matched.map(n => ({ id: n.id, label: n.data.label, type: n.data.resource_type })));
    onHighlight(matched.map(n => n.id));
  }, [nodes, onHighlight]);

  const handleClear = () => {
    setQuery('');
    setResults([]);
    onHighlight([]);
    setOpen(false);
  };

  return (
    <div className="search-bar">
      <Search size={13} className="search-icon" />
      <input
        ref={inputRef}
        type="text"
        className="search-input"
        placeholder="Search name, CIDR, type..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => setOpen(true)}
      />
      {query && (
        <button className="search-clear" onClick={handleClear}>
          <X size={12} />
        </button>
      )}
      {open && results.length > 0 && (
        <div className="search-results">
          {results.slice(0, 8).map(r => (
            <div key={r.id} className="search-result-item" onClick={() => {
              onHighlight([r.id]);
              setOpen(false);
            }}>
              <span className="search-result-type">{r.type.replace(/_/g, ' ')}</span>
              <span className="search-result-label">{r.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
