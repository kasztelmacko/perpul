import React from 'react';

const Intro = () => {
  return (
    <div className="relative left-0 right-0 bg-black z-10 h-96 flex items-center justify-center">
      <div className="text-center">
        <h1 className="sm:text-2xl md:text-4xl lg:text-6xl font-bold text-white leading-tight">
          Paint by Numbers
        </h1>
        <p className="mt-4 text-white">
          {/* Add your paragraph content here */}
        </p>
      </div>
    </div>
  );
};

export default Intro;