const GEAR_PATH =
  "M26.87 10.25 L25.78 3.33 A27 27 0 0 1 34.22 3.33 L33.13 10.25 A20 20 0 0 1 41.76 13.82 L45.87 8.16 A27 27 0 0 1 51.84 14.13 L46.18 18.24 A20 20 0 0 1 49.75 26.87 L56.67 25.78 A27 27 0 0 1 56.67 34.22 L49.75 33.13 A20 20 0 0 1 46.18 41.76 L51.84 45.87 A27 27 0 0 1 45.87 51.84 L41.76 46.18 A20 20 0 0 1 33.13 49.75 L34.22 56.67 A27 27 0 0 1 25.78 56.67 L26.87 49.75 A20 20 0 0 1 18.24 46.18 L14.13 51.84 A27 27 0 0 1 8.16 45.87 L13.82 41.76 A20 20 0 0 1 10.25 33.13 L3.33 34.22 A27 27 0 0 1 3.33 25.78 L10.25 26.87 A20 20 0 0 1 13.82 18.24 L8.16 14.13 A27 27 0 0 1 14.13 8.16 L18.24 13.82 A20 20 0 0 1 26.87 10.25 Z";
const INNER_PATH = "M40.83 28.09 A11 11 0 1 1 26.24 19.66";

function Gear({ id, size, pos }: { id: string; size: number; pos: React.CSSProperties }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 60 60"
      style={{ position: "absolute", pointerEvents: "none", overflow: "visible", ...pos }}
      aria-hidden="true"
    >
      <g id={id} style={{ transformOrigin: "30px 30px" }}>
        <path d={GEAR_PATH} fill="none" stroke="var(--ink)" strokeWidth={1.8} strokeLinejoin="round" />
        <path d={INNER_PATH} fill="none" stroke="var(--ink)" strokeWidth={1.8} strokeLinecap="round" />
      </g>
    </svg>
  );
}

export default function GearDecor() {
  return (
    <>
      <Gear id="gear-a" size={340} pos={{ top: 90, right: -110, opacity: 0.16 }} />
      <Gear id="gear-b" size={260} pos={{ top: 780, left: -90, opacity: 0.14 }} />
      <Gear id="gear-c" size={220} pos={{ bottom: 380, right: -70, opacity: 0.14 }} />
    </>
  );
}
