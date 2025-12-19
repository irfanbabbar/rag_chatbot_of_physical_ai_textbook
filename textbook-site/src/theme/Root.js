import React, { useState, useEffect, useContext, createContext } from 'react';

const SelectedTextContext = createContext(null);

export const useSelectedText = () => useContext(SelectedTextContext);

export default function Root({
  children
}) {
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      const text = selection.toString().trim();
      if (text.length > 0 && text !== selectedText) {
        setSelectedText(text);
        console.log('Selected Text:', text);
        // Here you would typically send the selected text to your chatbot component or backend
      }
    };

    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [selectedText]);

  return (
    <SelectedTextContext.Provider value={selectedText}>
      {children}
    </SelectedTextContext.Provider>
  );
}
