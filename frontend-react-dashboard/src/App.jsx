import { useState } from "react";
import "./App.css";
import { analyzeProduct } from "./api";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line,
} from "recharts";

// ─── Color constants ────────────────────────────────────────────────────────
const COLORS = {
  positive: "#22d3a0",
  negative: "#f4615c",
  neutral:  "#f5a623",
  accent:   "#4f9ef8",
};

const PIE_COLORS = [COLORS.positive, COLORS.negative, COLORS.neutral];

// ─── Custom Recharts tooltip ─────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#181c24",
      border: "1px solid #252b3a",
      borderRadius: 10,
      padding: "10px 16px",
      fontSize: 13,
    }}>
      {label && <p style={{ color: "#6b7280", marginBottom: 6, fontFamily: "Space Mono" }}>{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || "#e8eaf0" }}>
          {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  );
};

// ─── Source icons ─────────────────────────────────────────────────────────────
const SourceIcon = ({ source }) => {
  const icons = { Amazon: "🛒", Flipkart: "🏬" };
  return <span className="source-chip">{icons[source] || "🔗"} {source}</span>;
};

// ─── Main App ────────────────────────────────────────────────────────────────
export default function App() {
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [data, setData]         = useState(null);
  const [isDemo, setIsDemo]     = useState(false);
  const [filter, setFilter]     = useState("all");

  // ── Determine if input looks like a URL
  const isUrl = (str) =>
    str.startsWith("http://") || str.startsWith("https://") || str.includes("amazon") || str.includes("flipkart");

  // ── Handle analysis
  const handleAnalyze = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setData(null);
    setFilter("all");

    const productName = isUrl(input) ? "" : input.trim();
    const productUrl  = isUrl(input) ? input.trim() : "";

    const result = await analyzeProduct(productName, productUrl);
    setData(result.data);
    setIsDemo(result.isDemo);
    setLoading(false);
  };

  // ── Filter reviews
  const filteredReviews = data?.reviews?.filter((r) =>
    filter === "all" ? true : r.sentiment === filter
  ) ?? [];

  // ── Build pie data
  const pieData = data
    ? [
        { name: "Positive", value: data.sentiment_summary.positive },
        { name: "Negative", value: data.sentiment_summary.negative },
        { name: "Neutral",  value: data.sentiment_summary.neutral },
      ]
    : [];

  // ── Build bar data
  const barData = data
    ? [
        { name: "Positive", count: data.sentiment_summary.positive, fill: COLORS.positive },
        { name: "Negative", count: data.sentiment_summary.negative, fill: COLORS.negative },
        { name: "Neutral",  count: data.sentiment_summary.neutral,  fill: COLORS.neutral  },
      ]
    : [];

  // ── Export CSV
  const handleExportCSV = () => {
    if (!data) return;
    const headers = ["Review Text", "Sentiment", "Confidence", "Source", "Date"];
    const rows = filteredReviews.map((r) => [
      `"${r.text.replace(/"/g, '""')}"`,
      r.sentiment,
      r.confidence,
      r.source,
      r.date,
    ]);
    const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `sentiment_reviews_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      {/* ── Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">📊</div>
            <span className="logo-title">SentimentScope</span>
          </div>
          <p className="header-sub">Product Review Intelligence Dashboard</p>
        </div>
        {isDemo && (
          <div className="demo-badge">
            <span className="demo-dot" />
            DEMO DATA — Connect your backend to see live results
          </div>
        )}
      </header>

      {/* ── Search */}
      <section className="search-section">
        <p className="search-label">🔍 Analyze Product Reviews</p>
        <div className="search-row">
          <input
            className="search-input"
            type="text"
            placeholder="Enter product name or Amazon / Flipkart URL"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
          />
          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={loading || !input.trim()}
          >
            {loading ? "⏳ Analyzing..." : "⚡ Analyze Reviews"}
          </button>
        </div>
      </section>

      {/* ── Loading */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
          <p className="loading-text">PROCESSING REVIEWS</p>
          <div className="loading-steps">
            <span className="step-pill">🕷 Scraping reviews</span>
            <span className="step-pill">🧠 Running VADER/TextBlob</span>
            <span className="step-pill">💾 Storing in MongoDB</span>
          </div>
        </div>
      )}

      {/* ── Empty state */}
      {!loading && !data && (
        <div className="empty-state">
          <div className="empty-icon">🔭</div>
          <h2 className="empty-title">No data yet</h2>
          <p className="empty-sub">
            Enter a product name or paste an Amazon / Flipkart URL above and click <strong>Analyze Reviews</strong> to get started.
          </p>
        </div>
      )}

      {/* ── Dashboard */}
      {!loading && data && (
        <div className="dashboard">

          {/* ── Section: Summary Cards */}
          <p className="section-title">Overview</p>
          <div className="summary-grid">
            {/* Product card */}
            <div className="card card--product">
              <div className="card-accent-bar" />
              <div className="card-label">📦 Product Analyzed</div>
              <div className="product-name">{data.product_name}</div>
              {data.product_url && (
                <div className="product-url">{data.product_url}</div>
              )}
            </div>

            {/* Total */}
            <div className="card card--total">
              <div className="card-accent-bar" />
              <div className="card-label">📝 Total Reviews</div>
              <div className="card-value">{data.total_reviews}</div>
              <div className="card-sub">reviews scraped</div>
            </div>

            {/* Positive */}
            <div className="card card--pos">
              <div className="card-accent-bar" />
              <div className="card-label">✅ Positive</div>
              <div className="card-value">{data.sentiment_summary.positive}</div>
              <div className="card-sub">{data.sentiment_percentages.positive}% of reviews</div>
            </div>

            {/* Negative */}
            <div className="card card--neg">
              <div className="card-accent-bar" />
              <div className="card-label">❌ Negative</div>
              <div className="card-value">{data.sentiment_summary.negative}</div>
              <div className="card-sub">{data.sentiment_percentages.negative}% of reviews</div>
            </div>

            {/* Neutral */}
            <div className="card card--neu">
              <div className="card-accent-bar" />
              <div className="card-label">➖ Neutral</div>
              <div className="card-value">{data.sentiment_summary.neutral}</div>
              <div className="card-sub">{data.sentiment_percentages.neutral}% of reviews</div>
            </div>
          </div>

          {/* ── Section: Charts */}
          <p className="section-title">Sentiment Insights</p>
          <div className="charts-grid">
            {/* Pie Chart */}
            <div className="chart-card">
              <div className="chart-title">🥧 Sentiment Distribution</div>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i]} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    iconType="circle"
                    formatter={(v) => <span style={{ color: "#9aa3b2", fontSize: 12 }}>{v}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Bar Chart */}
            <div className="chart-card">
              <div className="chart-title">📊 Sentiment Counts</div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={barData} barCategoryGap="35%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {barData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Line Chart – full width */}
            <div className="chart-card chart-card--full">
              <div className="chart-title">📈 Review Trends Over Time</div>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={data.trend_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend formatter={(v) => <span style={{ color: "#9aa3b2", fontSize: 12 }}>{v}</span>} />
                  <Line type="monotone" dataKey="positive" stroke={COLORS.positive} strokeWidth={2.5} dot={{ r: 4, fill: COLORS.positive }} name="Positive" />
                  <Line type="monotone" dataKey="negative" stroke={COLORS.negative} strokeWidth={2.5} dot={{ r: 4, fill: COLORS.negative }} name="Negative" />
                  <Line type="monotone" dataKey="neutral"  stroke={COLORS.neutral}  strokeWidth={2.5} dot={{ r: 4, fill: COLORS.neutral }}  name="Neutral"  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ── Section: Keywords */}
          <p className="section-title">Top Keywords</p>
          <div className="keywords-card">
            <div className="keywords-title">🔑 Frequently Mentioned Terms</div>
            <div className="keywords-grid">
              {data.top_keywords.map((kw, i) => (
                <div className="keyword-chip" key={i}>
                  <span>{kw.word}</span>
                  <span className="keyword-count">{kw.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── Section: Reviews Table */}
          <p className="section-title">Reviews</p>
          <div className="reviews-section">
            <div className="reviews-header">
              <span className="reviews-title">
                📋 {filteredReviews.length} Review{filteredReviews.length !== 1 ? "s" : ""}
                {filter !== "all" && ` · ${filter.charAt(0).toUpperCase() + filter.slice(1)}`}
              </span>

              {/* Filter buttons */}
              <div className="filter-row">
                {["all", "positive", "negative", "neutral"].map((f) => (
                  <button
                    key={f}
                    className={`filter-btn ${f} ${filter === f ? "active" : ""}`}
                    onClick={() => setFilter(f)}
                  >
                    {f === "all"      && "All"}
                    {f === "positive" && "✅ Positive"}
                    {f === "negative" && "❌ Negative"}
                    {f === "neutral"  && "➖ Neutral"}
                  </button>
                ))}
              </div>

              {/* Export */}
              <button className="export-btn" onClick={handleExportCSV}>
                ⬇ Export CSV
              </button>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Review</th>
                    <th>Sentiment</th>
                    <th>Confidence</th>
                    <th>Source</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReviews.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: "center", color: "#6b7280", padding: "32px" }}>
                        No reviews match this filter.
                      </td>
                    </tr>
                  ) : (
                    filteredReviews.map((review, idx) => (
                      <tr key={review.id}>
                        <td style={{ color: "#6b7280", fontFamily: "Space Mono", fontSize: 11 }}>
                          {idx + 1}
                        </td>
                        <td className="review-text">{review.text}</td>
                        <td>
                          <span className={`badge badge--${review.sentiment}`}>
                            {review.sentiment}
                          </span>
                        </td>
                        <td>
                          <div className="confidence-bar-wrap">
                            <div className="confidence-bar">
                              <div
                                className="confidence-fill"
                                style={{
                                  width: `${review.confidence * 100}%`,
                                  background:
                                    review.sentiment === "positive" ? COLORS.positive
                                    : review.sentiment === "negative" ? COLORS.negative
                                    : COLORS.neutral,
                                }}
                              />
                            </div>
                            <span className="confidence-label">
                              {(review.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </td>
                        <td><SourceIcon source={review.source} /></td>
                        <td className="date-text">{review.date}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
