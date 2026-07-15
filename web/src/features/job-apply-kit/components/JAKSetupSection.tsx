interface SetupStepProps {
  num: string;
  title: string;
  description: React.ReactNode;
  cmd?: string;
  rotate?: string;
  numRotate?: string;
}

function SetupStep({ num, title, description, cmd, rotate = "0deg", numRotate = "0deg" }: SetupStepProps) {
  return (
    <div className="setup-step" style={{ transform: `rotate(${rotate})` }}>
      <div className="step-num" style={{ transform: `rotate(${numRotate})` }}>{num}</div>
      <div className="step-body">
        <h3 className="step-title">{title}</h3>
        <p className="step-desc">{description}</p>
        {cmd && (
          <div className="step-cmd">
            <span className="cmd-prompt">$</span>
            <span>{cmd}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function MetaStrip() {
  const items = [
    { label: "SCHEDULE", value: "Mon–Thu, 07:00" },
    { label: "RUNTIME", value: "~4 min / run" },
    { label: "OUTPUTS", value: "2 PDFs / job + log row" },
    { label: "SCRAPER", value: "Apify · LinkedIn Jobs" },
    { label: "RENDERER", value: "Playwright · Chromium" },
    { label: "LICENSE", value: "jaimenguyen168" },
  ];
  return (
    <div className="meta-strip">
      {items.map((item) => (
        <div key={item.label} className="meta-item">
          <span className="meta-label">{item.label}</span>
          <span className="meta-value">{item.value}</span>
        </div>
      ))}
    </div>
  );
}

const mono = { fontFamily: "'IBM Plex Mono', monospace", fontSize: 13 } as const;

export default function JAKSetupSection() {
  return (
    <section className="page-section page-setup">
      <div className="section-heading">
        <h2 className="section-title">Run it yourself</h2>
        <span className="handnote">~10 minutes of setup, then it&apos;s hands-off</span>
      </div>

      <div className="setup-grid">
        <SetupStep
          num="1"
          title="Clone and install"
          description="Create a virtual environment, install Python dependencies, and install Playwright's Chromium browser for PDF rendering."
          cmd="pip install -r requirements.txt && playwright install chromium"
          rotate="-0.3deg"
          numRotate="3deg"
        />
        <SetupStep
          num="2"
          title="Configure constants"
          description={
            <>
              Add your LinkedIn search URLs (one per weekday), scoring criteria, application prompt, and Google Drive/Sheets IDs in the{" "}
              <code style={mono}>constants/</code> directory. Templates are provided.
            </>
          }
          rotate="0.3deg"
          numRotate="-3deg"
        />
        <SetupStep
          num="3"
          title="Add credentials"
          description={
            <>
              Set <code style={mono}>APIFY_TOKEN</code> in <code style={mono}>.env</code>, then place{" "}
              <code style={mono}>credentials.json</code> from Google Cloud Console in the project root to enable Drive upload and Sheets logging.
            </>
          }
          rotate="-0.3deg"
          numRotate="2deg"
        />
        <SetupStep
          num="4"
          title="Drop in your resume"
          description={
            <>
              Add a plain-text resume at <code style={mono}>.data/resume.txt</code> and your HTML templates in{" "}
              <code style={mono}>application-pack/</code>. Run the pipeline once manually, then set a Claude Code scheduled task to run it every morning.
            </>
          }
          rotate="0.3deg"
          numRotate="-2deg"
        />
      </div>

      <div style={{ marginTop: "clamp(28px, 5vw, 44px)" }}>
        <MetaStrip />
      </div>
    </section>
  );
}
