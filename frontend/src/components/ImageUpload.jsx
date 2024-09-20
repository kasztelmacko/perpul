import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const ImageUploadForm = () => {
  const [file, setFile] = useState(null);
  const [imageType, setImageType] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTypeChange = (e) => {
    setImageType(e.target.value);
  };

  const handleSubmit = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post('http://localhost:8000/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    } catch (error) {
        console.error('Error uploading file:', error);
    }
};

return (
      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="bg-white shadow-lg mx-auto max-w-6xl flex items-center justify-between p-2 rounded-lg">
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
                       file:rounded-full file:border-0
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
            <option value="landscape">Landscape</option>
            <option value="abstract">Abstract</option>
          </select>
        </div>
        <button
          type="submit"
          className="bg-black text-white px-6 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition duration-300 ml-2"
        >
          Upload →
        </button>
      </form>
  );
};

export default ImageUploadForm;