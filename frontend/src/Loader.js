import React from 'react';
import './Loader.css';
const Loader = () => {
  return (
    <div className="loader">
      <div className="spinner"></div>
      <div className="message">Procesando...</div>
    </div>
  );
};

export default Loader;