import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);

  const backendUrl = 'http://localhost:5001'; // Replace with your backend URL

  const fetchPassage = async () => {
    setLoadingPassage(true);
    try {
      const response = await fetch(`${backendUrl}/api/get_passage?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setHebrew(data.hebrew);
        setEnglish(data.english);
      }
    } catch (error) {
      console.error('Error fetching passage:', error);
      alert('Error fetching passage. Please try again.');
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchCommentaries = async () => {
    setLoadingCommentaries(true);
    try {
      const response = await fetch(`${backendUrl}/api/get_commentaries?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setCommentaries(data.commentaries);
      }
    } catch (error) {
      console.error('Error fetching commentaries:', error);
      alert('Error fetching commentaries. Please try again.');
    } finally {
      setLoadingCommentaries(false);
    }
  };

  return (
    <div>
      <h1>ToraLens</h1>

      <div>
        <input
          type="text"
          placeholder="Enter Torah passage (e.g., Genesis 1:1)"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          style={{
            padding: '0.5em',
            fontSize: '1em',
            width: '300px',
          }}
        />
        <button onClick={fetchPassage} disabled={loadingPassage} style={{ marginLeft: '10px', padding: '0.5em' }}>
          {loadingPassage ? 'Loading...' : 'Get Passage'}
        </button>
        <button onClick={fetchCommentaries} disabled={loadingCommentaries} style={{ marginLeft: '10px', padding: '0.5em' }}>
          {loadingCommentaries ? 'Loading...' : 'Get Commentaries'}
        </button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>Hebrew Text</h2>
        <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(hebrew) }} style={{ whiteSpace: 'pre-line' }} />
        <h2>English Text</h2>
        <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(english) }} style={{ whiteSpace: 'pre-line' }} />
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>Commentaries</h2>
        {commentaries.length > 0 ? (
          commentaries.map((commentary, index) => (
            <div key={index} style={{ marginBottom: '20px' }}>
              <h3>{commentary.commentator}</h3>
              {/* Render WYSIWYG content */}
              <div
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(commentary.text),
                }}
              />
            </div>
          ))
        ) : (
          <p>No commentaries available.</p>
        )}
      </div>
    </div>
  );
};

export default App;

