import React from 'react';
import womenCookImage from '../../assets/photos/women-cook.jpg';

const JoinComponent: React.FC = () => {
  return (
    <div
      className="relative min-h-[70vh] sm:h-[80vh] flex items-center justify-center bg-cover bg-center z-0"
      style={{ backgroundImage: `url(${womenCookImage})` }}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-black/70 to-black/50"></div>

      <div className="relative text-center text-white px-4 sm:px-6 z-10 max-w-5xl py-12 sm:py-0">
        <h2 className="text-2xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold tracking-tight leading-tight drop-shadow-2xl mb-4 sm:mb-6">
          Ready to Maximize Your 
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-600">
            Restaurant's Potential?
          </span>
        </h2>

        <p className="text-base sm:text-lg lg:text-xl xl:text-2xl font-medium mb-6 sm:mb-8 drop-shadow-lg max-w-4xl mx-auto px-2">
          Join hundreds of restaurants already earning more by hosting events, 
          meetings, and celebrations during off-peak hours.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-8 sm:mb-10 text-center max-w-2xl sm:max-w-none mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 border border-white/20">
            <div className="text-2xl sm:text-3xl font-bold text-blue-400">+40%</div>
            <div className="text-xs sm:text-sm">Revenue Increase</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 border border-white/20">
            <div className="text-2xl sm:text-3xl font-bold text-blue-400">24/7</div>
            <div className="text-xs sm:text-sm">Booking Management</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 sm:p-4 border border-white/20">
            <div className="text-2xl sm:text-3xl font-bold text-blue-400">0%</div>
            <div className="text-xs sm:text-sm">Setup Fees</div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 max-w-md sm:max-w-none mx-auto">
          <button className="bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 sm:py-4 sm:px-8 rounded-lg shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-200 text-sm sm:text-base">
            Join as Restaurant Partner
          </button>
          <button className="border-2 border-white bg-white/10 backdrop-blur-sm text-white font-semibold py-3 px-6 sm:py-4 sm:px-8 rounded-lg hover:bg-white/20 transition-all duration-200 text-sm sm:text-base">
            Learn More
          </button>
        </div>

        <p className="text-xs sm:text-sm mt-4 sm:mt-6 opacity-90">
          ✨ Free to join • No monthly fees • Instant payouts
        </p>
      </div>
    </div>
  );
};

export default JoinComponent; 