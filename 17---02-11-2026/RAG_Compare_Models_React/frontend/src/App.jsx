import { useEffect, useState } from "react";

const modelDescriptions = {
  "gpt-4o-mini": "Fast and cost-efficient",
  "gpt-4.1-mini": "Balanced speed and quality",
  "gpt-4.1": "Detailed reasoning",
  "gpt-4o": "General-purpose multimodal",
};

async function apiRequest(path, options) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || "The request failed.");
  }
  return body;
}

function formatSeconds(seconds) {
  return `${Number(seconds).toFixed(2)}s`;
}

function App() {
  const [models, setModels] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [question, setQuestion] = useState("");
  const [results, setResults] = useState([]);
  const [retrievedChunks, setRetrievedChunks] = useState([]);
  const [bestDistance, setBestDistance] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [feedbackBusy, setFeedbackBusy] = useState("");

  useEffect(() => {
    Promise.all([apiRequest("/api/models"), apiRequest("/api/metrics")])
      .then(([{ models: available }, { models: savedMetrics }]) => {
        setModels(available);
        setSelectedModels(available.slice(0, 2));
        setMetrics(savedMetrics);
      })
      .catch((requestError) => setError(requestError.message));
  }, []);

  const ratedResults = results.filter(
    (result) => result.feedback === "Correct" || result.feedback === "Incorrect",
  );
  const accuracy = ratedResults.length
    ? Math.round(
        (ratedResults.filter((result) => result.feedback === "Correct").length /
          ratedResults.length) *
          100,
      )
    : null;
  const successfulResults = results.filter((result) => !result.error);
  const averageTime = successfulResults.length
    ? successfulResults.reduce((total, result) => total + result.total_seconds, 0) /
      successfulResults.length
    : null;
  const currentRunByModel = new Map(
    successfulResults.map((result) => [result.model, result]),
  );
  const timeComparison = metrics.map((item) => {
    const currentRun = currentRunByModel.get(item.model);
    return {
      model: item.model,
      value: currentRun?.total_seconds ?? item.average_total_seconds,
      detail: currentRun
        ? "Latest run"
        : `${item.run_count} saved ${item.run_count === 1 ? "run" : "runs"}`,
    };
  });

  function toggleModel(model) {
    setSelectedModels((current) =>
      current.includes(model)
        ? current.filter((item) => item !== model)
        : [...current, model],
    );
  }

  async function submitQuestion(event) {
    event.preventDefault();
    if (!question.trim() || !selectedModels.length || busy) return;

    setBusy(true);
    setError("");
    setResults([]);
    setRetrievedChunks([]);
    setBestDistance(null);
    try {
      const response = await apiRequest("/api/ask", {
        method: "POST",
        body: JSON.stringify({
          question: question.trim(),
          models: selectedModels,
        }),
      });
      setResults(response.results.map((result) => ({ ...result, feedback: "Not rated" })));
      setRetrievedChunks(response.retrieved_chunks);
      setBestDistance(response.best_distance);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function rateAnswer(result, feedback) {
    const key = result.model;
    setFeedbackBusy(key);
    setError("");
    try {
      const response = await apiRequest("/api/feedback", {
        method: "POST",
        body: JSON.stringify({
          model: result.model,
          question: question.trim(),
          answer: result.answer,
          retrieved_chunk_ids: retrievedChunks.map((chunk) => chunk.id),
          best_distance: bestDistance ?? 0,
          total_seconds: result.total_seconds,
          feedback,
        }),
      });
      setResults((current) =>
        current.map((item) =>
          item.model === key ? { ...item, feedback: response.feedback } : item,
        ),
      );
      const updatedMetrics = await apiRequest("/api/metrics");
      setMetrics(updatedMetrics.models);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setFeedbackBusy("");
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="RAG Model Studio home">
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          <span>RAG Model Studio</span>
        </a>
        <span className="local-badge">
          <span className="status-dot" />
          Local workspace
        </span>
      </header>

      <section className="intro">
        <p className="eyebrow">RETRIEVAL AUGMENTED GENERATION</p>
        <h1>Compare answers, side by side.</h1>
        <p className="intro-copy">
          Ask your indexed document a question and see how different models respond
          using the same retrieved context.
        </p>
      </section>

      <section className="workspace">
        <form className="question-panel panel" onSubmit={submitQuestion}>
          <div className="section-heading">
            <div>
              <span className="step-number">01</span>
              <h2>Choose models</h2>
            </div>
            <span className="selection-count">
              {selectedModels.length} selected
            </span>
          </div>

          <div className="model-grid">
            {models.map((model, index) => {
              const selected = selectedModels.includes(model);
              return (
                <button
                  className={`model-option${selected ? " selected" : ""}`}
                  type="button"
                  key={model}
                  aria-pressed={selected}
                  onClick={() => toggleModel(model)}
                >
                  <span className="model-icon">{model.startsWith("gpt-4o") ? "✳" : "◇"}</span>
                  <span className="model-copy">
                    <strong>{model}</strong>
                    <small>{modelDescriptions[model] || "Available model"}</small>
                  </span>
                  <span className="check-mark">{selected ? "✓" : index + 1}</span>
                </button>
              );
            })}
            {!models.length && (
              <p className="empty-models">Connecting to the local API…</p>
            )}
          </div>

          <label className="question-label" htmlFor="question">
            <span className="step-number">02</span>
            Your question
          </label>
          <div className="question-input-wrap">
            <textarea
              id="question"
              rows="3"
              maxLength="2000"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about your indexed documents…"
            />
            <span className="character-count">{question.length}/2000</span>
          </div>
          <div className="form-footer">
            <span className="hint">Answers are grounded in your retrieved chunks.</span>
            <button
              className="submit-button"
              type="submit"
              disabled={busy || !question.trim() || selectedModels.length === 0}
            >
              {busy ? (
                <>
                  <span className="spinner" /> Generating…
                </>
              ) : (
                <>
                  Generate answers <span aria-hidden="true">→</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-banner" role="alert">
            <span aria-hidden="true">!</span>
            <div>
              <strong>Something needs attention</strong>
              <p>{error}</p>
              {error.toLowerCase().includes("indexed collection") && (
                <p>Run <code>python 05_store_in_chroma.py</code>, then try again.</p>
              )}
            </div>
          </div>
        )}

        <section className="performance-section" aria-labelledby="performance-title">
          <div className="section-heading results-heading">
            <div>
              <span className="step-number">03</span>
              <div>
                <h2 id="performance-title">Model performance</h2>
                <p className="section-subtitle">
                  Compare saved answer ratings and response time across models.
                </p>
              </div>
            </div>
            <span className="selection-count">All tracked models</span>
          </div>

          <div className="comparison-charts">
            <ComparisonChart
              title="Answer accuracy"
              description="Correct ratings ÷ all rated answers"
              rows={metrics.map((item) => ({
                model: item.model,
                value: item.accuracy,
                detail: `${item.rated_count} ${item.rated_count === 1 ? "rating" : "ratings"}`,
              }))}
              suffix="%"
              scale={100}
              tone="accuracy"
              emptyMessage="Rate answers Correct or Incorrect to compare accuracy."
            />
            <ComparisonChart
              title="Response time"
              description={
                results.length
                  ? "Latest run where available; otherwise saved average"
                  : "Average end-to-end time from saved runs"
              }
              rows={timeComparison}
              suffix="s"
              tone="timing"
              emptyMessage="Run a question to compare response times."
            />
          </div>

          <div className="model-metrics-heading">
            <h3>Model-by-model metrics</h3>
            <span>Accuracy uses your feedback · time includes retrieval + generation</span>
          </div>
          <div className="model-metrics-grid">
            {metrics.map((item) => {
              const currentRun = currentRunByModel.get(item.model);
              return (
                <article className="model-metric-card panel" key={item.model}>
                  <div className="model-metric-head">
                    <span className="model-icon">
                      {item.model.startsWith("gpt-4o") ? "✳" : "◇"}
                    </span>
                    <div className="model-metric-name">
                      <h3>{item.model}</h3>
                      <span>
                        {modelDescriptions[item.model] || "Configured model"}
                      </span>
                    </div>
                    {item.rated_count > 0 && (
                      <span className="rating-sample">
                        {item.rated_count} rated
                      </span>
                    )}
                  </div>
                  <div className="model-metric-values">
                    <div className="model-metric-value">
                      <span>ACCURACY</span>
                      <strong>
                        {item.accuracy === null ? "—" : `${item.accuracy}%`}
                      </strong>
                      <small>
                        {item.rated_count
                          ? `${item.correct_count}/${item.rated_count} correct`
                          : "No ratings yet"}
                      </small>
                    </div>
                    <div className="model-metric-value">
                      <span>
                        {currentRun ? "LATEST TIME" : "AVG. RESPONSE TIME"}
                      </span>
                      <strong>
                        {currentRun
                          ? formatSeconds(currentRun.total_seconds)
                          : item.average_total_seconds === null
                            ? "—"
                            : formatSeconds(item.average_total_seconds)}
                      </strong>
                      <small>
                        {currentRun
                          ? "Current question"
                          : `${item.run_count} saved ${
                              item.run_count === 1 ? "run" : "runs"
                            }`}
                      </small>
                    </div>
                    <div className="model-metric-value">
                      <span>BEST DISTANCE</span>
                      <strong>
                        {item.best_distance === null
                          ? "—"
                          : item.best_distance.toFixed(4)}
                      </strong>
                      <small>Lower is a closer match</small>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
          <p className="accuracy-note">
            Accuracy is based on saved user ratings, not an automatic correctness
            test. More rated answers make the comparison more informative.
          </p>
        </section>

        {results.length > 0 && (
          <>
            <section className="summary-section" aria-label="Answer summary">
              <div className="section-heading results-heading">
                <div>
                  <span className="step-number">04</span>
                  <h2>Latest run</h2>
                </div>
                <span className="selection-count">
                  {results.filter((result) => !result.error).length} of {results.length} answered
                </span>
              </div>
              <div className="summary-grid">
                <SummaryCard
                  label="MODELS"
                  value={`${results.length}`}
                  detail="Selected for this run"
                  icon="◇"
                />
                <SummaryCard
                  label="ANSWERS RATED"
                  value={`${ratedResults.length}`}
                  detail={
                    accuracy === null
                      ? "Rate an answer below"
                      : `${accuracy}% correct in this run`
                  }
                  icon="◎"
                />
                <SummaryCard
                  label="AVG. TOTAL TIME"
                  value={averageTime === null ? "—" : formatSeconds(averageTime)}
                  detail="Retrieval + generation"
                  icon="◷"
                />
                <SummaryCard
                  label="BEST DISTANCE"
                  value={bestDistance === null ? "—" : bestDistance.toFixed(4)}
                  detail="Lower is a closer match"
                  icon="⌖"
                />
              </div>
              <p className="accuracy-note">
                Response times are measured end-to-end and can vary with API load
                and network conditions.
              </p>
            </section>

            <section className="answer-section">
              <div className="section-heading results-heading">
                <div>
                  <h2>Model answers</h2>
                </div>
                <span className="question-chip">{question}</span>
              </div>
              <div className="answer-grid">
                {results.map((result) => (
                  <article className="answer-card panel" key={result.model}>
                    <div className="answer-card-head">
                      <div className="answer-model">
                        <span className="model-icon">✳</span>
                        <div>
                          <h3>{result.model}</h3>
                          <span>{modelDescriptions[result.model] || "Model response"}</span>
                        </div>
                      </div>
                      <span className={`feedback-status ${result.feedback === "Correct" ? "positive" : result.feedback === "Incorrect" ? "negative" : ""}`}>
                        {result.error ? "Failed" : result.feedback}
                      </span>
                    </div>
                    {result.error ? (
                      <p className="answer-error">{result.error}</p>
                    ) : (
                      <p className="answer-text">{result.answer || "The model returned an empty answer."}</p>
                    )}
                    <div className="answer-metrics">
                      <div>
                        <span>BEST DISTANCE</span>
                        <strong>{bestDistance === null ? "—" : bestDistance.toFixed(4)}</strong>
                      </div>
                      <div>
                        <span>TOTAL TIME</span>
                        <strong>{formatSeconds(result.total_seconds)}</strong>
                      </div>
                      <div>
                        <span>ACCURACY</span>
                        <strong>{result.error ? "—" : result.feedback}</strong>
                      </div>
                    </div>
                    {!result.error && (
                      <div className="rating-row">
                        <span>Was this answer correct?</span>
                        <div className="rating-actions">
                          <button
                            type="button"
                            className={result.feedback === "Correct" ? "rated-correct" : ""}
                            disabled={feedbackBusy === result.model}
                            onClick={() => rateAnswer(result, "Correct")}
                          >
                            ✓ Correct
                          </button>
                          <button
                            type="button"
                            className={result.feedback === "Incorrect" ? "rated-incorrect" : ""}
                            disabled={feedbackBusy === result.model}
                            onClick={() => rateAnswer(result, "Incorrect")}
                          >
                            ✕ Incorrect
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            </section>

            {retrievedChunks.length > 0 && (
              <details className="sources-panel panel">
                <summary>
                  <span>
                    <span className="step-number">06</span>
                    Retrieved source chunks
                  </span>
                  <span className="source-count">
                    {retrievedChunks.length} chunks <span aria-hidden="true">⌄</span>
                  </span>
                </summary>
                <div className="source-list">
                  {retrievedChunks.map((chunk) => (
                    <article className="source-item" key={chunk.id}>
                      <div className="source-meta">
                        <strong>{chunk.id}</strong>
                        <span>Distance {chunk.distance.toFixed(4)}</span>
                      </div>
                      <p>{chunk.text}</p>
                      <small>{chunk.source}</small>
                    </article>
                  ))}
                </div>
              </details>
            )}
          </>
        )}
      </section>
      <footer className="footer">
        <span>RAG Model Studio</span>
        <span>Model answers may be inaccurate. Review before relying on them.</span>
      </footer>
    </main>
  );
}

function ComparisonChart({
  title,
  description,
  rows,
  suffix,
  scale,
  tone,
  emptyMessage,
}) {
  const maximum = scale || Math.max(0, ...rows.map((row) => row.value || 0));
  const hasValues = rows.some((row) => row.value !== null && row.value !== undefined);

  return (
    <article className="comparison-chart panel">
      <div className="chart-heading">
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        <span className={`chart-mark ${tone}`} aria-hidden="true">
          {tone === "accuracy" ? "◎" : "◷"}
        </span>
      </div>
      {!hasValues ? (
        <p className="chart-empty">{emptyMessage}</p>
      ) : (
        <div className="chart-rows">
          {rows.map((row) => {
            const hasValue = row.value !== null && row.value !== undefined;
            const width =
              hasValue && maximum > 0
                ? Math.max(row.value > 0 ? 2 : 0, (row.value / maximum) * 100)
                : 0;
            const value =
              !hasValue
                ? "—"
                : tone === "timing"
                  ? formatSeconds(row.value)
                  : `${row.value}${suffix}`;

            return (
              <div className="chart-row" key={row.model}>
                <div className="chart-model-label">
                  <strong title={row.model}>{row.model}</strong>
                  <small>{row.detail}</small>
                </div>
                <div
                  className="chart-track"
                  role="img"
                  aria-label={`${row.model}: ${hasValue ? value : "no data"}`}
                >
                  <span
                    className={`chart-bar ${tone}`}
                    style={{ width: `${width}%` }}
                  />
                </div>
                <strong className="chart-value">{value}</strong>
              </div>
            );
          })}
        </div>
      )}
    </article>
  );
}

function SummaryCard({ label, value, detail, icon }) {
  return (
    <article className="summary-card panel">
      <div className="summary-label">
        <span>{label}</span>
        <span className="summary-icon" aria-hidden="true">{icon}</span>
      </div>
      <strong className="summary-value">{value}</strong>
      <span className="summary-detail">{detail}</span>
    </article>
  );
}

export default App;
