import React, { useState } from 'react';

const PaintingOptions = ({ processedImages, handleProcess, processing }) => {
  const [isProcessed, setIsProcessed] = useState(false);

  const handleProcessClick = async () => {
    await handleProcess();
    setIsProcessed(true);
  };

  return (
    <div className="w-1/3">
      <h1 className="text-3xl font-bold mb-4">Paint by Numbers kit</h1>
      <p className="text-2xl font-semibold mb-6">130 zł</p>
      
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Size</h2>
        <div className="flex space-x-2">
          {['21 x 29 cm', '40 x 50 cm'].map(size => (
            <button key={size} className="px-4 py-2 border rounded-md hover:bg-gray-100">
              {size}
            </button>
          ))}
        </div>
      </div>

      {processedImages.label_color_mapping && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-2">Color Palette</h2>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(processedImages.label_color_mapping).map(([label, color]) => (
              <div key={label} className="flex items-center">
                <div 
                  className="w-6 h-6 rounded-full mr-2" 
                  style={{ backgroundColor: `rgb(${color.join(',')})` }}
                ></div>
                <span className="text-sm">{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {!processing && !isProcessed && (
        <button
          onClick={handleProcessClick}
          className="w-full bg-black text-white py-3 rounded-lg text-lg font-semibold 
                     hover:bg-gray-800 transition duration-300"
        >
          Process
        </button>
      )}
      {processing && (
        <div className="w-full bg-black text-white py-3 rounded-lg text-lg font-semibold text-center">
          <span className="loading loading-infinity loading-md text-white"></span>
        </div>
      )}
      {!processing && isProcessed && (
        <button
          className="w-full bg-green-500 text-white py-3 rounded-lg text-lg font-semibold 
                     hover:bg-green-600 transition duration-300"
        >
          Add to cart
        </button>
      )}
    </div>
  );
};

export default PaintingOptions;