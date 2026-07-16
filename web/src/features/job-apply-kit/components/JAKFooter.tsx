interface JAKFooterProps {
  tab: "batch" | "single";
}

export default function JAKFooter({ tab }: JAKFooterProps) {
  return (
    <footer className="page-footer">
      <span>Job ApplyKit</span>
      <span className="footer-dot">·</span>
      <span>built on the WAT framework</span>
      <span className="footer-dot">·</span>
      <span>{tab === "batch" ? "9 nodes" : "8 nodes"}</span>
      <span className="footer-dot">·</span>
      <a href="https://github.com/jaimenguyen168/wat-claude-job-applykit">source &amp; docs</a>
    </footer>
  );
}
