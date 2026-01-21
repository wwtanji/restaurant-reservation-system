import React from 'react';
import NavbarComponent from '../components/section/NavbarComponent';
import RegionsComponent from '../components/herosection/MainText';
import HowItWorksSection from '../components/herosection/HowItWorksSection';
import JoinComponent from '../components/herosection/JoinComponent';
import FooterComponent from '../components/section/FooterComponent';

const MainPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-grow">
        <NavbarComponent />
        <RegionsComponent />
        <HowItWorksSection />
        <JoinComponent />
      </main>
      <FooterComponent />
    </div>
  );
};

export default MainPage;