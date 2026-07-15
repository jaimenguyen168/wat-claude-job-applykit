import ThemeToggle from "../../../components/ThemeToggle";

export default function JAKHeader() {
  return (
    <header className="page-header">
      <div className="page-logo">
        <div className="page-logo-mark">JA</div>
        <span className="page-logo-name">Job ApplyKit</span>
      </div>
      <ThemeToggle />
    </header>
  );
}
