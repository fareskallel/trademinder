import { useEffect, useState } from "react";
import type { FormEvent } from "react";

const API_BASE_URL = "http://localhost:8000";

type FeedbackEntry = {
  id: number;
  text: string;
  context?: string | null;
  emotions?: string[];
  rules_broken?: string[];
  biases?: string[];
  advice?: string;
  created_at?: string;
};

type AnalyzeResponse = FeedbackEntry;
type Theme = "light" | "dark";
type ServiceKey = "home" | "session" | "journal" | "risk" | "llm";

const SERVICES: {
  key: ServiceKey;
  label: string;
  icon: string;
  description: string;
  comingSoon?: boolean;
}[] = [
  {
    key: "home",
    label: "Home",
    icon: "🏠",
    description: "Overview of your trading psychology system.",
  },
  {
    key: "session",
    label: "Session Feedback",
    icon: "🧠",
    description: "Reflect on your trading day and get structured feedback.",
  },
  {
    key: "journal",
    label: "Journal Explorer",
    icon: "📓",
    description: "Browse, search, and tag previous sessions.",
    comingSoon: true,
  },
  {
    key: "risk",
    label: "Risk Rules",
    icon: "⚖️",
    description: "Define and monitor your risk management rules.",
    comingSoon: true,
  },
  {
    key: "llm",
    label: "LLM Lab",
    icon: "🧪",
    description: "Experiment with prompts and custom AI routines.",
    comingSoon: true,
  },
];

function App() {
  const [text, setText] = useState("");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<AnalyzeResponse | null>(null);
  const [entries, setEntries] = useState<FeedbackEntry[]>([]);
  const [theme, setTheme] = useState<Theme>("light");
  const [activeService, setActiveService] = useState<ServiceKey>("home");

  // Load recent feedback entries on mount
  useEffect(() => {
    const fetchEntries = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/feedback?limit=10`);
        if (!res.ok) {
          throw new Error(`Failed to fetch feedback: ${res.status}`);
        }
        const data = await res.json();
        setEntries(data);
      } catch (err: any) {
        console.error(err);
      }
    };

    fetchEntries();
  }, []);

  // Optional: read preferred theme from localStorage
  useEffect(() => {
    const saved = window.localStorage.getItem("tm_theme") as Theme | null;
    if (saved === "light" || saved === "dark") {
      setTheme(saved);
    }
  }, []);

  // Persist theme choice
  useEffect(() => {
    window.localStorage.setItem("tm_theme", theme);
  }, [theme]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!text.trim()) {
      setError("Please write something about your trading session.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/feedback/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          context: context || null,
        }),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`API error (${res.status}): ${body}`);
      }

      const data: AnalyzeResponse = await res.json();
      setLastResult(data);

      // Prepend to entries list
      setEntries((prev) => [data, ...prev]);

      // Clear input
      setText("");
      setContext("");
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // ---- Theme palette ----
  const colors =
    theme === "light"
      ? {
          pageBg: "#f3f4f6",
          shellBg: "#ffffff",
          sidebarBg: "#ffffff",          // lighter sidebar in light mode
          sidebarBorder: "#e5e7eb",
          sidebarText: "#111827",
          sidebarMuted: "#6b7280",
          sidebarActiveBg: "#eff6ff",
          sidebarActiveBorder: "#3b82f6",
          cardOuterBg: "#f9fafb",
          cardBg: "#ffffff",
          text: "#111827",
          muted: "#4b5563",
          softer: "#6b7280",
          border: "#e5e7eb",
          accent: "#1d4ed8",
          accentMuted: "#6b7280",
          listItemBg: "#f9fafb",
          chipBg: "#e5e7eb",
        }
      : {
          pageBg: "#020617",
          shellBg: "#020617",
          sidebarBg: "#020617",          // deep dark sidebar in dark mode
          sidebarBorder: "#1f2937",
          sidebarText: "#e5e7eb",
          sidebarMuted: "#6b7280",
          sidebarActiveBg: "#0f172a",
          sidebarActiveBorder: "#3b82f6",
          cardOuterBg: "#020617",
          cardBg: "#0f172a",
          text: "#e5e7eb",
          muted: "#9ca3af",
          softer: "#6b7280",
          border: "#1f2937",
          accent: "#3b82f6",
          accentMuted: "#4b5563",
          listItemBg: "#020617",
          chipBg: "#111827",
        };

  // quick stats based on entries
  const totalEntries = entries.length;

  const uniqueDaysCount = (() => {
    const daySet = new Set<string>();
    for (const e of entries) {
      if (e.created_at) {
        const d = new Date(e.created_at);
        if (!isNaN(d.getTime())) {
          daySet.add(d.toDateString());
        }
      }
    }
    return daySet.size;
  })();

  const latestEmotion =
    lastResult?.emotions && lastResult.emotions.length > 0
      ? lastResult.emotions.join(", ")
      : "–";

  const lastEntryDateString = (() => {
    const latest = entries[0]?.created_at;
    if (!latest) return "–";
    const d = new Date(latest);
    if (isNaN(d.getTime())) return "–";
    return d.toLocaleString();
  })();

  const activeServiceLabel =
    SERVICES.find((s) => s.key === activeService)?.label ?? "";

  const activeServiceSubtitle =
    activeService === "home"
      ? "Your personal AI system for trading discipline, mindset tracking, and high-performance habits."
      : activeService === "session"
      ? "Write about your trading session, get structured feedback, and build awareness over time."
      : activeService === "journal"
      ? "Soon you’ll be able to filter, tag, and review past sessions to spot patterns in your behaviour."
      : activeService === "risk"
      ? "Design your risk rules once, and let the system remind you when you’re about to break them."
      : "A playground for prompts and future AI tools wired into your trading and journaling data.";

  return (
    <>
      {/* Micro-UX styles: hover, transitions */}
      <style>{`
        .tm-sidebar-item {
          transition: background-color 120ms ease, border-color 120ms ease, transform 80ms ease;
        }
        .tm-sidebar-item:hover {
          background-color: rgba(148, 163, 184, 0.1);
          transform: translateX(1px);
        }
        .tm-tool-card {
          transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease, background-color 120ms ease;
        }
        .tm-tool-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px -8px rgba(15, 23, 42, 0.35);
        }
        .tm-tool-card-disabled:hover {
          transform: none;
          box-shadow: none;
        }
      `}</style>

      <div
        style={{
          minHeight: "100vh",
          margin: 0,
          padding: 0,
          backgroundColor: colors.pageBg,
          color: colors.text,
          display: "flex",
          fontFamily:
            "system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif",
        }}
      >
        {/* Sidebar */}
        <aside
          style={{
            width: "260px",
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.sidebarBorder}`,
            padding: "1.5rem 1.25rem",
            display: "flex",
            flexDirection: "column",
            gap: "1.25rem",
          }}
        >
          {/* Logo / title (clickable -> Home) */}
          <div
            onClick={() => setActiveService("home")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              marginBottom: "0.2rem",
              cursor: "pointer",
              userSelect: "none",
            }}
          >
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "0.9rem",
                background:
                  "radial-gradient(circle at 10% 20%, #4f46e5 0, #22c55e 40%, #eab308 120%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.85rem",
                color: "#0b1120",
                fontWeight: 700,
              }}
            >
              TM
            </div>
            <div>
              <div
                style={{
                  fontSize: "1rem",
                  fontWeight: 700,
                  color: colors.sidebarText,
                }}
              >
                TraderMind OS
              </div>
              <div
                style={{
                  fontSize: "0.78rem",
                  color: colors.sidebarMuted,
                }}
              >
                MindTrader Control Panel
              </div>
            </div>
          </div>

          {/* Nav */}
          <nav
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "0.4rem",
              marginTop: "0.25rem",
            }}
          >
            <div
              style={{
                fontSize: "0.8rem",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: colors.sidebarMuted,
                marginBottom: "0.2rem",
              }}
            >
              Services
            </div>
            {SERVICES.map((service) => {
              const isActive = activeService === service.key;
              return (
                <button
                  key={service.key}
                  type="button"
                  onClick={() => setActiveService(service.key)}
                  title={service.description}
                  className="tm-sidebar-item"
                  style={{
                    width: "100%",
                    textAlign: "left",
                    borderRadius: "0.7rem",
                    padding: "0.55rem 0.65rem",
                    border: `1px solid ${
                      isActive ? colors.sidebarActiveBorder : "transparent"
                    }`,
                    backgroundColor: isActive
                      ? colors.sidebarActiveBg
                      : "transparent",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.55rem",
                    color: colors.sidebarText,
                    fontSize: "0.9rem",
                  }}
                >
                  <span style={{ fontSize: "1.1rem" }}>{service.icon}</span>
                  <span style={{ flex: 1, fontWeight: 500 }}>
                    {service.label}
                  </span>
                  {service.comingSoon && (
                    <span
                      style={{
                        fontSize: "0.65rem",
                        padding: "0.1rem 0.35rem",
                        borderRadius: "999px",
                        border: `1px solid ${colors.sidebarMuted}`,
                        color: colors.sidebarMuted,
                      }}
                    >
                      soon
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Spacer */}
          <div style={{ flex: 1 }} />

          {/* Theme toggle */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "0.4rem",
              borderTop: `1px solid ${colors.sidebarBorder}`,
              paddingTop: "0.8rem",
            }}
          >
            <button
              type="button"
              onClick={() =>
                setTheme((prev) => (prev === "light" ? "dark" : "light"))
              }
              style={{
                padding: "0.4rem 0.9rem",
                borderRadius: "999px",
                border: `1px solid ${colors.sidebarBorder}`,
                backgroundColor: colors.sidebarBg,   // << THE FIX
                color: colors.sidebarText,           // << ALWAYS CORRECT
                fontSize: "0.8rem",
                fontWeight: 500,
                cursor: "pointer",
                alignSelf: "flex-start",
              }}
            >
              {theme === "light" ? "🌙 Dark mode" : "☀️ Light mode"}
            </button>
            <div
              style={{
                fontSize: "0.7rem",
                color: colors.sidebarMuted,
              }}
            >
              v0.2 — local dev
            </div>
          </div>
        </aside>

        {/* Main app shell */}
        <main
          style={{
            flex: 1,
            padding: "1.75rem 1.75rem",
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-start",
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: "1100px",
              backgroundColor: colors.cardOuterBg,
              borderRadius: "1rem",
              boxShadow:
                theme === "light"
                  ? "0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.03)"
                  : "0 20px 25px -5px rgba(15,23,42,0.7), 0 10px 10px -5px rgba(15,23,42,0.9)",
              padding: "1.75rem",
              border: `1px solid ${colors.border}`,
            }}
          >
            {/* Top header */}
            <header
              style={{
                marginBottom: "1.5rem",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: "1rem",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: "0.8rem",
                    letterSpacing: "0.09em",
                    textTransform: "uppercase",
                    color: colors.softer,
                    marginBottom: "0.1rem",
                  }}
                >
                  {activeServiceLabel}
                </div>
                <h1
                  style={{
                    fontSize: "1.8rem",
                    fontWeight: 700,
                    marginBottom: "0.25rem",
                  }}
                >
                  {activeService === "home"
                    ? "Your personal trading discipline OS"
                    : activeService === "session"
                    ? "Session feedback & mindset analysis"
                    : activeService === "journal"
                    ? "Browse your trading journal"
                    : activeService === "risk"
                    ? "Risk rule control center"
                    : "LLM lab for custom tools"}
                </h1>
                <p
                  style={{
                    margin: 0,
                    color: colors.muted,
                    fontSize: "0.96rem",
                    maxWidth: "40rem",
                  }}
                >
                  {activeServiceSubtitle}
                </p>
              </div>

              {/* Quick stats chips */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.35rem",
                  minWidth: "185px",
                }}
              >
                <div
                  style={{
                    alignSelf: "flex-end",
                    fontSize: "0.76rem",
                    color: colors.softer,
                  }}
                >
                  MindTrader snapshot
                </div>
                <div
                  style={{
                    display: "flex",
                    gap: "0.4rem",
                    justifyContent: "flex-end",
                    flexWrap: "wrap",
                  }}
                >
                  <div
                    style={{
                      borderRadius: "999px",
                      padding: "0.25rem 0.6rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.chipBg,
                      fontSize: "0.78rem",
                    }}
                  >
                    📝 Entries:{" "}
                    <span style={{ fontWeight: 600 }}>{totalEntries}</span>
                  </div>
                  <div
                    style={{
                      borderRadius: "999px",
                      padding: "0.25rem 0.6rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.chipBg,
                      fontSize: "0.78rem",
                      maxWidth: "180px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    💭 Latest emotion:{" "}
                    <span style={{ fontWeight: 500 }}>{latestEmotion}</span>
                  </div>
                </div>
              </div>
            </header>

            {/* Service content */}
            {activeService === "home" ? (
              // ---- HOME DASHBOARD ----
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1.75rem",
                }}
              >
                {/* Stats row */}
                <section
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "1rem",
                  }}
                >
                  <div
                    style={{
                      padding: "1rem",
                      borderRadius: "0.9rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.cardBg,
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.softer,
                        marginBottom: "0.25rem",
                      }}
                    >
                      Entries logged
                    </div>
                    <div
                      style={{
                        fontSize: "1.4rem",
                        fontWeight: 600,
                      }}
                    >
                      {totalEntries}
                    </div>
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.muted,
                        marginTop: "0.2rem",
                      }}
                    >
                      {totalEntries === 0
                        ? "No entries yet. Start with your first session today."
                        : "Moments of reflection captured."}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: "1rem",
                      borderRadius: "0.9rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.cardBg,
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.softer,
                        marginBottom: "0.25rem",
                      }}
                    >
                      Journal days
                    </div>
                    <div
                      style={{
                        fontSize: "1.4rem",
                        fontWeight: 600,
                      }}
                    >
                      {uniqueDaysCount}
                    </div>
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.muted,
                        marginTop: "0.2rem",
                      }}
                    >
                      {uniqueDaysCount === 0
                        ? "Once you log, we’ll show how many days you’ve shown up."
                        : "Unique days you showed up and wrote."}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: "1rem",
                      borderRadius: "0.9rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.cardBg,
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.softer,
                        marginBottom: "0.25rem",
                      }}
                    >
                      Last session snapshot
                    </div>
                    <div
                      style={{
                        fontSize: "0.9rem",
                        marginBottom: "0.25rem",
                      }}
                    >
                      <span style={{ color: colors.softer }}>Emotion:</span>{" "}
                      <span style={{ fontWeight: 500 }}>{latestEmotion}</span>
                    </div>
                    <div
                      style={{
                        fontSize: "0.8rem",
                        color: colors.muted,
                      }}
                    >
                      Last entry:{" "}
                      {lastEntryDateString === "–"
                        ? "No sessions logged yet."
                        : lastEntryDateString}
                    </div>
                  </div>
                </section>

                {/* Tools section */}
                <section
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.9rem",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      gap: "0.5rem",
                    }}
                  >
                    <h2
                      style={{
                        fontSize: "1.1rem",
                        fontWeight: 600,
                        margin: 0,
                      }}
                    >
                      Your tools
                    </h2>
                    <div
                      style={{
                        fontSize: "0.85rem",
                        color: colors.softer,
                      }}
                    >
                      Start with session feedback to log today&apos;s trading.
                    </div>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(220px, 1fr))",
                      gap: "1rem",
                    }}
                  >
                    {SERVICES.filter((s) => s.key !== "home").map((service) => {
                      const isDisabled = service.comingSoon;
                      const isPrimary = service.key === "session";
                      const isCurrent = activeService === service.key;

                      return (
                        <button
                          key={service.key}
                          type="button"
                          onClick={() => {
                            if (!isDisabled) {
                              setActiveService(service.key);
                            }
                          }}
                          className={
                            "tm-tool-card" +
                            (isDisabled ? " tm-tool-card-disabled" : "")
                          }
                          style={{
                            textAlign: "left",
                            padding: "1rem",
                            borderRadius: "0.9rem",
                            border: `1px solid ${
                              isCurrent ? colors.accent : colors.border
                            }`,
                            backgroundColor: isCurrent
                              ? theme === "light"
                                ? "#eff6ff"
                                : "#0b1120"
                              : colors.cardBg,
                            cursor: isDisabled ? "default" : "pointer",
                            display: "flex",
                            flexDirection: "column",
                            gap: "0.45rem",
                            opacity: isDisabled ? 0.7 : 1,
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "space-between",
                              gap: "0.75rem",
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.5rem",
                              }}
                            >
                              <span
                                style={{
                                  fontSize: "1.2rem",
                                }}
                              >
                                {service.icon}
                              </span>
                              <span
                                style={{
                                  fontWeight: 600,
                                  fontSize: "0.98rem",
                                  color: colors.text,
                                }}
                              >
                                {service.label}
                              </span>
                            </div>
                            {!isDisabled && (
                              <span
                                style={{
                                  fontSize: "0.7rem",
                                  padding: "0.1rem 0.45rem",
                                  borderRadius: "999px",
                                  border: `1px solid ${colors.border}`,
                                  color: colors.text,
                                  backgroundColor:
                                    theme === "light"
                                      ? "#ffffff"
                                      : "#0f172a",
                                }}
                              >
                                {isCurrent
                                  ? "Active"
                                  : isPrimary
                                  ? "Recommended"
                                  : ""}
                              </span>
                            )}
                          </div>
                          <p
                            style={{
                              margin: 0,
                              fontSize: "0.9rem",
                              color: colors.muted,
                            }}
                          >
                            {service.description}
                          </p>
                          <div
                            style={{
                              marginTop: "0.2rem",
                              fontSize: "0.85rem",
                              color: isDisabled
                                ? colors.softer
                                : colors.accent,
                            }}
                          >
                            {isDisabled ? "Coming soon" : "Open →"}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </section>
              </div>
            ) : activeService === "session" ? (
              // ---- SESSION FEEDBACK ----
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(0, 3fr) minmax(0, 2.5fr)",
                  gap: "1.5rem",
                }}
              >
                {/* Left side: form + latest analysis */}
                <div>
                  {/* Form card */}
                  <section
                    style={{
                      marginBottom: "1.5rem",
                      padding: "1rem",
                      borderRadius: "0.75rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.cardBg,
                    }}
                  >
                    <h2
                      style={{
                        fontSize: "1.1rem",
                        fontWeight: 600,
                        marginBottom: "0.75rem",
                      }}
                    >
                      New session feedback
                    </h2>
                    <form onSubmit={handleSubmit}>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "0.35rem",
                          fontWeight: 600,
                          fontSize: "0.95rem",
                        }}
                      >
                        What happened this session?
                      </label>
                      <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows={5}
                        style={{
                          width: "100%",
                          padding: "0.75rem",
                          borderRadius: "0.5rem",
                          border: `1px solid ${colors.border}`,
                          marginBottom: "0.75rem",
                          resize: "vertical",
                          fontSize: "0.95rem",
                          color: colors.text,
                          backgroundColor:
                            theme === "light" ? "#f9fafb" : "#020617",
                        }}
                        placeholder="Example: I overtraded after a loss on gold. I felt frustrated and kept taking impulsive entries..."
                      />

                      <label
                        style={{
                          display: "block",
                          marginBottom: "0.25rem",
                          fontWeight: 600,
                          fontSize: "0.95rem",
                        }}
                      >
                        Context (optional)
                      </label>
                      <input
                        type="text"
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.5rem",
                          border: `1px solid ${colors.border}`,
                          marginBottom: "0.6rem",
                          fontSize: "0.95rem",
                          color: colors.text,
                          backgroundColor:
                            theme === "light" ? "#ffffff" : "#020617",
                        }}
                        placeholder="Example: FTMO 100k, gold scalping, London session"
                      />

                      {error && (
                        <div
                          style={{
                            marginTop: "0.25rem",
                            marginBottom: "0.75rem",
                            color: "#fca5a5",
                            fontSize: "0.9rem",
                          }}
                        >
                          {error}
                        </div>
                      )}

                      <button
                        type="submit"
                        disabled={loading}
                        style={{
                          padding: "0.6rem 1.4rem",
                          borderRadius: "999px",
                          border: "none",
                          backgroundColor: loading
                            ? colors.accentMuted
                            : colors.accent,
                          color: "white",
                          fontWeight: 600,
                          fontSize: "0.95rem",
                          cursor: loading ? "default" : "pointer",
                          boxShadow:
                            theme === "light"
                              ? "0 10px 15px -3px rgba(37, 99, 235, 0.4), 0 4px 6px -4px rgba(37, 99, 235, 0.3)"
                              : "0 10px 15px -3px rgba(15,23,42,0.7), 0 4px 6px -4px rgba(15,23,42,0.9)",
                        }}
                      >
                        {loading ? "Analyzing..." : "Analyze & Save"}
                      </button>
                    </form>
                  </section>

                  {/* Latest analysis card */}
                  {lastResult && (
                    <section
                      style={{
                        padding: "1rem",
                        borderRadius: "0.75rem",
                        border: `1px solid ${colors.border}`,
                        backgroundColor: colors.cardBg,
                      }}
                    >
                      <h2
                        style={{
                          fontSize: "1.1rem",
                          fontWeight: 600,
                          marginBottom: "0.75rem",
                        }}
                      >
                        Latest feedback analysis
                      </h2>
                      <p
                        style={{
                          marginBottom: "0.35rem",
                          fontSize: "0.95rem",
                          color: colors.text,
                        }}
                      >
                        <strong>Entry:</strong> {lastResult.text}
                      </p>
                      {lastResult.context && (
                        <p
                          style={{
                            marginBottom: "0.35rem",
                            fontSize: "0.9rem",
                            color: colors.muted,
                          }}
                        >
                          <strong>Context:</strong> {lastResult.context}
                        </p>
                      )}
                      <p
                        style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}
                      >
                        <strong>Emotions:</strong>{" "}
                        {lastResult.emotions && lastResult.emotions.length > 0
                          ? lastResult.emotions.join(", ")
                          : "–"}
                      </p>
                      <p
                        style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}
                      >
                        <strong>Rules broken:</strong>{" "}
                        {lastResult.rules_broken &&
                        lastResult.rules_broken.length > 0
                          ? lastResult.rules_broken.join(", ")
                          : "–"}
                      </p>
                      <p
                        style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}
                      >
                        <strong>Biases:</strong>{" "}
                        {lastResult.biases && lastResult.biases.length > 0
                          ? lastResult.biases.join(", ")
                          : "–"}
                      </p>
                      <p
                        style={{
                          marginTop: "0.5rem",
                          fontSize: "0.95rem",
                          color: colors.text,
                        }}
                      >
                        <strong>Advice:</strong> {lastResult.advice || "–"}
                      </p>
                    </section>
                  )}
                </div>

                {/* Right side: recent feedback entries */}
                <div>
                  <section
                    style={{
                      padding: "1rem",
                      borderRadius: "0.75rem",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.cardBg,
                      maxHeight: "540px",
                      overflowY: "auto",
                    }}
                  >
                    <h2
                      style={{
                        fontSize: "1.1rem",
                        fontWeight: 600,
                        marginBottom: "0.75rem",
                      }}
                    >
                      Recent feedback
                    </h2>
                    {entries.length === 0 ? (
                      <p
                        style={{ color: colors.softer, fontSize: "0.95rem" }}
                      >
                        No feedback yet. Write about your trading session on the
                        left.
                      </p>
                    ) : (
                      <ul
                        style={{
                          listStyle: "none",
                          padding: 0,
                          margin: 0,
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.75rem",
                        }}
                      >
                        {entries.map((entry) => (
                          <li
                            key={entry.id}
                            style={{
                              padding: "0.75rem",
                              borderRadius: "0.6rem",
                              border: `1px solid ${colors.border}`,
                              backgroundColor: colors.listItemBg,
                            }}
                          >
                            <p
                              style={{
                                marginBottom: "0.25rem",
                                fontSize: "0.9rem",
                                color: colors.muted,
                                display: "flex",
                                justifyContent: "space-between",
                                gap: "0.5rem",
                              }}
                            >
                              <span>
                                <strong>#{entry.id}</strong>
                              </span>
                              <span>
                                {entry.created_at
                                  ? new Date(
                                      entry.created_at
                                    ).toLocaleString()
                                  : ""}
                              </span>
                            </p>
                            {entry.context && (
                              <p
                                style={{
                                  marginBottom: "0.25rem",
                                  fontSize: "0.85rem",
                                  color: colors.softer,
                                }}
                              >
                                <strong>Context:</strong> {entry.context}
                              </p>
                            )}
                            <p
                              style={{
                                marginBottom: "0.3rem",
                                fontSize: "0.95rem",
                                color: colors.text,
                              }}
                            >
                              {entry.text}
                            </p>
                            {entry.emotions && entry.emotions.length > 0 && (
                              <p
                                style={{
                                  marginBottom: 0,
                                  fontSize: "0.85rem",
                                  color: colors.muted,
                                }}
                              >
                                <strong>Emotions:</strong>{" "}
                                {entry.emotions.join(", ")}
                              </p>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                </div>
              </div>
            ) : (
              // ---- PLACEHOLDERS FOR FUTURE SERVICES ----
              <section
                style={{
                  padding: "1.25rem",
                  borderRadius: "0.9rem",
                  border: `1px dashed ${colors.border}`,
                  backgroundColor: colors.cardBg,
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                  alignItems: "flex-start",
                }}
              >
                <div
                  style={{
                    fontSize: "1.05rem",
                    fontWeight: 600,
                    marginBottom: "0.1rem",
                  }}
                >
                  Coming soon to MindTrader
                </div>
                <p
                  style={{
                    margin: 0,
                    fontSize: "0.95rem",
                    color: colors.muted,
                    maxWidth: "36rem",
                  }}
                >
                  This section will be wired into the same backend services you
                  already have — we&apos;ll plug in the{" "}
                  {activeService === "journal"
                    ? "journal explorer and filtering"
                    : activeService === "risk"
                    ? "risk rule configuration and real-time checks"
                    : "LLM orchestration layer for experiments and tools."}
                </p>
                <ul
                  style={{
                    margin: "0.4rem 0 0",
                    paddingLeft: "1.1rem",
                    fontSize: "0.9rem",
                    color: colors.softer,
                  }}
                >
                  <li>Define what endpoints / services this view should call</li>
                  <li>Design the data model (e.g. rules, tags, prompts)</li>
                  <li>Iterate on UI once backend is ready</li>
                </ul>
              </section>
            )}
          </div>
        </main>
      </div>
    </>
  );
}

export default App;
