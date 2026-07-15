export default function Connector() {
  return (
    <svg width="24" height="52" viewBox="0 0 24 52" style={{ display: "block", margin: "0 auto", overflow: "visible" }}>
      <path d="M12 2 V40" stroke="var(--line)" strokeWidth={1.5} strokeDasharray="5 5" fill="none" style={{ animation: "dashFlow 1.4s linear infinite" }} />
      <path d="M6 39 L12 49 L18 39" stroke="var(--line)" strokeWidth={1.5} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
