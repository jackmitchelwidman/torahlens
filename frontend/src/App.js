import React, { useState, useRef, useEffect } from 'react';

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

  // Add effect to handle scrolling when commentary updates
  useEffect(() => {
    if (aiCommentary && commentaryRef.current) {
      // Try multiple scroll methods
      const scrollToCommentary = () => {
        // Method 1: scrollIntoView
        commentaryRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });

        // Method 2: manual scroll as backup
        const yOffset = -20; // Offset to account for any headers
        const element = commentaryRef.current;
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        
        window.scrollTo({
          top: y,
          behavior: 'smooth'
        });
      };

      // Add a small delay to ensure DOM is ready
      setTimeout(scrollToCommentary, 300);
    }
  }, [aiCommentary]);

  const backendUrl = ''; // Leave empty for relative path to the backend.

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
          <input
            type="text"
            value={passage}
            onChange={(e) => setPassage(e.target.value)}
            placeholder="Enter passage (e.g., Genesis 1:1)"
            className="input-field"
          />
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
          <button 
            onClick={fetchAiCommentary} 
            disabled={!english || loadingCommentary}
            className="button-secondary"
          >
            {loadingCommentary ? 'Ruminating...' : 'Get AI Commentary'}
          </button>
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

/** CSS styles **/

const styles = `
body {
  font-family: 'Alef', sans-serif;
  margin: 0;
  background-color: #f5f5f5;
  color: #333;
  scroll-behavior: smooth;
}

.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  padding-bottom: 60px; /* Add padding to account for fixed footer */
}

.app-header {
  background-color: #0038b8;
  color: white;
  width: 100%;
  text-align: center;
  padding: 15px 0;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
}

.app-main {
  max-width: 800px;
  width: 100%;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.input-section, .perspective-section, .passage-section, .commentary-section {
  margin-bottom: 20px;
}

.input-field {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 70%;
}

.button-primary, .button-secondary {
  padding: 10px 15px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.button-primary {
  background-color: #0056e6;
  color: white;
}

.button-secondary {
  background-color: #28a745;
  color: white;
}

.radio-label {
  margin-right: 15px;
  font-size: 14px;
  cursor: pointer;
}

.hebrew-text {
  direction: rtl;
  text-align: right;
  font-size: 18px;
  color: #0056e6;
}

.english-text {
  font-size: 18px;
}

.error-message {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

.app-footer {
  text-align: center;
  padding: 10px 0;
  background-color: #0038b8;
  color: white;
  width: 100%;
  position: fixed;
  bottom: 0;
}

.commentary-section {
  scroll-margin-top: 20px;
}
`;

document.head.insertAdjacentHTML("beforeend", `<style>${styles}</style>`);
