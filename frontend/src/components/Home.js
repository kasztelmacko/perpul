import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function Home() {
    const [file, setFile] = useState(null);
    const [uploadedImageUrl, setUploadedImageUrl] = useState('');
    const [processedImages, setProcessedImages] = useState({});
    const [displayedImage, setDisplayedImage] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const [previewUrl, setPreviewUrl] = useState(null);

    const handleSubmit = async () => {
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

    const onDrop = useCallback((acceptedFiles) => {
        const file = acceptedFiles[0];
        setFile(file);
        setPreviewUrl(URL.createObjectURL(file));
    }, []);
    
    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });
    
    useEffect(() => {
        setIsDragging(isDragActive);
    }, [isDragActive]);


    return (
      <div className="container mx-auto p-4">
        <div className="bg-gray-800 p-8 rounded-lg h-[900px] flex flex-col">
          {!previewUrl ? (
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed p-8 text-center cursor-pointer flex-grow flex items-center justify-center ${
                isDragging ? 'border-blue-500 bg-blue-100' : 'border-gray-300'
              }`}
            >
              <input {...getInputProps()} />
              <p className="text-white">Drag and drop an image here, or click to select a file</p>
            </div>
          ) : (
            <div className="flex h-full">
              <div className="w-[50%] pr-4 overflow-hidden flex flex-col">
                <div className="flex flex-col h-full">
                  <div className="flex-grow flex items-end justify-left overflow-hidden">
                    <img 
                      className="max-h-[calc(100%-100px)] max-w-full rounded-lg object-contain"
                      src={displayedImage || previewUrl} 
                      alt="Preview" 
                    />
                  </div>
                  <div className="h-24 mt-4 flex space-x-4 overflow-x-auto">
                    {uploadedImageUrl && (
                      <img 
                        src={uploadedImageUrl} 
                        alt="Original" 
                        className="h-full w-auto object-contain rounded-lg cursor-pointer"
                        onClick={() => handlePreviewClick(uploadedImageUrl)}
                      />
                    )}
                    {processedImages.img_cluster_url && (
                      <img 
                        src={processedImages.img_cluster_url} 
                        alt="Clustered" 
                        className="h-full w-auto object-contain rounded-lg cursor-pointer"
                        onClick={() => handlePreviewClick(processedImages.img_cluster_url)}
                      />
                    )}
                    {processedImages.img_outline_url && (
                      <img 
                        src={processedImages.img_outline_url} 
                        alt="Outline" 
                        className="h-full w-auto object-contain rounded-lg cursor-pointer"
                        onClick={() => handlePreviewClick(processedImages.img_outline_url)}
                      />
                    )}
                  </div>
                </div>
              </div>
              <div className="w-[30%] pl-4 flex flex-col">
                <button onClick={handleSubmit} className="btn btn-primary mb-4">
                  Upload
                </button>
                {uploadedImageUrl && (
                  <button onClick={handleProcess} className="btn btn-secondary mb-4">
                    Process Image
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
};

export default Home;