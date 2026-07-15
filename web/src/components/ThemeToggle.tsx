import { useState, useEffect } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("jak-theme");
      if (saved === "light" || saved === "dark") {
        setTheme(saved);
        document.getElementById("page-root")?.setAttribute("data-theme", saved);
      }
    } catch (_) {}
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    try {
      localStorage.setItem("jak-theme", next);
    } catch (_) {}
    setTheme(next);
    document.getElementById("page-root")?.setAttribute("data-theme", next);
  };

  return (
    <button
      onClick={toggle}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        padding: "8px 14px",
        border: "1.5px solid var(--ink)",
        borderRadius: "999px",
        background: "var(--card)",
        color: "var(--ink)",
        fontFamily: "'IBM Plex Mono', monospace",
        fontSize: "12px",
        cursor: "pointer",
        boxShadow: "2px 2px 0 var(--shadow)",
        transition:
          "transform 0.15s ease, box-shadow 0.15s ease, background-color 0.35s ease, color 0.35s ease",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLButtonElement).style.transform =
          "translate(-1px, -1px)";
        (e.currentTarget as HTMLButtonElement).style.boxShadow =
          "3px 3px 0 var(--shadow)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLButtonElement).style.transform = "";
        (e.currentTarget as HTMLButtonElement).style.boxShadow =
          "2px 2px 0 var(--shadow)";
      }}
    >
      <span style={{ fontSize: "14px", lineHeight: "1" }}>
        {theme === "dark" ? "◐" : "◑"}
      </span>
      <span>{theme === "dark" ? "light" : "dark"}</span>
    </button>
  );
}
