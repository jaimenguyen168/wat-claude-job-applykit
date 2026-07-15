export default function BotEndMarker() {
  return (
    <div className="bot-wrap">
      <svg width="88" height="106" viewBox="0 0 80 96" style={{ overflow: "visible" }}>
        <g style={{ animation: "botBob 3.2s ease-in-out infinite" }}>
          <line x1="40" y1="18" x2="40" y2="9" stroke="var(--ink)" strokeWidth={1.5} />
          <circle cx="40" cy="6" r="3" fill="var(--accent)" stroke="var(--ink)" strokeWidth={1.5} style={{ animation: "botPulse 2s ease-in-out infinite" }} />
          <rect x="22" y="18" width="36" height="26" rx="8" fill="var(--card)" stroke="var(--ink)" strokeWidth={1.5} />
          <circle cx="34" cy="31" r="3" fill="var(--ink)" style={{ animation: "botBlink 4.5s ease-in-out infinite", transformBox: "fill-box", transformOrigin: "center" }} />
          <circle cx="46" cy="31" r="3" fill="var(--ink)" style={{ animation: "botBlink 4.5s 0.1s ease-in-out infinite", transformBox: "fill-box", transformOrigin: "center" }} />
          <path d="M36 38 Q40 41 44 38" fill="none" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
          <line x1="40" y1="44" x2="40" y2="48" stroke="var(--ink)" strokeWidth={1.5} />
          <rect x="18" y="48" width="44" height="30" rx="9" fill="var(--card)" stroke="var(--ink)" strokeWidth={1.5} />
          <circle cx="40" cy="63" r="5" fill="none" stroke="var(--ink)" strokeWidth={1.5} />
          <circle cx="40" cy="63" r="1.8" fill="var(--c-logic)" />
          <line x1="18" y1="56" x2="9" y2="65" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
          <g style={{ animation: "botWave 2.6s ease-in-out infinite", transformBox: "fill-box", transformOrigin: "0% 100%" }}>
            <line x1="62" y1="56" x2="71" y2="47" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
            <circle cx="72.5" cy="45.5" r="2.5" fill="var(--card)" stroke="var(--ink)" strokeWidth={1.5} />
          </g>
          <line x1="31" y1="78" x2="31" y2="87" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
          <line x1="49" y1="78" x2="49" y2="87" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
          <line x1="27" y1="88" x2="35" y2="88" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
          <line x1="45" y1="88" x2="53" y2="88" stroke="var(--ink)" strokeWidth={1.5} strokeLinecap="round" />
        </g>
      </svg>
      <span className="bot-label">done — check your Drive</span>
    </div>
  );
}
