import React, { useState } from 'react';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);
  const [error, setError] = useState('');

  const backendUrl = 'https://torahlens-827cce34fdb8.herokuapp.com';

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
      }
    } catch (err) {
      setError('Error fetching commentaries. Please try again.');
      console.error(err);
    } finally {
      setLoadingCommentaries(false);
    }
  };

  return (
    <div className="App" style={{ padding: '20px' }}>
      <h1>TorahLens</h1>
      <div>
        <input
          type="text"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          placeholder="Enter passage (e.g., Genesis 1:1)"
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={fetchPassage} disabled={loadingPassage} style={{ marginRight: '10px' }}>
          {loadingPassage ? 'Loading...' : 'Get Passage'}
        </button>
        <button onClick={fetchCommentaries} disabled={loadingCommentaries}>
          {loadingCommentaries ? 'Loading...' : 'Get Commentaries'}
        </button>
      </div>

      {error && <div style={{ color: 'red', margin: '10px 0' }}>{error}</div>}

      {hebrew && (
        <div style={{ margin: '20px 0' }}>
          <h2>Hebrew Text:</h2>
          <div style={{ direction: 'rtl', textAlign: 'right' }}>{hebrew}</div>
          <h2>English Translation:</h2>
          <div>{english}</div>
        </div>
      )}

      {commentaries.length > 0 && (
        <div style={{ margin: '20px 0' }}>
          <h2>Commentaries:</h2>
          {commentaries.map((commentary, index) => (
            <div key={index} style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}>
              <h3 style={{ color: '#444', marginBottom: '10px' }}>{commentary.commentator}</h3>
              <div>{commentary.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;
