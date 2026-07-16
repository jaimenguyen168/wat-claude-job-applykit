interface JAKHeroProps {
  tab: "batch" | "single";
}

export default function JAKHero({ tab }: JAKHeroProps) {
  const cmd = tab === "batch"
    ? ".venv/bin/python tools/scrape_linkedin_jobs.py"
    : ".venv/bin/python tools/scrape_single_job.py <url>";

  return (
    <section className="page-section page-hero">
      <div className="handnote" style={{ animation: "riseIn 0.6s ease both" }}>
        runs every morning, while you have coffee
      </div>
      <h1 className="hero-title" style={{ animation: "riseIn 0.6s 0.08s ease both" }}>
        Job ApplyKit<br />
        <span className="hero-sub">an automated job application workflow</span>
      </h1>
      <p className="hero-desc" style={{ animation: "riseIn 0.6s 0.16s ease both" }}>
        Scrapes LinkedIn job listings daily, scores them against your profile,
        and generates a tailored resume and cover letter PDF for every role
        that passes — then uploads everything to Google Drive and logs it in a
        spreadsheet.
      </p>
      <div className="hero-badges" style={{ animation: "riseIn 0.6s 0.24s ease both" }}>
        <span className="badge-dashed">Workflows</span>
        <span className="badge-dashed">Agents</span>
        <span className="badge-dashed">Tools</span>
        <span className="badge-solid">built on the WAT framework</span>
      </div>
      <div className="hero-terminal" style={{ animation: "riseIn 0.6s 0.32s ease both" }}>
        <span className="term-prompt">$</span>
        <span>{cmd}</span>
        <span className="term-caret" />
      </div>
    </section>
  );
}
