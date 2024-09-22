import React from 'react';

const Navbar = () => {
  const scrollToFAQ = (event) => {
    event.preventDefault();
    const faqSection = document.getElementById('faq-section');
    faqSection.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <nav className="absolute top-0 left-0 right-0 z-10 flex justify-between items-center p-6">
      <div className="text-white font-bold text-4xl">perpul.</div>
      <div className="bg-white flex items-center rounded-md">
        <a href="#" className="text-black font-bold px-6 py-2 hover:bg-gray-100 transition duration-300">About</a>
        <div className="h-6 w-px bg-gray-300"></div>
        <a href="#" className="text-black font-bold px-6 py-2 hover:bg-gray-100 transition duration-300">Blog</a>
        <div className="h-6 w-px bg-gray-300"></div>
        <a href="#faq-section" onClick={scrollToFAQ} className="text-black font-bold px-6 py-2 hover:bg-gray-100 transition duration-300">FAQ</a>
      </div>
    </nav>
  );
};

export default Navbar;