import React, { useState } from 'react';

const FAQItem = ({ question, answer }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-gray-200">
      <button
        className="flex justify-between items-center w-full py-5 text-left"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="text-lg font-semibold text-gray-800">{question}</span>
        <svg
          className={`w-6 h-6 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="pb-5 text-gray-600">
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

const FAQSection = () => (
  <section className="bg-white py-16">
    <div className="container mx-auto px-4">
      <h2 className="text-sm font-semibold text-center text-blue-600 mb-2">FAQs</h2>
      <h3 className="text-3xl font-bold text-center mb-8">Frequently asked questions</h3>
      <div className="max-w-3xl mx-auto">
        <FAQItem
          question="What is painting by numbers?"
          answer=".."
        />
        <FAQItem
          question="How to choose the right photo?"
          answer=".."
        />
        <FAQItem
          question="Examples of good and bad photos"
          answer=".."
        />
        <FAQItem
          question="What is in the kit?"
          answer=".."
        />
        <FAQItem
          question="What are the benefits of painting by numbers?"
          answer=".."
        />
      </div>
    </div>
  </section>
);

export default FAQSection;
