import React, { useState, useRef, useEffect } from 'react';
import './styles/App.css';

const PERSPECTIVES = [
  "Theological",
  "Philosophical",
  "Secular",
  "Scientific"
];

const Overview = () => (
  <div className="overview-body">
    <p>
      TorahLens lets you read any passage of the Hebrew Bible in Hebrew and in English,
      then get a commentary on it written by an AI from the perspective you choose. The text comes
      from Sefaria, a free online library of Jewish texts: the traditional Hebrew alongside a modern
      Jewish Publication Society translation.
    </p>
    <p>
      The site covers the Torah (the Five Books of Moses) and the rest of the Hebrew Bible, which
      Christian readers know as the Old Testament. Whether you come to these books through Jewish
      tradition, Christian tradition, or curiosity, the steps are the same.
    </p>
    <h3>How to use it</h3>
    <ol>
      <li>
        <strong>Find a passage.</strong> Type a reference such as <em>Genesis 1:1</em> or{' '}
        <em>Exodus 20:1-17</em>, a Hebrew reference such as <em>בראשית א:א</em>, or describe the
        passage in plain words, like <em>Noah's Ark</em> or <em>the splitting of the Red Sea</em>.
        Then click <strong>Get Passage</strong>.
      </li>
      <li>
        <strong>Read it.</strong> The passage appears verse by verse, first in Hebrew and then in
        English, with verse numbers.
      </li>
      <li>
        <strong>Choose a perspective.</strong> Pick Theological, Philosophical, Secular, or
        Scientific, then click <strong>Get AI Commentary</strong>. Try a second perspective on the
        same passage and compare.
      </li>
    </ol>
    <p className="overview-note">
      The commentary is generated on the spot by an AI language model. Read it as a starting point
      for your own study, and check anything it claims against the text and traditional sources.
    </p>
  </div>
);

const AboutModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          Close
        </button>
        <h2>About TorahLens</h2>
        <Overview />
      </div>
    </div>
  );
};

const EXAMPLE_PHRASES = [
  "Noah's Ark",
  'The Tower of Babel',
  'The splitting of the Red Sea',
  'The Ten Commandments',
  'The binding of Isaac',
];

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState([]);
  const [english, setEnglish] = useState([]);
  const [startVerse, setStartVerse] = useState(1);
  const [passageRef, setPassageRef] = useState('');
  const [resolvedFrom, setResolvedFrom] = useState('');
  const [prevRef, setPrevRef] = useState(null);
  const [nextRef, setNextRef] = useState(null);
  const [fetchedInput, setFetchedInput] = useState('');
  const [aiCommentary, setAiCommentary] = useState('');
  const [perspective, setPerspective] = useState("Theological");
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentary, setLoadingCommentary] = useState(false);
  const [error, setError] = useState('');
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const isHome = english.length === 0;
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

  const cleanHebrewText = (text) => {
    return text
      .replace(/\u200b/g, '')  // Remove zero-width spaces
      .replace(/\u00a0/g, ' ') // Replace non-breaking spaces
      .replace(/[\u0591-\u05C7]/g, ''); // Optionally remove cantillation marks
  };

  const fetchPassage = async (text = passage) => {
    const query = (typeof text === 'string' ? text : passage).trim();
    if (!query) {
      setError('Please enter a passage reference');
      return;
    }

    setLoadingPassage(true);
    setError('');
    setHebrew([]);
    setEnglish([]);
    setAiCommentary('');
    
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      if (!response.ok) {
        setError(data.error || 'Please provide a valid reference format, such as "Genesis 1:1" or "בראשית א:א"');
        return;
      }
      
      if (data.error) {
        setError(data.error);
      } else {
        setHebrew((data.hebrew || []).map(cleanHebrewText));
        setEnglish(data.english || []);
        setStartVerse(data.start_verse || 1);
        setPassageRef(data.ref || '');
        setResolvedFrom(data.resolved_from || '');
        setPrevRef(data.prev_ref || null);
        setNextRef(data.next_ref || null);
        setFetchedInput(query);
      }
    } catch (err) {
      setError('Error fetching passage. Please try again with a valid reference.');
      console.error(err);
    } finally {
      setLoadingPassage(false);
    }
  };

  const goTo = (ref) => {
    if (!ref) return;
    setPassage(ref);
    fetchPassage(ref);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const PassageNav = () => (
    <div className="passage-nav">
      <button type="button" className="button-secondary" onClick={() => goTo(prevRef)} disabled={!prevRef || loadingPassage}>
        ← Previous
      </button>
      <button type="button" className="button-secondary" onClick={() => goTo(nextRef)} disabled={!nextRef || loadingPassage}>
        Next →
      </button>
    </div>
  );

  const fetchAiCommentary = async () => {
    if (!passage.trim()) {
      setError("Please fetch the passage first.");
      return;
    }

    setLoadingCommentary(true);
    setError("");
    setAiCommentary("");

    try {
      const url = new URL(`${backendUrl}/api/get_ai_commentary`, window.location.origin);
      // Use the resolved reference when the box still holds the input that produced it
      const ref = (passageRef && passage.trim() === fetchedInput) ? passageRef : passage.trim();
      url.searchParams.append('passage', ref);
      url.searchParams.append('perspective', perspective);

      const response = await fetch(url.toString());
      const data = await response.json();

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
      <header className="app-header marble">
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

      <main className={isHome ? 'app-main home' : 'app-main'}>
        {isHome && (
          <p className="tagline">
            Read any passage of the Hebrew Bible, in Hebrew and English, then explore it from
            different perspectives.
          </p>
        )}

        <div className="input-section">
          <div className="input-wrapper">
            <input
              type="text"
              value={passage}
              onChange={(e) => setPassage(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') fetchPassage(); }}
              placeholder="Genesis 1:1, בראשית א:א, or describe a passage"
              className="input-field"
              dir="auto"
              autoFocus
            />
          </div>
          <button onClick={fetchPassage} disabled={loadingPassage} className="button-primary">
            {loadingPassage ? 'Loading...' : 'Get Passage'}
          </button>
        </div>

        <div className="examples">
          <span className="examples-label">Try:</span>
          {EXAMPLE_PHRASES.map((phrase) => (
            <button
              key={phrase}
              type="button"
              className="example-chip"
              onClick={() => { setPassage(phrase); fetchPassage(phrase); }}
            >
              {phrase}
            </button>
          ))}
        </div>

        {isHome && (
          <button type="button" className="how-link" onClick={() => setIsAboutOpen(true)}>
            How does this work?
          </button>
        )}

        {error && <div className="error-message">{error}</div>}

        {!isHome && <div className="perspective-section">
          <h3>AI Commentary Perspective</h3>
          <div className="perspective-options">
            <select 
              value={perspective}
              onChange={(e) => setPerspective(e.target.value)}
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
              disabled={english.length === 0 || loadingCommentary}
              className="button-secondary"
            >
              {loadingCommentary ? 'Ruminating...' : 'Get AI Commentary'}
            </button>
          </div>
        </div>}

        {english.length > 0 && (
          <div className="passage-section">
            {passageRef && <div className="passage-ref">{passageRef}</div>}
            {resolvedFrom && <div className="resolved-note">Interpreted "{resolvedFrom}" as {passageRef}</div>}
            <h2>Hebrew Text:</h2>
            <div className="hebrew-text">
              {hebrew.map((v, i) => (
                <p key={i} className="verse">
                  <span className="verse-number">{startVerse + i}</span>{v}
                </p>
              ))}
            </div>
            <h2>English Translation:</h2>
            <div className="english-text">
              {english.map((v, i) => (
                <p key={i} className="verse">
                  <span className="verse-number">{startVerse + i}</span>{v}
                </p>
              ))}
            </div>
            <PassageNav />
          </div>
        )}

        {aiCommentary && (
          <div ref={commentaryRef} className="commentary-section">
            <h2>AI Commentary ({perspective} Perspective):</h2>
            <p>{aiCommentary}</p>
          </div>
        )}
      </main>
      <footer className="app-footer marble">
        <p>TorahLens - Dive Deep</p>
      </footer>
    </div>
  );
};

export default App;
