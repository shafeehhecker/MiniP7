/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Design tokens (ADR-0014): a drafting-table aesthetic, grounded in
      // where CPM scheduling comes from — construction and engineering
      // blueprints — not a generic SaaS palette. See docs/adr/0014.
      colors: {
        ink: "#14213D", // blueprint navy — chrome, nav, primary headings
        paper: "#EEF1F5", // cool blueprint paper — page background
        "paper-line": "#C7D2E0", // graph-paper grid lines
        graphite: "#1B1F27", // body text
        steel: "#5B6B85", // secondary text, muted labels
        hazard: "#E8590C", // critical path — construction safety orange
        "hazard-dim": "#FBE4D5",
        slack: "#2F9E44", // float / on-track — engineering "go" green
        "slack-dim": "#DFF3E3",
      },
      fontFamily: {
        display: ["Space Grotesk", "system-ui", "sans-serif"],
        body: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        blueprint:
          "linear-gradient(var(--paper-line) 1px, transparent 1px), linear-gradient(90deg, var(--paper-line) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "24px 24px",
      },
      borderRadius: {
        DEFAULT: "2px", // sharp, drafted corners — not a soft consumer app
      },
    },
  },
  plugins: [],
};
