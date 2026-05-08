import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SearchFrom from "../components/SearchFrom";
import StatsCard from "../components/StatsCard";
import SentimentChart from "../components/SentimentChart";

function Dashboard() {
  return (
    <div>
      <Navbar />
      <Sidebar />

      <h1>Product Sentiment Dashboard</h1>

      <SearchFrom />

      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <StatsCard title="Positive Reviews" value="120" />
        <StatsCard title="Negative Reviews" value="30" />
      </div>

      <SentimentChart />
    </div>
  );
}

export default Dashboard;