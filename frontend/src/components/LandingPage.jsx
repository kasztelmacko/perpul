import React from 'react';
import Navbar from './Navbar';
import ImageUploadForm from './ImageUpload';
import Intro from './Intro';
import FAQSection from './FAQ';
import Footer from './Footer';



const MainContent = () => (
    <main className="relative h-screen w-full overflow-hidden">
        <Navbar />
      <div className="absolute inset-0 diff">
        <div className="diff-item-1">
          <img 
            alt="" 
            src="https://wpoichocccyoxzippfzj.supabase.co/storage/v1/object/public/useful_images/index_img.jpg"
          />
        </div>
        <div className="diff-item-2">
          <img 
            alt="" 
            src="https://wpoichocccyoxzippfzj.supabase.co/storage/v1/object/public/useful_images/index_img_c.png"
          />
        </div>
        <div className="diff-resizer z-20"></div>
      </div>

      <div className="absolute inset-x-0 bottom-4 sm:bottom-auto sm:top-[calc(50%-5rem)] sm:transform sm:-translate-y-1/2 z-10 w-11/12 sm:w-auto mx-auto">
        <ImageUploadForm />
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-1/6 bg-black"></div>
      <div className="absolute inset-0 flex flex-col justify-end">
        <div className="p-6 sm:p-10 md:p-14 lg:p-20 xl:p-20">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold text-white leading-tight max-w-6xl">
            Find a photo. <br />
            Paint it by numbers.
          </h1>
        </div>
      </div>

    </main>
  );

const LandingPage = () => (
  <div className="min-h-screen overflow-y-auto">
    <div className="relative h-screen">
      <MainContent />
    </div>
    <div className="relative z-10 bg-white">
      <Intro />
    </div>
    <div id="faq-section">
      <FAQSection />
    </div>
    <Footer />
  </div>
);

export default LandingPage;