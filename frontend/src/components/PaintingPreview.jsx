import React from 'react';

const PaintingPreview = ({ painting, displayedImage, processing, processedImages, handleProcess, handlePreviewClick }) => {
  return (
    <div className="w-2/3">
      <div className="relative inline-block mb-4">
      <img 
          src={displayedImage || painting.img_url} 
          alt="Displayed painting" 
          className="max-h-[800px] w-auto object-contain rounded-lg shadow-lg"
        />
        {!processing && Object.keys(processedImages).length === 0 && (
          <button
            onClick={handleProcess}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                       bg-black text-white px-6 py-1 rounded-lg text-sm font-semibold 
                       hover:bg-gray-800 transition duration-300 ml-2"
          >
            Process
          </button>
        )}
        {processing && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                          bg-black text-white px-6 py-1 rounded-lg text-sm font-semibold">
            <span className="loading loading-infinity loading-md text-white"></span>
          </div>
        )}
      </div>
      <div className="h-24 mt-4 flex space-x-4 overflow-x-auto">
        {painting.img_url && (
          <img 
            src={painting.img_url} 
            alt="Original" 
            className="h-full w-auto object-contain rounded-lg cursor-pointer"
            onClick={() => handlePreviewClick(painting.img_url)}
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
  );
};

export default PaintingPreview;