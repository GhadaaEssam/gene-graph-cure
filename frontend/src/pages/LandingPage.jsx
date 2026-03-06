import React from "react";
import HeroSection from "../components/landing/HeroSection";
import ChallengeSection from "../components/landing/ChallengeSection";
import HowItWorksSection from "../components/landing/HowItWorksSection";
import ExplainabilitySection from "../components/landing/ExplainabilitySection";
import FeaturesSection from "../components/landing/FeaturesSection";
import ResearchAudienceSection from "../components/landing/ResearchAudienceSection";
import FooterSection from "../components/landing/FooterSection";


function LandingPage() {
  return (
    <>
      <HeroSection />
      <ChallengeSection />
            <HowItWorksSection />
            <ExplainabilitySection />
      <FeaturesSection />
      <ResearchAudienceSection />
      <FooterSection />

    </>
  );
}

export default LandingPage;