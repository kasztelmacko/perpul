import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Process() {
  const [processedImages, setProcessedImages] = useState({});

  useEffect(() => {
    handleProcess();
  }, []);

  const handleProcess = async () => {
    try {
      const response = await axios.post('http://localhost:8000/process');
      setProcessedImages(response.data);
    } catch (error) {
      console.error('Error processing image:', error);
    }
  };

  return (
    <div>
      <h2>Processed Images</h2>
      {processedImages.img_cluster_url && (
        <div>
          <h3>Clustered Image</h3>
          <img src={processedImages.img_cluster_url} alt="Clustered" />
        </div>
      )}
      {processedImages.img_outline_url && (
        <div>
          <h3>Outline Image</h3>
          <img src={processedImages.img_outline_url} alt="Outline" />
        </div>
      )}
    </div>
  );
}

export default Process;