import React, { useState } from "react";
import DOMPurify from "dompurify";

const App = () => {
  const [passage, setPassage] = useState("");
  const [hebrew, setHebrew] = useState("");
  const [english, setEnglish] = useState("");
  const [commentaries, setCommentaries] = useState([]);
  const [comparisons, setComparisons] = useState("");
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [loadingCommentaries, setLoadingCommentaries] = useState(false);
  const [loadingComparisons, setLoadingComparisons] = useState(false);

  const backendUrl = "https://torahlens-827cce34fdb8.herokuapp.com";

  const fetchPassage = async () => {
    setLoadingPassage(true);
    try {
      const response = await fetch(
        `${backendUrl}/api/get_passage?passage=${encodeURIComponent(
          passage.trim()
        )}`
      );
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setHebrew(data.hebrew);
        setEnglish(data.english);
      }
    } catch (error) {
      console.error("Error fetching passage:", error);
      alert("Error fetching passage. Please try again.");
    } finally {
      setLoadingPassage(false);
    }
  };

  const fetchCommentaries = async () => {
    setLoadingCommentaries(true);
    try {
      const response = await fetch(
        `${backendUrl}/api/get_commentaries?passage=${encodeURIComponent(
          passage.trim()
        )}`
      );
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setCommentaries(data.commentaries);
      }
    } catch (error) {
      console.error("Error fetching commentaries:", error);
      alert("Error fetching commentaries. Please try again.");
    } finally {
      setLoadingCommentaries(false);
    }
  };

  const fetchComparisons = async () => {
    setLoadingComparisons(true);
    try {
      const response = await fetch(
        `${backendUrl}/api/get_comparisons?passage=${encodeURIComponent(
          passage.trim()
        )}`
      );
      const data = await response.json();
      if (data.error) {
        alert(data.error);
      } else {
        setCommentaries(data.commentaries);
        setComparisons(data.comparisons);
      }
    } catch (error) {
      console.error("Error fetching comparisons:", error);
      alert("Error fetching comparisons. Please try again.");
    } finally {
      setLoadingComparisons(false);
    }
  };

  return (
    <div className="app">
      <h1>ToraLens</h1>
      <div className="input-container">
        <input
          type="text"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          placeholder="Enter a passage (e.g., Genesis 1:1)"
        />
        <button onClick={fetchPassage} disabled={loadingPassage}>
          {loadingPassage ? "Loading..." : "Get Passage"}
        </button>
        <button onClick={fetchCommentaries} disabled={loadingCommentaries}>
          {loadingCommentaries ? "Loading..." : "Get Commentaries"}
        </button>
        <button onClick={fetchComparisons} disabled={loadingComparisons}>
          {loadingComparisons ? "Loading..." : "Get Comparisons"}
        </button>
      </div>
      <div className="results">
        {hebrew && (
          <div>
            <h2>Hebrew</h2>
            <div
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(hebrew) }}
            />
          </div>
        )}
        {english && (
          <div>
            <h2>English</h2>
            <div
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(english) }}
            />
          </div>
        )}
        {commentaries.length > 0 && (
          <div>
            <h2>Commentaries</h2>
            {commentaries.map((commentary, index) => (
              <details key={index}>
                <summary>{commentary.commentator}</summary>
                <p
                  dangerouslySetInnerHTML={{
                    __html: DOMPurify.sanitize(commentary.text),
                  }}
                />
              </details>
            ))}
          </div>
        )}
        {comparisons && (
          <div>
            <h2>Comparisons</h2>
            <p
              dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(comparisons),
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;

