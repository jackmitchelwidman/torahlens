import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [comparison, setComparison] = useState('');
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
        setCommentaries(data.commentaries || []);
        setComparison(data.comparison || '');
      }
    } catch (err) {
      setError('Error fetching commentaries. Please try again.');
      console.error(err);
    } finally {
      setLoadingCommentaries(false);
    }
  };

  return (
    <div className="App">
      <h1>ToraLens</h1>
      <input
        type="text"
        placeholder="Enter passage (e.g., Genesis 1:1)"
        value={passage}
        onChange={(e) => setPassage(e.target.value)}
      />
      <button onClick={fetchPassage} disabled={loadingPassage}>
        {loadingPassage ? 'Loading...' : 'Get Passage'}
      </button>
      <button onClick={fetchCommentaries} disabled={loadingCommentaries}>
        {loadingCommentaries ? 'Loading...' : 'Get Commentaries'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {hebrew && <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(hebrew) }} />}
      {english && <p>{english}</p>}
      {commentaries.length > 0 && (
        <div>
          <h2>Commentaries</h2>
          {commentaries.map((c, idx) => (
            <div key={idx}>
              <strong>{c.source}</strong>: {c.text}
            </div>
          ))}
        </div>
      )}
      {comparison && (
        <div>
          <h2>Comparison</h2>
          <p>{comparison}</p>
        </div>
      )}
    </div>
  );
};

export default App;

