import React, { useState, useEffect } from 'react';
import { useSelectedText } from '@site/src/theme/Root';

const Chatbot = () => {
  const selectedText = useSelectedText();
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedText) {
      // Optionally, pre-fill the question or add a context message to chat history
      // For now, we'll just log it and it will be sent with the next question
      console.log('Chatbot received selected text:', selectedText);
    }
  }, [selectedText]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: 'user', content: question, selectedContext: selectedText };
    setChatHistory((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, selected_text: selectedText }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch response from backend');
      }

      const data = await response.json();
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      console.error('Chatbot error:', err);
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
      setQuestion('');
    }
  };

  return (
    <div style={styles.chatbotContainer}>
      <h3 style={styles.chatbotHeader}>Book Chatbot</h3>
      <div style={styles.chatHistory}>
        {chatHistory.map((msg, index) => (
          <div key={index} style={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}>
            <p><strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong> {msg.content}</p>
            {msg.selectedContext && <p style={styles.contextText}><em>(Context: {msg.selectedContext.substring(0, 100)}...)</em></p>}
            {msg.sources && msg.sources.length > 0 && (
              <div style={styles.sourcesContainer}>
                <strong>Sources:</strong>
                <ul>
                  {msg.sources.map((source, srcIndex) => (
                    <li key={srcIndex}>{source.split('/').pop()}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div style={styles.loadingMessage}>Thinking...</div>}
        {error && <div style={styles.errorMessage}>Error: {error}</div>}
      </div>
      <form onSubmit={handleSubmit} style={styles.chatForm}>
        <input
          type='text'
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder='Ask a question about the book...'
          style={styles.chatInput}
          disabled={loading}
        />
        <button type='submit' style={styles.chatButton} disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

const styles = {
  chatbotContainer: {
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '15px',
    margin: '20px auto',
    maxWidth: '600px',
    fontFamily: 'Arial, sans-serif',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  },
  chatbotHeader: {
    textAlign: 'center',
    marginBottom: '15px',
    color: '#333',
  },
  chatHistory: {
    maxHeight: '300px',
    overflowY: 'auto',
    border: '1px solid #eee',
    padding: '10px',
    marginBottom: '15px',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
  },
  userMessage: {
    backgroundColor: '#e6f7ff',
    padding: '8px',
    borderRadius: '5px',
    marginBottom: '8px',
    marginLeft: '20%',
    textAlign: 'right',
  },
  assistantMessage: {
    backgroundColor: '#e0ffe0',
    padding: '8px',
    borderRadius: '5px',
    marginBottom: '8px',
    marginRight: '20%',
    textAlign: 'left',
  },
  contextText: {
    fontSize: '0.8em',
    color: '#555',
    marginTop: '5px',
  },
  sourcesContainer: {
    marginTop: '5px',
    fontSize: '0.85em',
    color: '#666',
  },
  chatForm: {
    display: 'flex',
    gap: '10px',
  },
  chatInput: {
    flexGrow: '1',
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '5px',
    fontSize: '1em',
  },
  chatButton: {
    padding: '10px 15px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '1em',
  },
  loadingMessage: {
    textAlign: 'center',
    color: '#888',
    fontStyle: 'italic',
  },
  errorMessage: {
    textAlign: 'center',
    color: 'red',
    fontWeight: 'bold',
  },
};

export default Chatbot;
