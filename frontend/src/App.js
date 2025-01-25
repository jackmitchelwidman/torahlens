import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [comparisons, setComparisons] = useState('');
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);
  const [error, setError] = useState('');

  const backendUrl = 'https://torahlens-827cce34fdb8.herokuapp.com'; // Replace with your backend URL

  const fetchPassage = async () => {
    setLoadingPassage(true);
    setError('');
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setHebrew(data.hebrew);
        setEnglish(data.english);
      }
    } catch (err) {
      setError('Error fetching passage. Please try again.');
      console.error(err);
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchCommentaries = async () => {
    setLoadingCommentaries(true);
    setError('');
    try {
      const response = await fetch(`${backendUrl}/api/get_commentaries?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setCommentaries(data.commentaries);
        setComparisons(data.comparisons);
      }
    } catch (err) {
      setError('Error fetching commentaries. Please try again.');
      console.error(err);
    } finally {
      setLoadingCommentaries(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>ToraLens</h1>
        <p>Explore Torah passages and their commentaries.</p>
      </header>
      <main className="app-main">
        <div className="input-section">
          <label htmlFor="passage">Enter Passage (e.g., Genesis 1:1):</label>
          <input
            type="text"
            id="passage"
            value={passage}
            onChange={(e) => setPassage(e.target.value)}
            placeholder="Enter passage reference"
          />
          <div className="button-group">
            <button onClick={fetchPassage} disabled={loadingPassage}>
              {loadingPassage ? 'Loading Passage...' : 'Get Passage'}
            </button>
            <button onClick={fetchCommentaries} disabled={loadingCommentaries}>
              {loadingCommentaries ? 'Loading Commentaries...' : 'Get Commentaries'}
            </button>
          </div>
        </div>
        {error && <p className="error-message">{error}</p>}
        {hebrew && english && (
          <div className="passage-section">
            <h2>Passage</h2>
            <div className="passage">
              <div className="hebrew" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(hebrew) }} />
              <div className="english" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(english) }} />
            </div>
          </div>
        )}
        {commentaries.length > 0 && (
          <div className="commentaries-section">
            <h2>Commentaries</h2>
            <div className="accordion">
              {commentaries.map((commentary, index) => (
                <div key={index} className="accordion-item">
                  <input type="checkbox" id={`accordion-${index}`} />
                  <label htmlFor={`accordion-${index}`} className="accordion-title">
                    {commentary.commentator}
                  </label>
                  <div className="accordion-content">
                    <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(commentary.text) }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {comparisons && (
          <div className="comparisons-section">
            <h2>Comparisons</h2>
            <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comparisons) }} />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;

