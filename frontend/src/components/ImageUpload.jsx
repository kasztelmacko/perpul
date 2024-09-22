import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const ImageUploadForm = () => {
  const [file, setFile] = useState(null);
  const [imageType, setImageType] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTypeChange = (e) => {
    setImageType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      console.log('Upload response:', response.data);

      if (response.data && response.data.unique_filename) {
        const filenameWithoutExtension = response.data.unique_filename.split('.')[0];
        navigate(`/painting/${filenameWithoutExtension}`);
      } else {
        setError('Upload successful, but no unique filename received');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.detail || 'Error uploading file');
    } finally {
      setIsLoading(false);
    }
  };

return (
      <form onSubmit={handleSubmit } className="bg-white shadow-lg mx-auto max-w-6xl flex items-center justify-between p-2 rounded-lg">
        <div className="flex-1 px-2">
          <label htmlFor="file-upload" className="block text-xs text-gray-500 mb-1">Upload Image</label>
          <input
            id="file-upload"
            name="file-upload"
            type="file"
            onChange={handleFileChange}
            accept="image/*"
            className="w-full text-sm text-gray-500 cursor-pointer
                       file:mr-4 file:py-2 file:px-4
                       file:rounded-md file:border-0
                       file:text-sm file:font-semibold
                       file:bg-black file:text-white
                       hover:file:bg-grey-700"
          />
        </div>
        <div className="flex-1 px-2 border-l border-gray-200">
          <label htmlFor="image-type" className="block text-xs text-gray-500 mb-1">Image Type</label>
          <select
            id="image-type"
            name="image-type"
            onChange={handleTypeChange}
            value={imageType}
            className="w-full text-sm border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-black"
          >
            <option value="portrait">Portrait</option>
            <option value="animal">Animal</option>
            <option value="landscape">Landscape</option>
            <option value="abstract">Abstract</option>
          </select>
        </div>
        <button
        type="submit"
        className="bg-black text-white px-6 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition duration-300 ml-2 min-w-[100px]"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="loading loading-infinity loading-md text-white"></span>
        ) : (
          'Upload →'
        )}
      </button>
      </form>
  );
};

export default ImageUploadForm;