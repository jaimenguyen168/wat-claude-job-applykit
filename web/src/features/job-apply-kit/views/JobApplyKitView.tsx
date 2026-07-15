import { useEffect } from "react";
import JAKHeader from "../components/JAKHeader";
import JAKHero from "../components/JAKHero";
import JAKWorkflowSection from "../components/JAKWorkflowSection";
import JAKSetupSection from "../components/JAKSetupSection";
import JAKFooter from "../components/JAKFooter";
import GearDecor from "../components/GearDecor";

export default function JobApplyKitView() {
  useEffect(() => {
    const handleScroll = () => {
      const y = window.scrollY;
      const a = document.getElementById("gear-a");
      const b = document.getElementById("gear-b");
      const c = document.getElementById("gear-c");
      if (a) a.style.transform = `rotate(${y * 0.09}deg)`;
      if (b) b.style.transform = `rotate(${-y * 0.13}deg)`;
      if (c) c.style.transform = `rotate(${y * 0.11}deg)`;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div id="page-root" data-theme="light" className="page-root">
      <GearDecor />
      <JAKHeader />
      <JAKHero />
      <JAKWorkflowSection />
      <JAKSetupSection />
      <JAKFooter />
    </div>
  );
}
