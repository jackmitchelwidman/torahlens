import React, { useState, useRef, useEffect } from 'react';
import './styles/App.css';

const PERSPECTIVES = [
  "Theological",
  "Philosophical",
  "Secular",
  "Scientific"
];

const AboutModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          Close
        </button>
        <h2>About TorahLens</h2>
        <p>
          TorahLens is an innovative tool that brings ancient biblical texts into dialogue with modern perspectives. 
          By combining traditional Hebrew scripture with AI-powered analysis, it offers users the unique ability 
          to explore Torah passages through multiple viewpoints - theological, philosophical, secular, archaeological, 
          scientific, and more. Whether you're a scholar, student, or seeker, TorahLens helps bridge the gap between 
          ancient wisdom and contemporary understanding, providing fresh insights into these timeless texts.
        </p>
      </div>
    </div>
  );
};

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [aiCommentary, setAiCommentary] = useState('');
  const [perspective, setPerspective] = useState("Theological");
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentary, setLoadingCommentary] = useState(false);
  const [error, setError] = useState('');
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const commentaryRef = useRef(null);

  useEffect(() => {
    if (aiCommentary && commentaryRef.current) {
      const scrollToCommentary = () => {
        commentaryRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });

        const yOffset = -20;
        const element = commentaryRef.current;
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        
        window.scrollTo({
          top: y,
          behavior: 'smooth'
        });
      };

      setTimeout(scrollToCommentary, 300);
    }
  }, [aiCommentary]);

  const backendUrl = 'http://localhost:5000';

  const stripHtml = (html) => {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  };

  const fetchPassage = async () => {
    if (!passage.trim()) {
      setError('Please enter a passage reference');
      return;
    }

    setLoadingPassage(true);
    setError('');
    setHebrew('');
    setEnglish('');
    setAiCommentary('');
    
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      
      if (response.status === 400) {
        setError(data.error || 'Please provide a valid reference format, such as "Genesis 1:1" or "בראשית א:א"');
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch passage');
      }
      
      if (data.error) {
        setError(data.error);
      } else {
        setHebrew(stripHtml(data.hebrew));
        setEnglish(stripHtml(data.english));
      }
    } catch (err) {
      setError('Error fetching passage. Please try again with a valid reference.');
      console.error(err);
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchAiCommentary = async () => {
    if (!passage.trim()) {
      setError("Please fetch the passage first.");
      return;
    }

    setLoadingCommentary(true);
    setError("");
    setAiCommentary("");

    try {
      // Build URL with explicit encoding
      const url = new URL(`${backendUrl}/api/get_ai_commentary`);
      url.searchParams.append('passage', encodeURIComponent(passage.trim()));
      url.searchParams.append('perspective', perspective);
      
      console.log('Making request to:', url.toString());
      console.log('Using perspective:', perspective);

      const response = await fetch(url.toString());
      console.log('Response status:', response.status);
      
      // Get the raw text first
      const rawText = await response.text();
      console.log('Raw response text:', rawText);
      
      // Try to parse as JSON
      let data;
      try {
        data = JSON.parse(rawText);
        console.log('Parsed JSON:', data);
      } catch (e) {
        console.error('JSON parse error:', e);
        setError('Server returned invalid JSON. Raw response: ' + rawText.substring(0, 100) + '...');
        return;
      }

      if (!response.ok) {
        setError(data.error || `HTTP error ${response.status}`);
        return;
      }

      if (data.commentary) {
        setAiCommentary(data.commentary);
        setError("");
      } else {
        setError("No commentary received from server");
      }
    } catch (error) {
      console.error("Network error:", error);
      setError("Unable to fetch AI commentary. Error: " + error.message);
    } finally {
      setLoadingCommentary(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1>TorahLens</h1>
          <button 
            className="about-link"
            onClick={() => setIsAboutOpen(true)}
          >
            About TorahLens
          </button>
        </div>
      </header>

      <AboutModal 
        isOpen={isAboutOpen} 
        onClose={() => setIsAboutOpen(false)} 
      />

      <main className="app-main">
        <div className="input-section">
          <div className="input-wrapper">
            <input
              type="text"
              value={passage}
              onChange={(e) => setPassage(e.target.value)}
              placeholder="Enter passage (e.g., Genesis 1:1 or בראשית א:א)"
              className="input-field"
              dir="auto"
            />
            <div className="input-helper-text">
              Enter a reference like "Genesis 1:1", "Genesis 1", or in Hebrew "בראשית א:א"
            </div>
          </div>
          <button onClick={fetchPassage} disabled={loadingPassage} className="button-primary">
            {loadingPassage ? 'Loading...' : 'Get Passage'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="perspective-section">
          <h3>AI Commentary Perspective</h3>
          <div className="perspective-options">
            <select 
              value={perspective}
              onChange={(e) => {
                console.log('Setting perspective to:', e.target.value);
                setPerspective(e.target.value);
              }}
              className="perspective-select"
            >
              {PERSPECTIVES.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div className="commentary-button-container">
            <button 
              onClick={fetchAiCommentary} 
              disabled={!english || loadingCommentary}
              className="button-secondary"
            >
              {loadingCommentary ? 'Ruminating...' : 'Get AI Commentary'}
            </button>
            {!english && passage && (
              <div className="button-helper-text">
                Please fetch the passage first using "Get Passage"
              </div>
            )}
          </div>
        </div>

        {english && (
          <div className="passage-section">
            <h2>Hebrew Text:</h2>
            <div className="hebrew-text">{hebrew}</div>
            <h2>English Translation:</h2>
            <div className="english-text">{english}</div>
          </div>
        )}

        {aiCommentary && (
          <div ref={commentaryRef} className="commentary-section">
            <h2>AI Commentary ({perspective} Perspective):</h2>
            <p>{aiCommentary}</p>
          </div>
        )}
      </main>
      <footer className="app-footer">
        <p>TorahLens - Dive Deep</p>
      </footer>
    </div>
  );
};

export default App;