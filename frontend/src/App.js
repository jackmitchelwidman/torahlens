import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const App = () => {
  const [passage, setPassage] = useState('');
  const [hebrew, setHebrew] = useState('');
  const [english, setEnglish] = useState('');
  const [commentaries, setCommentaries] = useState([]);
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);

  const backendUrl = 'https://torahlens.herokuapp.com:5000';
    
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
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>ToraLens</h1>
      </header>

      <div style={styles.inputContainer}>
        <input
          type="text"
          placeholder="Enter Torah passage (e.g., Genesis 1:1)"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          style={styles.input}
        />
        <button onClick={fetchPassage} disabled={loadingPassage} style={styles.button}>
          {loadingPassage ? 'Loading...' : 'Get Passage'}
        </button>
        <button onClick={fetchCommentaries} disabled={loadingCommentaries} style={styles.button}>
          {loadingCommentaries ? 'Loading...' : 'Get Commentaries'}
        </button>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Hebrew Text</h2>
        <div
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(hebrew) }}
          style={styles.textBlock}
        />
        <h2 style={styles.sectionTitle}>English Text</h2>
        <div
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(english) }}
          style={styles.textBlock}
        />
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Commentaries</h2>
        {commentaries.length > 0 ? (
          commentaries.map((commentary, index) => (
            <div key={index} style={styles.commentaryBlock}>
              <h3 style={styles.commentator}>{commentary.commentator}</h3>
              <div
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(commentary.text),
                }}
                style={styles.commentaryText}
              />
            </div>
          ))
        ) : (
          <p style={styles.noCommentaries}>No commentaries available.</p>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    fontFamily: "'Alef', sans-serif",
    backgroundColor: '#fefcf4',
    color: '#4a4a4a',
    padding: '20px',
    lineHeight: '1.6',
  },
  header: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '2.5em',
    color: '#3b3a30',
  },
  inputContainer: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  input: {
    padding: '10px',
    fontSize: '1em',
    width: '300px',
    border: '1px solid #ccc',
    borderRadius: '5px',
    marginRight: '10px',
  },
  button: {
    padding: '10px 15px',
    fontSize: '1em',
    color: '#fff',
    backgroundColor: '#0074d9',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginLeft: '5px',
  },
  section: {
    marginBottom: '40px',
  },
  sectionTitle: {
    fontSize: '1.5em',
    marginBottom: '10px',
    color: '#3b3a30',
  },
  textBlock: {
    backgroundColor: '#ffffff',
    padding: '15px',
    borderRadius: '5px',
    boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
    marginBottom: '20px',
  },
  commentaryBlock: {
    marginBottom: '20px',
    padding: '10px',
    backgroundColor: '#ffffff',
    borderRadius: '5px',
    boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
  },
  commentator: {
    fontSize: '1.2em',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  commentaryText: {
    fontSize: '1em',
    lineHeight: '1.6',
  },
  noCommentaries: {
    fontStyle: 'italic',
    color: '#666',
  },
};

export default App;

