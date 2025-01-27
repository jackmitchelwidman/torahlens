import React, { useState, useRef, useEffect } from 'react';
import './styles/App.css';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [aiCommentary, setAiCommentary] = useState('');
  const [perspective, setPerspective] = useState('Theological');
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentary, setLoadingCommentary] = useState(false);
  const [error, setError] = useState('');
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

  const backendUrl = '';

  const stripHtml = (html) => {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  };

  const fetchPassage = async () => {
    setLoadingPassage(true);
    setError('');
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setHebrew(stripHtml(data.hebrew));
        setEnglish(stripHtml(data.english));
      }
    } catch (err) {
      setError('Error fetching passage. Please try again.');
      console.error(err);
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchAiCommentary = async () => {
    setLoadingCommentary(true);
    setError('');
    try {
      const response = await fetch(
        `${backendUrl}/api/get_ai_commentary?passage=${encodeURIComponent(passage.trim())}&perspective=${perspective}`
      );
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setAiCommentary(data.commentary);
      }
    } catch (err) {
      setError('Error fetching AI commentary. Please try again.');
      console.error(err);
    } finally {
      setLoadingCommentary(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>TorahLens</h1>
      </header>
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
              You can enter references in English (e.g., "Genesis 1:1") or Hebrew (e.g., "בראשית א:א")
            </div>
          </div>
          <button onClick={fetchPassage} disabled={loadingPassage} className="button-primary">
            {loadingPassage ? 'Loading...' : 'Get Passage'}
          </button>
        </div>

        <div className="perspective-section">
          <h3>AI Commentary Perspective</h3>
          {['Theological', 'Philosophical', 'Secular'].map((perspectiveOption) => (
            <label key={perspectiveOption} className="radio-label">
              <input
                type="radio"
                value={perspectiveOption}
                checked={perspective === perspectiveOption}
                onChange={() => setPerspective(perspectiveOption)}
              />
              {perspectiveOption}
            </label>
          ))}
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

        {error && <div className="error-message">{error}</div>}

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
