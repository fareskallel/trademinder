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

function App() {
  const [text, setText] = useState("");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<AnalyzeResponse | null>(null);
  const [entries, setEntries] = useState<FeedbackEntry[]>([]);
  const [theme, setTheme] = useState<Theme>("light");

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

  // Optional: try to read preferred theme from localStorage
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
          pageBg: "#ffffff",
          cardOuterBg: "#f9fafb",
          cardBg: "#ffffff",
          text: "#111827",
          muted: "#4b5563",
          softer: "#6b7280",
          border: "#e5e7eb",
          accent: "#1d4ed8",
          accentMuted: "#6b7280",
          listItemBg: "#f9fafb",
        }
      : {
          pageBg: "#020617",
          cardOuterBg: "#020617",
          cardBg: "#0f172a",
          text: "#e5e7eb",
          muted: "#9ca3af",
          softer: "#6b7280",
          border: "#1f2937",
          accent: "#3b82f6",
          accentMuted: "#4b5563",
          listItemBg: "#020617",
        };

  return (
    <div
      style={{
        minHeight: "100vh",
        margin: 0,
        padding: "2rem 1rem",
        backgroundColor: colors.pageBg,
        color: colors.text,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif",
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
        {/* Header + theme toggle */}
        <header
          style={{
            marginBottom: "1.5rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "1rem",
          }}
        >
          <div>
            <h1
              style={{
                fontSize: "1.9rem",
                fontWeight: 700,
                marginBottom: "0.25rem",
              }}
            >
              TraderMind OS – Session Feedback
            </h1>
            <p
              style={{
                margin: 0,
                color: colors.muted,
                fontSize: "0.98rem",
              }}
            >
              Write about your trading session, get structured feedback, and
              build awareness of your habits over time.
            </p>
          </div>
          <button
            type="button"
            onClick={() =>
              setTheme((prev) => (prev === "light" ? "dark" : "light"))
            }
            style={{
              padding: "0.4rem 0.9rem",
              borderRadius: "999px",
              border: `1px solid ${colors.border}`,
              backgroundColor:
                theme === "light" ? "#ffffff" : "rgba(15,23,42,0.9)",
              color: colors.text,
              fontSize: "0.85rem",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            {theme === "light" ? "🌙 Dark mode" : "☀️ Light mode"}
          </button>
        </header>

        {/* Main two-column layout */}
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
                <p style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}>
                  <strong>Emotions:</strong>{" "}
                  {lastResult.emotions && lastResult.emotions.length > 0
                    ? lastResult.emotions.join(", ")
                    : "–"}
                </p>
                <p style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}>
                  <strong>Rules broken:</strong>{" "}
                  {lastResult.rules_broken &&
                  lastResult.rules_broken.length > 0
                    ? lastResult.rules_broken.join(", ")
                    : "–"}
                </p>
                <p style={{ marginBottom: "0.25rem", fontSize: "0.95rem" }}>
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
                <p style={{ color: colors.softer, fontSize: "0.95rem" }}>
                  No feedback yet. Write about your trading session on the left.
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
                        }}
                      >
                        <strong>#{entry.id}</strong>{" "}
                        <span>
                          {entry.created_at
                            ? new Date(entry.created_at).toLocaleString()
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
      </div>
    </div>
  );
}

export default App;
