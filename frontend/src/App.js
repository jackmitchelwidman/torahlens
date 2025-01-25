import React, { useState } from 'react';
import DOMPurify from 'dompurify';
import './App.css'; // Ensure this file includes the accordion styles

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [comparisons, setComparisons] = useState([]);
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);
  const [loadingComparisons, setLoadingComparisons] = useState(false);

  const backendUrl = 'https://torahlens-827cce34fdb8.herokuapp.com';

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

  const fetchComparisons = async () => {
    setLoadingComparisons(true);
    try {
      const response = await fetch(`${backendUrl}/api/get_comparisons?passage=${encodeURIComponent(passage.trim())}`);
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setComparisons(data.comparisons);
      }
    } catch (error) {
      console.error('Error fetching comparisons:', error);
      alert('Error fetching comparisons. Please try again.');
    } finally {
      setLoadingComparisons(false);
    }
  };

  return (
    <div className="app-container">
      <h1>ToraLens</h1>
      <div className="input-container">
        <input
          type="text"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          placeholder="Enter a passage (e.g., Genesis 1:1)"
        />
        <button onClick={fetchPassage} disabled={loadingPassage}>
          {loadingPassage ? 'Loading...' : 'Get Passage'}
        </button>
        <button onClick={fetchCommentaries} disabled={loadingCommentaries}>
          {loadingCommentaries ? 'Loading...' : 'Get Commentaries'}
        </button>
        <button onClick={fetchComparisons} disabled={loadingComparisons}>
          {loadingComparisons ? 'Loading...' : 'Get Comparisons'}
        </button>
      </div>
      <div className="passage-container">
        <h2>Passage</h2>
        {hebrew && (
          <div>
            <h3>Hebrew Text</h3>
            <p>{hebrew}</p>
          </div>
        )}
        {english && (
          <div>
            <h3>English Text</h3>
            <p>{english}</p>
          </div>
        )}
      </div>
      <div className="commentaries-container">
        <h2>Commentaries</h2>
        {commentaries.length > 0 ? (
          commentaries.map((commentary, index) => (
            <div key={index}>
              <h3>{commentary.commentator}</h3>
              <p
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(commentary.text),
                }}
              />
            </div>
          ))
        ) : (
          <p>No commentaries to display.</p>
        )}
      </div>
      <div className="comparisons-container">
        <h2>Comparisons</h2>
        {comparisons.length > 0 ? (
          comparisons.map((comparison, index) => (
            <div key={index} className="accordion">
              <button
                className="accordion-header"
                onClick={(e) => {
                  const body = e.target.nextElementSibling;
                  body.classList.toggle('expanded');
                }}
              >
                {comparison.commentators}
              </button>
              <div className="accordion-body">
                <p>{comparison.comparison}</p>
              </div>
            </div>
          ))
        ) : (
          <p>No comparisons to display.</p>
        )}
      </div>
    </div>
  );
};

export default App;

