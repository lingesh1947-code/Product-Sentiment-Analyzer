import axios from "axios";

const BASE_URL = "http://localhost:5000"; // Change this to your backend URL

// Demo fallback data used when backend is not connected
export const DEMO_DATA = {
  product_name: "Sony WH-1000XM5 Wireless Headphones",
  product_url: "https://www.amazon.in/dp/B09XS7JWHH",
  total_reviews: 248,
  sentiment_summary: {
    positive: 162,
    negative: 41,
    neutral: 45,
  },
  sentiment_percentages: {
    positive: 65.3,
    negative: 16.5,
    neutral: 18.2,
  },
  trend_data: [
    { date: "Jan", positive: 18, negative: 5, neutral: 7 },
    { date: "Feb", positive: 22, negative: 6, neutral: 9 },
    { date: "Mar", positive: 28, negative: 8, neutral: 6 },
    { date: "Apr", positive: 31, negative: 7, neutral: 10 },
    { date: "May", positive: 35, negative: 9, neutral: 7 },
    { date: "Jun", positive: 28, negative: 6, neutral: 6 },
  ],
  top_keywords: [
    { word: "noise cancelling", count: 87 },
    { word: "battery life", count: 74 },
    { word: "sound quality", count: 68 },
    { word: "comfortable", count: 55 },
    { word: "value", count: 43 },
    { word: "premium", count: 38 },
    { word: "microphone", count: 31 },
    { word: "Bluetooth", count: 28 },
    { word: "carrying case", count: 22 },
    { word: "price", count: 19 },
  ],
  reviews: [
    {
      id: 1,
      text: "Absolutely love these headphones! The noise cancellation is phenomenal and the battery lasts forever. Best purchase I've made this year.",
      sentiment: "positive",
      confidence: 0.97,
      source: "Amazon",
      date: "2024-05-21 10:32",
    },
    {
      id: 2,
      text: "Decent headphones but the ear cups feel a bit plasticky for the price. Sound quality is good though.",
      sentiment: "neutral",
      confidence: 0.72,
      source: "Flipkart",
      date: "2024-05-19 14:15",
    },
    {
      id: 3,
      text: "Terrible mic quality during calls. Everyone on the other end says I sound muffled. Very disappointed.",
      sentiment: "negative",
      confidence: 0.91,
      source: "Amazon",
      date: "2024-05-18 09:44",
    },
    {
      id: 4,
      text: "The ANC is industry-leading. Music sounds incredibly detailed and immersive. Worth every rupee.",
      sentiment: "positive",
      confidence: 0.95,
      source: "Amazon",
      date: "2024-05-17 18:20",
    },
    {
      id: 5,
      text: "Good product overall. Shipping was fast and packaging was intact. Would recommend.",
      sentiment: "positive",
      confidence: 0.81,
      source: "Flipkart",
      date: "2024-05-16 11:05",
    },
    {
      id: 6,
      text: "Stopped working after 3 months. Support team was unresponsive. Complete waste of money.",
      sentiment: "negative",
      confidence: 0.96,
      source: "Amazon",
      date: "2024-05-15 16:48",
    },
    {
      id: 7,
      text: "The touch controls take some getting used to but work well once you learn the gestures.",
      sentiment: "neutral",
      confidence: 0.68,
      source: "Flipkart",
      date: "2024-05-14 13:22",
    },
    {
      id: 8,
      text: "Perfect for long work from home sessions. Wear them 8+ hours with zero fatigue. Exceptional comfort.",
      sentiment: "positive",
      confidence: 0.93,
      source: "Amazon",
      date: "2024-05-13 08:55",
    },
    {
      id: 9,
      text: "Sound profile is too bass-heavy for my taste. Highs feel rolled off. Expected better for this price.",
      sentiment: "negative",
      confidence: 0.79,
      source: "Amazon",
      date: "2024-05-12 20:10",
    },
    {
      id: 10,
      text: "Connects instantly to my phone and laptop. The multipoint connection feature is super useful.",
      sentiment: "positive",
      confidence: 0.88,
      source: "Flipkart",
      date: "2024-05-11 15:33",
    },
  ],
};

/**
 * Analyze reviews for a product.
 * Sends POST /api/analyze to backend.
 * Falls back to demo data if backend is unreachable.
 *
 * @param {string} productName - Product name typed by user
 * @param {string} productUrl  - Amazon/Flipkart URL pasted by user
 * @returns {Promise<object>}  - API response or demo data
 */
export async function analyzeProduct(productName, productUrl) {
  try {
    const response = await axios.post(
      `${BASE_URL}/api/analyze`,
      {
        product_name: productName,
        product_url: productUrl,
      },
      { timeout: 30000 } // 30s timeout for scraping
    );
    return { data: response.data, isDemo: false };
  } catch (error) {
    console.warn("Backend not reachable — using demo data.", error.message);
    // Simulate a short delay so the loading state is visible
    await new Promise((r) => setTimeout(r, 1800));
    return { data: DEMO_DATA, isDemo: true };
  }
}
