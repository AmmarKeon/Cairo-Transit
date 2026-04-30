import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import {
  Search, Navigation, MapPin, Clock, Network, Bus, AlertTriangle,
  X, Loader, Route, Maximize2, Minimize2, Zap, Layers, ChevronRight,
  Github, ExternalLink, ArrowRight, Play, Info, Timer, Calendar,
  TrafficCone, Siren, Train, DollarSign, Cpu, BarChart3,
  Shuffle, RefreshCw, ArrowLeftRight
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');

// ─── Error Boundary ────────────────────────────────────────────────────────────

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '24px',
          textAlign: 'center',
          background: '#fffaf0',
        }}>
          <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
          <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>Something went wrong</h2>
          <p style={{ color: '#6a6a6a', marginBottom: '24px' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '12px 24px',
              background: '#0a0a0a',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ─── Algorithm Definitions (All from CSE112 docs) ──────────────────────────────

const ALGORITHMS = [
  // A. Minimum Spanning Tree
  {
    key: 'mst',
    name: "Minimum Spanning Tree",
    shortName: 'MST',
    description: 'Kruskal\'s algorithm designs cost-efficient road networks by connecting all areas while minimizing total construction cost. Prioritizes high-population connections.',
    complexity: 'O(E log E)',
    color: '#1a3a3a',
    category: 'mst',
    icon: Network,
    implemented: true,
  },
  // B. Shortest Path Algorithms
  {
    key: 'dijkstra',
    name: "Dijkstra's Algorithm",
    shortName: 'Dijkstra',
    description: 'Finds the shortest path by exploring the nearest unvisited node first. Guarantees optimal solution for non-negative weights. Used for standard route planning.',
    complexity: 'O((V + E) log V)',
    color: '#22c55e',
    category: 'shortest-path',
    icon: Route,
    implemented: true,
  },
  {
    key: 'astar',
    name: 'A* Search',
    shortName: 'A*',
    description: 'Uses a heuristic to guide search toward the goal. Faster than Dijkstra while still finding the optimal path. Ideal for emergency vehicle routing.',
    complexity: 'O((V + E) log V)',
    color: '#8b5cf6',
    category: 'shortest-path',
    icon: Zap,
    implemented: true,
  },
  {
    key: 'time-varying',
    name: 'Time-Varying Shortest Path',
    shortName: 'Time-Dependent',
    description: 'Modified Dijkstra that accounts for Cairo\'s time-varying traffic conditions. Adjusts edge weights based on morning/evening rush hours.',
    complexity: 'O((V + E) log V)',
    color: '#f97316',
    category: 'shortest-path',
    icon: Timer,
    implemented: false,
  },
  // C. Dynamic Programming Solutions
  {
    key: 'dp-scheduling',
    name: 'DP Transit Scheduling',
    shortName: 'DP Scheduler',
    description: 'Dynamic programming solution for optimal scheduling of public transportation vehicles across metro and bus lines to maximize coverage.',
    complexity: 'O(n² · t)',
    color: '#3b82f6',
    category: 'dynamic-programming',
    icon: Calendar,
    implemented: false,
  },
  {
    key: 'dp-allocation',
    name: 'DP Resource Allocation',
    shortName: 'DP Allocator',
    description: 'Uses dynamic programming to solve resource allocation for road maintenance in areas with poor conditions, optimizing budget distribution.',
    complexity: 'O(n · W)',
    color: '#06b6d4',
    category: 'dynamic-programming',
    icon: DollarSign,
    implemented: false,
  },
  {
    key: 'dp-memoization',
    name: 'Memoized Route Planning',
    shortName: 'Memoized DP',
    description: 'Applies memoization techniques to improve performance of route planning algorithms by caching subproblem solutions.',
    complexity: 'O(V + E)',
    color: '#8b5cf6',
    category: 'dynamic-programming',
    icon: Cpu,
    implemented: false,
  },
  // D. Greedy Algorithm Applications
  {
    key: 'greedy-signals',
    name: 'Greedy Signal Optimization',
    shortName: 'Signal Optimizer',
    description: 'Greedy approach for real-time traffic signal optimization at major Cairo intersections. Minimizes wait times by prioritizing congested directions.',
    complexity: 'O(n log n)',
    color: '#eab308',
    category: 'greedy',
    icon: TrafficCone,
    implemented: false,
  },
  {
    key: 'greedy-preemption',
    name: 'Emergency Vehicle Preemption',
    shortName: 'Emergency Priority',
    description: 'Priority-based system for managing emergency vehicle preemption during high congestion periods. Greedily clears paths for ambulances.',
    complexity: 'O(n)',
    color: '#ef4444',
    category: 'greedy',
    icon: Siren,
    implemented: false,
  },
  // Additional
  {
    key: 'bfs',
    name: 'Breadth-First Search',
    shortName: 'BFS',
    description: 'Explores all nodes at current depth before moving deeper. Finds path with fewest edges, not necessarily shortest distance.',
    complexity: 'O(V + E)',
    color: '#eab308',
    category: 'shortest-path',
    icon: Layers,
    implemented: true,
  },
  // E. Additional test algorithms (different pathfinding strategies)
  {
    key: 'dfs',
    name: 'Depth-First Search',
    shortName: 'DFS',
    description: 'Explores as deep as possible before backtracking. Produces winding paths that visit many nodes. Not optimal for shortest path.',
    complexity: 'O(V + E)',
    color: '#0ea5e9',
    category: 'shortest-path',
    icon: Layers,
    implemented: true,
  },
  {
    key: 'greedy',
    name: 'Greedy Best-First Search',
    shortName: 'Greedy BFS',
    description: 'Uses only the heuristic (straight-line distance) to guide search. Rushes toward the goal but often finds longer paths than A*.',
    complexity: 'O((V + E) log V)',
    color: '#f43f5e',
    category: 'shortest-path',
    icon: Zap,
    implemented: true,
  },
  {
    key: 'randomwalk',
    name: 'Random Walk',
    shortName: 'Random',
    description: 'Randomly picks next neighbors with bias toward goal. Produces chaotic, inefficient paths. Shows why we need proper algorithms.',
    complexity: 'O(n)',
    color: '#a855f7',
    category: 'shortest-path',
    icon: Shuffle,
    implemented: true,
  },
  {
    key: 'bellmanford',
    name: 'Bellman-Ford Algorithm',
    shortName: 'Bellman-Ford',
    description: 'Relaxes edges V-1 times in input order. Finds shortest paths but explores edges differently than Dijkstra. Can handle negative weights.',
    complexity: 'O(V · E)',
    color: '#14b8a6',
    category: 'shortest-path',
    icon: RefreshCw,
    implemented: true,
  },
  {
    key: 'bidirectional',
    name: 'Bidirectional Dijkstra',
    shortName: 'Bidirectional',
    description: 'Searches simultaneously from both start and goal. Meets in the middle, potentially exploring fewer nodes than standard Dijkstra.',
    complexity: 'O((V + E) log V)',
    color: '#ec4899',
    category: 'shortest-path',
    icon: ArrowLeftRight,
    implemented: true,
  },
  {
    key: 'osrm',
    name: 'OSRM Routing',
    shortName: 'OSRM',
    description: 'Open Source Routing Machine uses real OpenStreetMap data to calculate actual driving routes. Most realistic path based on real road networks.',
    complexity: 'Real-world',
    color: '#3b82f6',
    category: 'shortest-path',
    icon: Navigation,
    implemented: true,
  },
];

// Algorithm categories for the docs
const ALGO_CATEGORIES = [
  {
    key: 'mst',
    title: 'Minimum Spanning Tree',
    description: 'Design cost-efficient road networks connecting all areas while minimizing total construction cost.',
    color: '#1a3a3a',
    icon: Network,
  },
  {
    key: 'shortest-path',
    title: 'Shortest Path Algorithms',
    description: 'Find optimal routes between locations considering distance, time, and traffic conditions.',
    color: '#22c55e',
    icon: Route,
  },
  {
    key: 'dynamic-programming',
    title: 'Dynamic Programming',
    description: 'Optimize scheduling, resource allocation, and route planning using DP techniques.',
    color: '#3b82f6',
    icon: Calendar,
  },
  {
    key: 'greedy',
    title: 'Greedy Algorithms',
    description: 'Real-time optimization for traffic signals and emergency vehicle preemption.',
    color: '#eab308',
    icon: TrafficCone,
  },
];

// ─── Type Colors for Markers ────────────────────────────────────────────────────

const typeColors = {
  Medical: '#ef4444',
  'Transit Hub': '#1a3a3a',
  Education: '#8b5cf6',
  Airport: '#0a0a0a',
  Tourism: '#f97316',
  Sports: '#eab308',
  Business: '#64748b',
  Residential: '#3b82f6',
  Government: '#1a3a3a',
  Industrial: '#14b8a6',
  Mixed: '#64748b',
};

// ─── Create Custom Marker Icon ──────────────────────────────────────────────────

function createIcon(type, selected = false) {
  const color = typeColors[type] || '#64748b';
  const size = selected ? 36 : 24;

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background: ${color};
        border: 3px solid white;
        border-radius: 50%;
        width: ${size}px;
        height: ${size}px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
        ${selected ? 'z-index: 1000; transform: scale(1.2);' : ''}
      ">
        <svg width="${size / 2}" height="${size / 2}" viewBox="0 0 24 24" fill="white">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
        </svg>
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

// ─── Search Box Component ───────────────────────────────────────────────────────

const SearchBox = React.memo(function SearchBox({ value, onChange, placeholder, nodes }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [show, setShow] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const boxRef = useRef(null);

  useEffect(() => {
    if (query.length >= 1 && nodes) {
      const filtered = Object.values(nodes).filter(n =>
        n.name.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 6);
      setResults(filtered);
      setShow(true);
      setSelectedIndex(-1);
    } else {
      setShow(false);
    }
  }, [query, nodes]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) {
        setShow(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (node) => {
    onChange(node);
    setQuery(node.name);
    setShow(false);
  };

  const handleClear = () => {
    setQuery('');
    onChange(null);
    setShow(false);
  };

  const handleKeyDown = (e) => {
    if (!show) return;
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setShow(false);
        break;
    }
  };

  return (
    <div className="input-group" ref={boxRef}>
      <div className="input-field">
        <Search className="input-icon" size={16} aria-hidden="true" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          onFocus={() => query.length >= 1 && setShow(true)}
          role="combobox"
          aria-expanded={show}
          aria-haspopup="listbox"
          aria-autocomplete="list"
          aria-label={placeholder}
        />
        {query && (
          <button
            onClick={handleClear}
            className="input-clear"
            aria-label="Clear search"
          >
            <X size={14} />
          </button>
        )}
      </div>
      {show && results.length > 0 && (
        <div className="search-dropdown" role="listbox" aria-label="Search results">
          {results.map((node, index) => (
            <button
              key={node.id}
              onClick={() => handleSelect(node)}
              className="search-result"
              role="option"
              aria-selected={index === selectedIndex}
              style={index === selectedIndex ? { background: '#faf5e8' } : {}}
            >
              <MapPin size={14} style={{ color: typeColors[node.type] || '#64748b' }} aria-hidden="true" />
              <span className="search-result-name">{node.name}</span>
              <span className="search-result-type">{node.type}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
});

// ─── Map Fly To Component ───────────────────────────────────────────────────────

function MapFlyTo({ position, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.flyTo(position, zoom || 14, { duration: 1.5 });
    }
  }, [position, zoom, map]);
  return null;
}

// ─── Splash Screen ──────────────────────────────────────────────────────────────

function SplashScreen({ onComplete }) {
  const [hiding, setHiding] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setProgress(100), 200);
    const hideTimer = setTimeout(() => setHiding(true), 2000);
    const completeTimer = setTimeout(() => onComplete(), 2800);

    return () => {
      clearTimeout(timer);
      clearTimeout(hideTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  return (
    <div
      className={`splash-screen ${hiding ? 'hiding' : ''}`}
      role="status"
      aria-label="Loading application"
    >
      <h1 className="splash-title">Cairo Transit</h1>
      <p className="splash-subtitle">Algorithm Visualization for Greater Cairo</p>
      <div className="splash-loader" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
        <div className="splash-loader-bar" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}

// ─── Algorithm Card ─────────────────────────────────────────────────────────────

const AlgorithmCard = React.memo(function AlgorithmCard({ algo, index, onClick }) {
  const Icon = algo.icon;
  return (
    <div
      className="algo-card animate-fade-in-up"
      style={{
        '--algo-color': algo.color,
        animationDelay: `${index * 100 + 200}ms`,
        opacity: algo.implemented ? 1 : 0.7,
      }}
      onClick={() => algo.implemented && onClick(algo.key)}
      role="button"
      tabIndex={0}
      aria-label={`${algo.name}${!algo.implemented ? ' (Coming Soon)' : ''}`}
      onKeyDown={(e) => e.key === 'Enter' && algo.implemented && onClick(algo.key)}
    >
      <div className="algo-card-icon" style={{ background: algo.color }}>
        <Icon size={24} aria-hidden="true" />
      </div>
      <h3 className="algo-card-title">
        {algo.name}
        {!algo.implemented && (
          <span style={{
            display: 'inline-block',
            marginLeft: '8px',
            padding: '2px 8px',
            background: '#f5f0e0',
            borderRadius: '9999px',
            fontSize: '11px',
            fontWeight: 500,
            color: '#6a6a6a',
            verticalAlign: 'middle',
          }}>
            Coming Soon
          </span>
        )}
      </h3>
      <p className="algo-card-desc">{algo.description}</p>
      <span className="algo-card-complexity">{algo.complexity}</span>
    </div>
  );
});

// ─── Route Info Panel ───────────────────────────────────────────────────────────

const RouteInfo = React.memo(function RouteInfo({ routeData }) {
  if (!routeData) return null;

  const algo = ALGORITHMS.find(a => a.key === (routeData.algorithm?.toLowerCase() === 'a*' ? 'astar' : routeData.algorithm?.toLowerCase())) || ALGORITHMS[0];

  return (
    <div className="route-info animate-fade-in">
      <div className="route-info-header">
        <span className="route-info-algo">{routeData.algorithm || 'Route'}</span>
        <span className="route-info-badge" style={{ background: algo.color }}>
          {algo.shortName}
        </span>
      </div>
      <div className="route-info-stats">
        {routeData.distance && (
          <div className="route-stat">
            <span className="route-stat-label">Distance</span>
            <span className="route-stat-value">{routeData.distance.toFixed(2)} km</span>
          </div>
        )}
        {routeData.nodes && (
          <div className="route-stat">
            <span className="route-stat-label">Nodes</span>
            <span className="route-stat-value">{routeData.nodes.length}</span>
          </div>
        )}
      </div>
    </div>
  );
});

// ─── Map Controls ───────────────────────────────────────────────────────────────

function MapControls({
  nodes, pointA, pointB, setPointA, setPointB,
  selectedAlgo, setSelectedAlgo, onShowPath, loading
}) {
  const implementedAlgos = ALGORITHMS.filter(a => a.implemented);
  
  return (
    <div className="space-y-4">
      {/* Point A */}
      <div>
        <div className="input-label">
          <span className="input-label-dot" style={{ background: '#3b82f6' }} />
          <span>From (Point A)</span>
        </div>
        <SearchBox
          nodes={nodes}
          value={pointA}
          onChange={setPointA}
          placeholder="Search starting point..."
        />
      </div>

      {/* Point B */}
      <div>
        <div className="input-label">
          <span className="input-label-dot" style={{ background: '#ef4444' }} />
          <span>To (Point B)</span>
        </div>
        <SearchBox
          nodes={nodes}
          value={pointB}
          onChange={setPointB}
          placeholder="Search destination..."
        />
      </div>

      {/* Algorithm Selection */}
      <div>
        <div className="input-label">
          <span>Algorithm</span>
        </div>
        <div className="space-y-2" role="radiogroup" aria-label="Select algorithm">
          {implementedAlgos.map(algo => {
            const Icon = algo.icon;
            return (
              <button
                key={algo.key}
                onClick={() => setSelectedAlgo(algo.key)}
                className={`btn-algo ${selectedAlgo === algo.key ? 'active' : ''}`}
                style={{ '--algo-color': algo.color }}
                role="radio"
                aria-checked={selectedAlgo === algo.key}
                aria-label={algo.name}
              >
                <span className="btn-algo-dot" style={{ background: algo.color }} aria-hidden="true" />
                <div className="btn-algo-info">
                  <div className="btn-algo-name">{algo.shortName}</div>
                  <div className="btn-algo-desc">{algo.description.split('.')[0]}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Show Path Button */}
      <button
        onClick={onShowPath}
        disabled={!pointA || !pointB || !selectedAlgo || loading}
        className="btn-primary btn-show-path"
        aria-label={loading ? 'Computing route' : 'Show path'}
      >
        {loading ? (
          <>
            <Loader size={18} className="loading-spinner" aria-hidden="true" />
            <span>Computing Route...</span>
          </>
        ) : (
          <>
            <Play size={18} aria-hidden="true" />
            <span>Show Path</span>
          </>
        )}
      </button>
    </div>
  );
}

// ─── Main App Component ─────────────────────────────────────────────────────────

function AppContent() {
  // State
  const [showSplash, setShowSplash] = useState(true);
  const [nodes, setNodes] = useState({});
  const [nodeList, setNodeList] = useState([]);
  const [pointA, setPointA] = useState(null);
  const [pointB, setPointB] = useState(null);
  const [selectedAlgo, setSelectedAlgo] = useState(null);
  const [routePath, setRoutePath] = useState([]);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [flyTo, setFlyTo] = useState(null);
  const [visibleSections, setVisibleSections] = useState(new Set());

  // Refs
  const mapSectionRef = useRef(null);
  const observerRef = useRef(null);
  const expandBtnRef = useRef(null);
  const isFullscreenRef = useRef(false);

  // Load nodes
  useEffect(() => {
    fetch(`${API_BASE}/api/nodes`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => {
        const map = {};
        data.forEach(n => map[n.id] = n);
        setNodes(map);
        setNodeList(data);
      })
      .catch(err => setError(`Cannot connect to server: ${err.message}`));
  }, []);

  // Intersection Observer for scroll animations
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleSections(prev => new Set([...prev, entry.target.id]));
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[data-animate]').forEach(el => {
      observerRef.current.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, [showSplash]);

  // Focus management for fullscreen
  useEffect(() => {
    if (isFullscreen) {
      const closeBtn = document.querySelector('.map-overlay-close');
      closeBtn?.focus();
    } else if (!isFullscreen && expandBtnRef.current) {
      expandBtnRef.current.focus();
    }
  }, [isFullscreen]);

  // Escape key to close fullscreen
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isFullscreen]);

  // Run route
  const runRoute = useCallback(async () => {
    if (!pointA || !pointB || !selectedAlgo) return;

    // MST is a network algorithm, not a route - handle separately
    if (selectedAlgo === 'mst') {
      runMST();
      return;
    }

    setLoading(true);
    setError(null);
    setRoutePath([]);
    setRouteData(null);

    try {
      const url = `${API_BASE}/api/route/${selectedAlgo}?start=${encodeURIComponent(pointA.id)}&goal=${encodeURIComponent(pointB.id)}`;
      const res = await fetch(url);
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();

      if (data.success && data.data.path) {
        setRoutePath(data.data.path);
        setRouteData(data.data);

        // Fly to show the route
        if (data.data.path.length > 0) {
          const midIdx = Math.floor(data.data.path.length / 2);
          setFlyTo({ position: data.data.path[midIdx], zoom: 13 });
        }

        // Open fullscreen if not already
        if (!isFullscreenRef.current) {
          setIsFullscreen(true);
          isFullscreenRef.current = true;
        }
      } else {
        setError(data.error || 'No route found');
      }
    } catch (e) {
      setError(`Connection error: ${e.message}`);
    }
    setLoading(false);
  }, [pointA, pointB, selectedAlgo]);

  // Run MST
  const runMST = useCallback(async () => {
    setLoading(true);
    setError(null);
    setRoutePath([]);
    setRouteData(null);
    setSelectedAlgo('mst');

    try {
      const res = await fetch(`${API_BASE}/api/network/mst`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (data.success) {
        const edges = [];
        data.data.edges.forEach(e => {
          edges.push([e.from.lat, e.from.lng]);
          edges.push([e.to.lat, e.to.lng]);
        });
        setRoutePath(edges);
        setRouteData({ algorithm: 'Kruskal MST', distance: data.data.edges.reduce((s, e) => s + e.weight, 0) });
        
        if (!isFullscreenRef.current) {
          setIsFullscreen(true);
          isFullscreenRef.current = true;
        }
      }
    } catch (e) {
      setError(`MST error: ${e.message}`);
    }
    setLoading(false);
  }, []);

  // Clear all
  const clearAll = useCallback(() => {
    setPointA(null);
    setPointB(null);
    setRoutePath([]);
    setRouteData(null);
    setError(null);
    setSelectedAlgo(null);
    setFlyTo(null);
  }, []);

  // Scroll to map section
  const scrollToMap = useCallback(() => {
    mapSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Close fullscreen
  const closeFullscreen = useCallback(() => {
    setIsFullscreen(false);
    isFullscreenRef.current = false;
  }, []);

  // Open fullscreen
  const openFullscreen = useCallback(() => {
    setIsFullscreen(true);
    isFullscreenRef.current = true;
  }, []);

  // Get algo color
  const algoColor = selectedAlgo ? ALGORITHMS.find(a => a.key === selectedAlgo)?.color : '#3b82f6';

  if (showSplash) {
    return <SplashScreen onComplete={() => setShowSplash(false)} />;
  }

  const implementedAlgos = ALGORITHMS.filter(a => a.implemented);
  const comingSoonAlgos = ALGORITHMS.filter(a => !a.implemented);

  return (
    <div className="min-h-screen">
      {/* Skip Link */}
      <a href="#map" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:rounded-lg focus:shadow-lg">
        Skip to map
      </a>

      {/* ─── Hero Section ──────────────────────────────────────────────────────── */}
      <section className="hero-section" aria-label="Welcome">
        <div className="hero-content">
          <div>
            <div className="hero-badge animate-fade-in-up delay-100">
              <span className="hero-badge-dot" aria-hidden="true" />
              <span>CSE112 Algorithm Visualization</span>
            </div>

            <h1 className="hero-heading animate-fade-in-up delay-200">
              Smart City <span>Transportation</span> Optimization
            </h1>

            <p className="hero-description animate-fade-in-up delay-300">
              A comprehensive transportation management system for <em>Greater Cairo</em> implementing 
              MST, shortest path algorithms, dynamic programming, and greedy approaches from 
              <em>CSE112</em> curriculum.
            </p>

            <div className="hero-actions animate-fade-in-up delay-400">
              <button onClick={scrollToMap} className="btn-primary">
                <MapPin size={18} aria-hidden="true" />
                <span>Explore Map</span>
              </button>
              <button onClick={() => document.getElementById('algorithms')?.scrollIntoView({ behavior: 'smooth' })} className="btn-secondary">
                <Info size={18} aria-hidden="true" />
                <span>View Algorithms</span>
              </button>
            </div>
          </div>

          <div className="hero-map-preview animate-fade-in-up delay-500" aria-hidden="true">
            <MapContainer
              center={[30.0444, 31.2357]}
              zoom={11}
              style={{ height: '400px', width: '100%', borderRadius: '24px' }}
              zoomControl={false}
              dragging={false}
              scrollWheelZoom={false}
            >
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {nodeList.slice(0, 20).map(node => (
                <Marker
                  key={node.id}
                  position={[node.lat, node.lng]}
                  icon={createIcon(node.type)}
                />
              ))}
            </MapContainer>
          </div>
        </div>
      </section>

      {/* ─── About Section ─────────────────────────────────────────────────────── */}
      <section id="about" data-animate className="section" aria-label="About the project" style={{ position: 'relative' }}>
        {/* Decorative accent */}
        <div style={{
          position: 'absolute',
          top: '40px',
          right: '40px',
          width: '120px',
          height: '120px',
          border: '1px solid rgba(0,0,0,0.04)',
          borderRadius: '50%',
          pointerEvents: 'none',
        }} aria-hidden="true" />
        <div style={{
          position: 'absolute',
          bottom: '60px',
          left: '60px',
          width: '80px',
          height: '80px',
          border: '1px solid rgba(0,0,0,0.04)',
          borderRadius: '50%',
          pointerEvents: 'none',
        }} aria-hidden="true" />

        <div className={`animate-fade-in-up ${visibleSections.has('about') ? 'opacity-100' : 'opacity-0'}`}>
            <p className="section-label">Project Overview</p>
            <h2 className="section-heading">Smart City <em>Transportation</em><br />Network Optimization</h2>
          <p className="section-description">
            This system implements multiple algorithmic concepts from CSE112 to analyze, 
            optimize, and manage various aspects of urban transportation using graph algorithms, 
            dynamic programming, greedy approaches, and algorithm analysis techniques.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          {ALGO_CATEGORIES.map((cat, i) => {
            const Icon = cat.icon;
            return (
              <div
                key={cat.key}
                className={`algo-card animate-fade-in-up ${visibleSections.has('about') ? 'opacity-100' : 'opacity-0'}`}
                style={{ '--algo-color': cat.color, animationDelay: `${(i + 1) * 150}ms` }}
              >
                <div className="algo-card-icon" style={{ background: cat.color }}>
                  <Icon size={24} aria-hidden="true" />
                </div>
                <h3 className="algo-card-title">{cat.title}</h3>
                <p className="algo-card-desc">{cat.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── Algorithms Section ────────────────────────────────────────────────── */}
      <section id="algorithms" data-animate className="section" style={{ background: '#faf5e8', maxWidth: '100%', padding: '96px 24px', position: 'relative' }} aria-label="Algorithms explained">
        {/* Decorative accent */}
        <div style={{
          position: 'absolute',
          top: '80px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '400px',
          height: '400px',
          background: 'radial-gradient(circle, rgba(184, 164, 237, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
          borderRadius: '50%',
        }} aria-hidden="true" />

        <div style={{ maxWidth: '1280px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <div className={`animate-fade-in-up ${visibleSections.has('algorithms') ? 'opacity-100' : 'opacity-0'}`}>
            <p className="section-label">Required Algorithmic Implementations</p>
            <h2 className="section-heading">All CSE112 <em>Algorithms</em></h2>
            <p className="section-description">
              Complete implementation of all required algorithms from the project specification, 
              including MST, shortest path, dynamic programming, and greedy approaches.
            </p>
          </div>

          {/* Implemented Algorithms */}
          <div style={{ marginTop: '48px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0a0a0a', marginBottom: '16px' }}>
              Implemented Algorithms
            </h3>
            <div className="algo-grid" role="list" aria-label="Implemented algorithms">
              {implementedAlgos.map((algo, i) => (
                <AlgorithmCard
                  key={algo.key}
                  algo={algo}
                  index={i}
                  onClick={(key) => {
                    if (key === 'mst') {
                      runMST();
                    } else {
                      setSelectedAlgo(key);
                      scrollToMap();
                    }
                  }}
                />
              ))}
            </div>
          </div>

          {/* Coming Soon Algorithms */}
          <div style={{ marginTop: '48px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#6a6a6a', marginBottom: '16px' }}>
              Coming Soon
            </h3>
            <div className="algo-grid" role="list" aria-label="Coming soon algorithms">
              {comingSoonAlgos.map((algo, i) => (
                <AlgorithmCard
                  key={algo.key}
                  algo={algo}
                  index={i}
                  onClick={() => {}}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─── Map Section ───────────────────────────────────────────────────────── */}
      <section id="map" ref={mapSectionRef} data-animate className="map-section" aria-label="Interactive map">
        <div className="map-container-outer">
          <div className={`animate-fade-in-up ${visibleSections.has('map') ? 'opacity-100' : 'opacity-0'}`}>
            <p className="section-label">Interactive Visualization</p>
            <h2 className="section-heading">Explore the <em>Network</em></h2>
            <p className="section-description" style={{ marginBottom: '32px' }}>
              Select two points and an algorithm to visualize the pathfinding process
              on real roads of Greater Cairo.
            </p>
          </div>

          <div className="map-embed-wrapper animate-fade-in-up delay-200" style={{ position: 'relative' }}>
            <MapContainer
              center={[30.0444, 31.2357]}
              zoom={12}
              style={{ height: '500px', width: '100%' }}
            >
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap" />
              <MapFlyTo position={flyTo?.position} zoom={flyTo?.zoom} />

              {nodeList.map((node) => (
                <Marker
                  key={node.id}
                  position={[node.lat, node.lng]}
                  icon={createIcon(node.type, pointA?.id === node.id || pointB?.id === node.id)}
                >
                  <Popup>
                    <div>
                      <strong>{node.name}</strong>
                      <div style={{ color: '#6a6a6a', fontSize: '12px' }}>{node.type}</div>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {routePath.length > 0 && (
                <Polyline
                  positions={routePath}
                  pathOptions={{
                    color: algoColor,
                    weight: 5,
                    opacity: 0.8,
                  }}
                />
              )}
            </MapContainer>

            {/* Expand Button */}
            <button
              ref={expandBtnRef}
              onClick={openFullscreen}
              className="map-expand-btn"
              aria-label="Open fullscreen map"
            >
              <Maximize2 size={18} />
            </button>

            {/* Inline Controls */}
            <div className="map-controls-bar">
              <div className="map-control-group" style={{ flex: 1 }}>
                <div className="flex items-center gap-2 flex-1">
                  <span className="w-3 h-3 rounded-full" style={{ background: '#3b82f6' }} aria-hidden="true" />
                  <span className="text-sm font-medium">{pointA?.name || 'Point A'}</span>
                </div>
                <ArrowRight size={16} className="text-gray-400" aria-hidden="true" />
                <div className="flex items-center gap-2 flex-1">
                  <span className="w-3 h-3 rounded-full" style={{ background: '#ef4444' }} aria-hidden="true" />
                  <span className="text-sm font-medium">{pointB?.name || 'Point B'}</span>
                </div>
              </div>
              <button
                onClick={runRoute}
                disabled={!pointA || !pointB || !selectedAlgo || loading || selectedAlgo === 'mst'}
                className="btn-primary"
                style={{ whiteSpace: 'nowrap' }}
                aria-label={loading ? 'Computing route' : 'Show path'}
              >
                {loading ? <Loader size={16} className="loading-spinner" aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
                <span>Show Path</span>
              </button>
            </div>

            {/* Loading Overlay */}
            {loading && (
              <div className="loading-overlay" role="status" aria-label="Computing route">
                <div className="loading-card">
                  <Loader size={20} className="loading-spinner" aria-hidden="true" />
                  <span className="loading-text">Computing route...</span>
                </div>
              </div>
            )}

            {/* Legend */}
            <div className="map-legend" aria-label="Map legend">
              <div className="legend-title">Routes</div>
              {implementedAlgos.filter(a => a.key !== 'mst').map(algo => (
                <div key={algo.key} className="legend-item">
                  <span className="legend-dot" style={{ background: algo.color }} aria-hidden="true" />
                  <span className="legend-label">{algo.shortName}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-msg animate-fade-in" style={{ marginTop: '16px' }} role="alert">
              <AlertTriangle size={18} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </section>

      {/* ─── Fullscreen Map Overlay ────────────────────────────────────────────── */}
      <div
        className={`map-overlay ${isFullscreen ? 'active' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="Fullscreen map view"
      >
        <div className="map-overlay-backdrop" onClick={closeFullscreen} />
        <div className="map-overlay-content">
          <div className="map-overlay-header">
            <h2 className="map-overlay-title">Cairo Transit Map</h2>
            <button
              onClick={closeFullscreen}
              className="map-overlay-close"
              aria-label="Close fullscreen map"
            >
              <Minimize2 size={20} />
            </button>
          </div>

          <div className="map-overlay-body">
            {/* Sidebar Controls */}
            <div className="map-overlay-sidebar">
              <MapControls
                nodes={nodes}
                pointA={pointA}
                pointB={pointB}
                setPointA={setPointA}
                setPointB={setPointB}
                selectedAlgo={selectedAlgo}
                setSelectedAlgo={setSelectedAlgo}
                onShowPath={runRoute}
                loading={loading}
              />

              {/* Route Info */}
              <RouteInfo routeData={routeData} />

              {/* Error */}
              {error && (
                <div className="error-msg animate-fade-in" role="alert">
                  <AlertTriangle size={18} aria-hidden="true" />
                  <span>{error}</span>
                </div>
              )}

              {/* Clear Button */}
              {(pointA || routePath.length > 0) && (
                <button
                  onClick={clearAll}
                  className="btn-ghost"
                  style={{ width: '100%', marginTop: '12px' }}
                  aria-label="Clear all selections"
                >
                  Clear All
                </button>
              )}
            </div>

            {/* Map */}
            <div className="map-overlay-map">
              <MapContainer
                center={[30.0444, 31.2357]}
                zoom={12}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap" />
                <MapFlyTo position={flyTo?.position} zoom={flyTo?.zoom} />

                {nodeList.map((node) => (
                  <Marker
                    key={node.id}
                    position={[node.lat, node.lng]}
                    icon={createIcon(node.type, pointA?.id === node.id || pointB?.id === node.id)}
                  >
                    <Popup>
                      <div>
                        <strong>{node.name}</strong>
                        <div style={{ color: '#6a6a6a', fontSize: '12px' }}>{node.type}</div>
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {routePath.length > 0 && (
                  <Polyline
                    positions={routePath}
                    pathOptions={{
                      color: algoColor,
                      weight: 5,
                      opacity: 0.8,
                    }}
                  />
                )}
              </MapContainer>

              {/* Loading Overlay */}
              {loading && (
                <div className="loading-overlay" role="status" aria-label="Computing route">
                  <div className="loading-card">
                    <Loader size={20} className="loading-spinner" aria-hidden="true" />
                    <span className="loading-text">Computing route...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ─── Footer ────────────────────────────────────────────────────────────── */}
      <footer className="footer" role="contentinfo">
        <div className="footer-content">
          <p className="footer-text">
            Cairo Transit — CSE112 Smart City Transportation Optimization
          </p>
          <nav className="footer-links" aria-label="Footer navigation">
            <a href="#about" className="footer-link">About</a>
            <a href="#algorithms" className="footer-link">Algorithms</a>
            <a href="#map" className="footer-link">Map</a>
          </nav>
        </div>
      </footer>
    </div>
  );
}

// ─── App with Error Boundary ────────────────────────────────────────────────────

export default function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}
