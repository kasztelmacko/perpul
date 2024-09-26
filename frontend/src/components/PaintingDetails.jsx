import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import PaintingPreview from './PaintingPreview';
import PaintingOptions from './PaintingOptions';

const PaintingDetails = () => {
  const [painting, setPainting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [processedImages, setProcessedImages] = useState({});
  const [displayedImage, setDisplayedImage] = useState('');
  const [error, setError] = useState(null);
  const { uniqueFilename } = useParams();

  useEffect(() => {
    const fetchPainting = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/painting/${uniqueFilename}`);
        setPainting(response.data);
        setDisplayedImage(response.data.img_url);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch painting details');
        setLoading(false);
      }
    };

    fetchPainting();
  }, [uniqueFilename]);

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const response = await axios.post('http://localhost:8000/process');
      setProcessedImages(response.data);
    } catch (error) {
      console.error('Error processing image:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handlePreviewClick = (imageUrl) => {
    setDisplayedImage(imageUrl);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!painting) return <div>No painting found</div>;

  return (
    <div className="container mx-auto mt-8 px-4">
      <div className="flex flex-col lg:flex-row lg:space-x-8 space-y-8 lg:space-y-0">
        <div className="w-full lg:w-2/3">
          <PaintingPreview 
            painting={painting}
            displayedImage={displayedImage}
            processedImages={processedImages}
            handlePreviewClick={handlePreviewClick}
          />
        </div>
        <div className="w-full lg:w-1/3">
          <PaintingOptions 
            processedImages={processedImages} 
            handleProcess={handleProcess} 
            processing={processing} 
          />
        </div>
      </div>
    </div>
  );
};

export default PaintingDetails;