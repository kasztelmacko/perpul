import React, { useState } from 'react';
import axios from 'axios';

function Home() {
    const [file, setFile] = useState(null);
    const [uploadedImageUrl, setUploadedImageUrl] = useState('');
    const [processedImages, setProcessedImages] = useState({});
    const [displayedImage, setDisplayedImage] = useState('');
  
    const handleFileChange = (e) => {
      setFile(e.target.files[0]);
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!file) return;
  
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        const response = await axios.post('http://localhost:8000/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setUploadedImageUrl(response.data.image_url);
        setDisplayedImage(response.data.image_url);
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    };
  
    const handleProcess = async () => {
      try {
        const response = await axios.post('http://localhost:8000/process');
        setProcessedImages(response.data);
      } catch (error) {
        console.error('Error processing image:', error);
      }
    };
  
    const handlePreviewClick = (imageUrl) => {
      setDisplayedImage(imageUrl);
    };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Welcome to Pokolorach</h1>
      <h2 className="text-xl mb-2">Upload Image</h2>
      <form onSubmit={handleSubmit} className="mb-4">
        <input type="file" onChange={handleFileChange} className="file-input file-input-bordered w-full max-w-xs" />
        <button type="submit" className="btn btn-primary ml-2">Upload</button>
      </form>
      {displayedImage && (
        <div className="mb-4">
          <img src={displayedImage} alt="Displayed" className="max-w-lg mx-auto mb-2" />
          {uploadedImageUrl && <button onClick={handleProcess} className="btn btn-secondary">Process Image</button>}
        </div>
      )}
      <div className="flex justify-around">
        {uploadedImageUrl && (
          <div className="text-center">
            <h3 className="font-semibold mb-1">Original</h3>
            <img 
              src={uploadedImageUrl} 
              alt="Original" 
              className="w-36 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => handlePreviewClick(uploadedImageUrl)}
            />
          </div>
        )}
        {processedImages.img_cluster_url && (
          <div className="text-center">
            <h3 className="font-semibold mb-1">Clustered</h3>
            <img 
              src={processedImages.img_cluster_url} 
              alt="Clustered" 
              className="w-36 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => handlePreviewClick(processedImages.img_cluster_url)}
            />
          </div>
        )}
        {processedImages.img_outline_url && (
          <div className="text-center">
            <h3 className="font-semibold mb-1">Outline</h3>
            <img 
              src={processedImages.img_outline_url} 
              alt="Outline" 
              className="w-36 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => handlePreviewClick(processedImages.img_outline_url)}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;