import React from "react";
import Connector from "./Connector";
import BotEndMarker from "./BotEndMarker";

const BADGE_COLORS: Record<string, string> = {
  TRIGGER: "var(--c-trigger)",
  TOOL: "var(--c-tool)",
  LLM: "var(--c-llm)",
  LOGIC: "var(--c-logic)",
};

interface WorkflowCardProps {
  badge: "TRIGGER" | "TOOL" | "LLM" | "LOGIC";
  num: string;
  title: string;
  description: React.ReactNode;
  cmd?: string;
  rotate?: string;
  dashed?: boolean;
}

function WorkflowCard({ badge, num, title, description, cmd, rotate = "0deg", dashed = false }: WorkflowCardProps) {
  const border = dashed ? "1.5px dashed var(--ink)" : "1.5px solid var(--ink)";
  return (
    <div className="workflow-card" style={{ transform: `rotate(${rotate})`, border }}>
      <div className="card-header">
        <span className="card-badge" style={{ background: BADGE_COLORS[badge] }}>{badge}</span>
        <span className="node-num">{num}</span>
      </div>
      <h3 className="card-title">{title}</h3>
      <p className="card-desc">{description}</p>
      {cmd && (
        <div className="card-cmd">
          <span className="cmd-prompt">$</span>
          <span>{cmd}</span>
        </div>
      )}
    </div>
  );
}

const NODES: WorkflowCardProps[] = [
  {
    badge: "TRIGGER",
    num: "01",
    title: "Daily Schedule",
    description: "Fires Mon–Thu at 07:00. Rotates LinkedIn search URL by day of week so you hit different roles across the week.",
    rotate: "-0.4deg",
  },
  {
    badge: "TOOL",
    num: "02",
    title: "LinkedIn Scraper",
    description: (
      <>
        Fetches up to 50 fresh job listings via the Apify{" "}
        <code style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 13 }}>curious_coder/linkedin-jobs-scraper</code>{" "}
        actor. Returns structured JSON — title, company, location, description, salary, URL.
      </>
    ),
    cmd: ".venv/bin/python tools/scrape_linkedin_jobs.py",
    rotate: "0.4deg",
  },
  {
    badge: "TOOL",
    num: "03",
    title: "Filter & Dedup",
    description: (
      <>
        Drops any listing whose ID already appears in{" "}
        <code style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 13 }}>seen_ids.json</code>.
        {" "}Marks the new ones as seen so future runs skip them automatically.
      </>
    ),
    cmd: ".venv/bin/python tools/filter_new_jobs.py",
    rotate: "-0.3deg",
  },
  {
    badge: "TOOL",
    num: "04",
    title: "Profile Extractor",
    description: (
      <>
        Reads{" "}
        <code style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 13 }}>.data/resume.txt</code>
        {" "}and optionally scrapes your portfolio URL, then outputs a structured JSON profile the scoring agent uses as its reference.
      </>
    ),
    cmd: ".venv/bin/python tools/extract_candidate_profile.py",
    rotate: "0.3deg",
  },
  {
    badge: "LLM",
    num: "05",
    title: "Job Scorer",
    description: "Claude evaluates each job against your profile using your custom scoring prompt. Returns a 0–100 score, a verdict (pass / skip / maybe), and a one-line reason for each listing.",
    cmd: ".venv/bin/python tools/score_jobs.py",
    rotate: "-0.4deg",
  },
  {
    badge: "LOGIC",
    num: "06",
    title: "Score Gate",
    description: "Jobs at or above your configured threshold continue to document generation. Everything below is logged as skipped — score and reason preserved for review.",
    rotate: "0.4deg",
    dashed: true,
  },
  {
    badge: "LLM",
    num: "07",
    title: "Application Pack Generator",
    description: "For each passing job, Claude tailors your resume and writes a targeted cover letter — both output as clean HTML files, grounded in your real experience and the specific role.",
    cmd: ".venv/bin/python tools/prepare_application_pack.py",
    rotate: "-0.3deg",
  },
  {
    badge: "TOOL",
    num: "08",
    title: "PDF Renderer",
    description: "Playwright headless Chromium renders each HTML file to a selectable, ATS-safe PDF with embedded IBM Plex fonts. One resume PDF and one cover letter PDF per job.",
    cmd: ".venv/bin/python tools/render_pdf.py",
    rotate: "0.3deg",
  },
  {
    badge: "TOOL",
    num: "09",
    title: "Drive & Sheets",
    description: "Uploads both PDFs to Google Drive under a folder named for the company. Appends one row to your tracking spreadsheet: title, company, score, salary, location, and direct PDF links.",
    cmd: ".venv/bin/python tools/upload_and_log.py",
    rotate: "-0.4deg",
  },
];

const GEAR_PATH =
  "M26.87 10.25 L25.78 3.33 A27 27 0 0 1 34.22 3.33 L33.13 10.25 A20 20 0 0 1 41.76 13.82 L45.87 8.16 A27 27 0 0 1 51.84 14.13 L46.18 18.24 A20 20 0 0 1 49.75 26.87 L56.67 25.78 A27 27 0 0 1 56.67 34.22 L49.75 33.13 A20 20 0 0 1 46.18 41.76 L51.84 45.87 A27 27 0 0 1 45.87 51.84 L41.76 46.18 A20 20 0 0 1 33.13 49.75 L34.22 56.67 A27 27 0 0 1 25.78 56.67 L26.87 49.75 A20 20 0 0 1 18.24 46.18 L14.13 51.84 A27 27 0 0 1 8.16 45.87 L13.82 41.76 A20 20 0 0 1 10.25 33.13 L3.33 34.22 A27 27 0 0 1 3.33 25.78 L10.25 26.87 A20 20 0 0 1 13.82 18.24 L8.16 14.13 A27 27 0 0 1 14.13 8.16 L18.24 13.82 A20 20 0 0 1 26.87 10.25 Z";
const INNER_PATH = "M40.83 28.09 A11 11 0 1 1 26.24 19.66";

export default function JAKWorkflowSection() {
  return (
    <section className="page-section">
      <div className="section-heading">
        <svg width="72" height="52" viewBox="0 0 96 68" style={{ alignSelf: "center", overflow: "visible" }}>
          <g transform="scale(0.87)">
            <g style={{ animation: "spinCW 14s linear infinite", transformOrigin: "30px 30px" }}>
              <path d={GEAR_PATH} fill="var(--card)" stroke="var(--ink)" strokeWidth={3.2} strokeLinejoin="round" />
              <path d={INNER_PATH} fill="none" stroke="var(--ink)" strokeWidth={3.2} strokeLinecap="round" />
            </g>
          </g>
          <g transform="translate(52, 30) scale(0.55)">
            <g style={{ animation: "spinCCW 9s linear infinite", transformOrigin: "30px 30px" }}>
              <path d={GEAR_PATH} fill="var(--card)" stroke="var(--ink)" strokeWidth={4.2} strokeLinejoin="round" />
              <path d={INNER_PATH} fill="none" stroke="var(--ink)" strokeWidth={4.2} strokeLinecap="round" />
            </g>
          </g>
        </svg>
        <h2 className="section-title">The workflow</h2>
        <span className="handnote">9 nodes, fully linear, zero clicks</span>
      </div>

      <div className="flow">
        {NODES.map((node, i) => (
          <React.Fragment key={node.num}>
            <WorkflowCard {...node} />
            {i < NODES.length - 1 && <Connector />}
          </React.Fragment>
        ))}
        <BotEndMarker />
      </div>
    </section>
  );
}
