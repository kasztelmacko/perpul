import React from 'react';

const Navbar = () => (
  <nav className="absolute top-0 left-0 right-0 z-10 flex justify-between items-center p-6">
    <div className="text-white font-bold text-4xl">perpul.</div>
    <div className="flex space-x-6">
      <a href="#" className="text-white font-bold hover:text-gray-300 transition duration-300">Blog</a>
      <a href="#" className="text-white font-bold hover:text-gray-300 transition duration-300">FAQ</a>
    </div>
  </nav>
);

export default Navbar;