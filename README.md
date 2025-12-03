# 📊 InsightGen

**Automated Weekly Performance Report Generator with AI-Powered Insights**

Transform raw performance data into beautiful, actionable executive reports with AI-powered insights, weather correlations, anomaly detection, and competitive benchmarking. Upload multiple CSV files, and InsightGen automatically generates descriptive and prescriptive analytics in PDF or PowerPoint format.

---

## 🎯 Problem Statement

Account Managers and Analytics teams waste hours manually downloading CSVs, calculating metrics, and creating reports for clients. This is slow, error-prone, and doesn't scale.

**InsightGen solves this:** Automate the entire pipeline from data ingestion → analysis → report generation with **intelligent insights that drive action**.

---

## ✨ Key Features

### Core Features
- **Multi-Source Data Ingestion**: Upload multiple CSV files (campaigns, traffic, weather, customers, budget)
- **Automatic Data Standardization**: Unifies schemas across different data sources
- **Intelligent Merging**: Combines data on common keys (date, campaign_id, location)
- **Descriptive Analytics**: Automatic calculation of KPIs (CTR, CPC, CPA, ROAS, etc.)
- **Beautiful Reports**: Exports as PDF or PowerPoint, ready for client presentations
- **Interactive Frontend**: User-friendly web interface for non-technical users
- **One-Click Generation**: Simple "Generate Report" button—no coding required

### 🌟 Unique Differentiators (Stand-Out Features)

1. **🌦️ Weather-Driven Marketing Insights**
   - Automatically correlate performance metrics with weather data
   - Discover patterns: "On rainy days, foot traffic drops 23%, but online conversions increase 15%"
   - AI-generated recommendation: "Increase digital ad spend on weather-forecasted rainy days"
   - Example: "Temperature drops correlate with 18% higher conversion rates—test seasonal messaging"

2. **🚨 Anomaly Detection & Alerts**
   - Automatically detect unusual spikes/drops in KPIs using statistical methods
   - Flag critical changes with severity levels: Critical/Warning/Info
   - Root cause analysis: "Email campaign had 0 opens on Jan 5 due to subject line change"
   - Smart alerting: Only flag anomalies that matter (>15% variance)

3. **📊 Competitor Benchmarking**
   - Compare client's performance against industry averages
   - Show relative performance: "Your ROAS is 3.2x (industry avg 2.1x) — you're in top 10%"
   - Identify gaps: "CPA is 15% above benchmark—investigate"
   - Benchmarks included for: CTR, CPC, CVR, CPA, ROAS by channel & industry

4. **🔮 Predictive Next-Week Forecast**
   - Use historical trends to predict next week's key metrics
   - Include confidence intervals: "Expected conversions: 650-720 (70% confidence)"
   - Identify growth/decline trends before they happen
   - Help with proactive budget allocation

5. **🎯 AI-Powered Insights**: Uses Gemini/Groq LLM to generate:
   - **Descriptive**: What happened in the data (facts, trends, outliers)
   - **Prescriptive**: What actions to take (5+ actionable recommendations)

---

## 🏗️ Architecture

```
Frontend (HTML/JS)
    ↓ (CSV Upload)
    ↓
Backend (Python/Flask)
    ├─ Step 1: Data Ingestion (Pandas)
    ├─ Step 2: Data Cleaning & Merging
    ├─ Step 3: KPI Calculation
    ├─ Step 4: Weather Correlation Analysis
    ├─ Step 5: Anomaly Detection (Std Dev, Z-Score)
    ├─ Step 6: Competitive Benchmarking
    ├─ Step 7: Predictive Forecasting
    ├─ Step 8: LLM Integration (Gemini/Groq)
    ├─ Step 9: Chart Generation (Matplotlib)
    └─ Step 10: Report Export (ReportLab/python-pptx)
    ↓
    ↓ (PDF/PPT Download with AI Insights)
    ↓
Client (Beautiful, Actionable Report)
```

---

## 📋 Data Requirements

The system accepts multiple CSV files with the following structure:

### 1. **campaigns.csv**
```
date, campaign_id, campaign_name, channel, impressions, clicks, spend, conversions, revenue
2025-01-01, C1, "Spring Sale", email, 50000, 2500, 500, 125, 2500
```

### 2. **traffic.csv**
```
date, store_id, store_name, city, visits, unique_visitors
2025-01-01, S1, "Main Store", "New York", 1200, 950
```

### 3. **weather.csv** (NEW: Powers Weather Insights)
```
date, city, temperature_c, rainfall_mm
2025-01-01, "New York", 15, 0.5
```

### 4. **customers.csv**
```
customer_id, signup_date, segment, city, lifetime_value, last_purchase_date
C1001, 2024-06-15, "VIP", "New York", 5000, 2025-01-10
```

### 5. **budget.csv**
```
date, campaign_id, planned_spend, actual_spend
2025-01-01, C1, 1000, 950
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Node.js (optional, for frontend)

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/InsightGen.git
cd InsightGen

# Install Python dependencies
pip install -r requirements.txt

# Set up API keys (Gemini or Groq)
export GEMINI_API_KEY="your_api_key_here"
# OR
export GROQ_API_KEY="your_api_key_here"
```

### Run Locally

#### Option 1: CLI (Fastest for Hackathon)
```bash
python generate_report.py --csvs campaigns.csv traffic.csv weather.csv --week "2025-01-01" --format pdf --client "Acme Corp" --include-anomalies --include-benchmarks --include-forecast
```

#### Option 2: Web Interface
```bash
flask run
# Open http://localhost:5000
```

---

## 📁 Project Structure

```
InsightGen/
├── frontend/
│   ├── index.html              # Main web interface
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── backend/
│   ├── pipeline.py             # Step 1: Data ingestion & merging
│   ├── kpi_calculator.py       # Step 2: Compute metrics
│   ├── weather_analyzer.py     # Step 3: Weather correlation analysis (NEW)
│   ├── anomaly_detector.py     # Step 4: Anomaly detection (NEW)
│   ├── benchmarking.py         # Step 5: Competitive benchmarking (NEW)
│   ├── forecaster.py           # Step 6: Predictive forecasting (NEW)
│   ├── insights_generator.py   # Step 7: LLM integration
│   ├── chart_generator.py      # Step 8: Create visualizations
│   ├── report_builder.py       # Step 9: PDF/PPT generation
│   ├── app.py                  # Flask/FastAPI server
│   └── config.py               # Configuration & API keys
├── sample_data/
│   ├── campaigns.csv
│   ├── traffic.csv
│   ├── weather.csv
│   ├── customers.csv
│   └── budget.csv
├── benchmarks/
│   └── industry_benchmarks.json # Industry average KPIs (NEW)
├── requirements.txt
├── README.md
└── .env                        # API keys (do NOT commit)
```

---

## 🔧 Technical Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | Python 3.8+ |
| **Data Processing** | Pandas, Polars, NumPy, SciPy |
| **Anomaly Detection** | Scipy (Z-Score, Standard Deviation) |
| **Weather Analysis** | Pandas Correlation, Pearson |
| **Forecasting** | Statsmodels (ARIMA), Scikit-learn |
| **LLM Integration** | Gemini API, Groq API |
| **Visualization** | Matplotlib, Seaborn |
| **Report Generation** | ReportLab (PDF), python-pptx (PowerPoint) |
| **Web Framework** | Flask or FastAPI |
| **Deployment** | Docker, GitHub Actions |

---

## 📊 Sample Report Outputs

### Descriptive Insights
- **Impressions**: 250,000 total | 8,064 daily average
- **Clicks**: 12,500 total | CTR: 5.0%
- **Conversions**: 625 total | CVR: 5.0% | CPA: $40
- **Revenue**: $12,500 | ROAS: 2.5x

### 🌦️ Weather-Driven Insights (NEW)
- "Performance correlates strongly with temperature (r=0.72)"
- "On rainy days, foot traffic drops 23% but online sales increase 15%"
- "Recommendation: Shift 15% of budget to digital ads on rainy day forecasts"

### 🚨 Anomalies Detected (NEW)
- **Critical**: Email CTR dropped 45% on Jan 5 (typical: 5.2%, observed: 2.8%)
- **Warning**: Social media CPC increased 18% (above 2-week average)
- **Info**: Store visits spiked 32% on Jan 6 (weekend + local event)

### 📊 Competitive Benchmarking (NEW)
- **Your CTR**: 5.0% | **Industry Avg**: 3.2% | **Status**: ✅ Top 15%
- **Your CPA**: $40 | **Industry Avg**: $38 | **Status**: ⚠️ Slightly High
- **Your ROAS**: 2.5x | **Industry Avg**: 2.1x | **Status**: ✅ Top 20%

### 🔮 Next Week Forecast (NEW)
- **Expected Conversions**: 680-750 (70% confidence)
- **Trend**: Gradual growth expected (↑3-5% week-over-week)
- **Risk**: If weather drops below 10°C, expect 12-15% reduction

### Prescriptive Recommendations
1. **Weather-Based Optimization**: Shift digital budget during rainy forecasts
2. **Investigate Email Issues**: CTR anomaly on Jan 5 needs root cause analysis
3. **Increase Budget on High-ROAS**: Email channel showing 3.2x ROAS; recommend 20% increase
4. **Optimize Low-Performing Channels**: Social media CTR is 40% below benchmark
5. **Customer Segment Focus**: VIP segment has 5x higher LTV; allocate 30% more budget for targeting

---

## 🎓 How It Works (Step-by-Step)

### Step 1: Data Ingestion
- User uploads 4-5 CSV files via web interface
- Backend reads and validates each file
- Checks for common keys (date, campaign_id, location)

### Step 2: Data Standardization & Merging
- Renames columns to standard schema
- Converts data types (dates, numeric fields)
- Merges all files on common key (LEFT JOIN on date)

### Step 3: KPI Calculation
- CTR = Clicks / Impressions
- CPC = Spend / Clicks
- CVR = Conversions / Clicks
- CPA = Spend / Conversions
- ROAS = Revenue / Spend
- Grouping by campaign, channel, location, day-of-week

### Step 4: Weather Correlation Analysis (NEW)
```python
correlation = campaigns_df['conversions'].corr(weather_df['rainfall'])
# If |correlation| > 0.6: strong signal
# Generate insight: "Rainy days drive X% more/less conversions"
```

### Step 5: Anomaly Detection (NEW)
```python
# Use Z-Score: |value - mean| / std_dev
# Flag if Z > 2 (95% confidence it's anomalous)
anomalies = data[np.abs(stats.zscore(data['ctr'])) > 2]
```

### Step 6: Competitive Benchmarking (NEW)
```python
# Load industry_benchmarks.json
client_ctr = 5.0
industry_ctr = 3.2
percentile = (client_ctr - industry_ctr) / industry_ctr * 100
# Result: "You're in top 15%"
```

### Step 7: Predictive Forecasting (NEW)
```python
# Simple: Use trend from last 7 days + confidence interval
# Advanced: ARIMA, Linear Regression
forecast = data['conversions'].tail(7).mean() * trend_factor
```

### Step 8: LLM-Powered Insights
Prompt to Gemini/Groq:
```
You are a marketing analyst. Analyze this performance data:
[KPI Summary + Anomalies + Weather Insights + Benchmarks + Forecast in JSON]

Provide:
1. DESCRIPTIVE: What happened? (facts, trends, outliers)
2. PRESCRIPTIVE: What should we do? (5+ actionable recommendations)
```

### Step 9: Chart Generation
- Line chart: Impressions, clicks, conversions over time (highlight anomalies)
- Bar chart: ROAS by campaign/channel (vs. benchmark)
- Scatter: Weather vs. Conversions (show correlation)
- Forecast: Next 7 days with confidence interval

### Step 10: Report Generation
- **PDF/PowerPoint** with:
  - Executive summary (LLM-generated)
  - Key metrics table (vs. benchmark)
  - Weather insights section
  - Anomalies flagged with severity
  - Forecast section with confidence
  - Charts and visualizations
  - Detailed prescriptive recommendations
  - Ready to send to clients

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
# API Keys
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here

# Report Settings
REPORT_FORMAT=pdf  # or ppt
INCLUDE_RECOMMENDATIONS=true
INCLUDE_ANOMALIES=true
INCLUDE_BENCHMARKS=true
INCLUDE_FORECAST=true
INCLUDE_WEATHER_INSIGHTS=true
CLIENT_NAME="Your Client Name"

# Feature Flags
ENABLE_LLM=true
ENABLE_WEATHER_ANALYSIS=true
ENABLE_ANOMALY_DETECTION=true
ANOMALY_THRESHOLD=2.0  # Z-Score threshold

# Flask
FLASK_ENV=development
FLASK_DEBUG=true
```

---

## 📦 Requirements

```txt
pandas==2.0.0
polars==0.19.0
numpy==1.24.0
scipy==1.10.0
statsmodels==0.13.0
scikit-learn==1.3.0
flask==3.0.0
google-generativeai==0.3.0
groq==0.4.0
matplotlib==3.7.0
seaborn==0.12.0
reportlab==4.0.0
python-pptx==0.6.21
python-dotenv==1.0.0
requests==2.31.0
```

---

## 🏆 Hackathon Scope (4 Hours)

For a 4-hour hackathon, focus on this priority order:

✅ **Hour 1** (0-60 min):
- Data ingestion (pipeline.py)
- Basic KPI calculation
- Frontend file upload

✅ **Hour 2** (60-120 min):
- Weather correlation analysis
- Anomaly detection (Z-Score)
- PDF generation with tables

✅ **Hour 3** (120-180 min):
- Competitive benchmarking (use hard-coded benchmarks)
- Predictive forecasting (simple trend)
- Add charts (matplotlib)

✅ **Hour 4** (180-240 min):
- LLM integration for smart insights
- Polish UI/UX
- Testing

📌 **Minimum Demo for Judges**:
- Upload 3 CSVs → Click "Generate Report" → Download PDF showing:
  - ✅ KPI Table
  - ✅ Weather Correlation (if strong signal)
  - ✅ 2-3 Anomalies Detected
  - ✅ Benchmark Comparison
  - ✅ Simple Forecast

---

## 🚀 Features Implementation Checklist

- [x] Multi-source CSV ingestion
- [x] Data standardization & merging
- [x] KPI calculation (CTR, CPC, CVR, CPA, ROAS)
- [ ] Weather correlation analysis
- [ ] Anomaly detection
- [ ] Competitive benchmarking
- [ ] Predictive forecasting
- [ ] LLM integration
- [ ] Chart generation
- [ ] PDF/PPT export
- [ ] Interactive frontend
- [ ] CLI interface

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m "Add feature"`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙋 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/InsightGen/issues)
- Email: support@insightgen.dev

---

## 🎉 Credits

Built with ❤️ for the **4-Hour AI Hackathon**

**Team**: [Your Team Name]  
**Mentors**: [Mentor Names]  
**Event**: [Hackathon Name]

---

## 📌 Unique Value Proposition

> **InsightGen** stands out because it doesn't just report what happened—it **correlates weather patterns, detects anomalies automatically, benchmarks against competitors, and forecasts trends** to explain *why* performance changed and *what to do about it*. All in one beautiful, AI-powered report.

---

## 📌 Next Steps (Post-Hackathon)

- [ ] Deploy on AWS/GCP
- [ ] Add Docker support
- [ ] Implement user authentication & multi-tenant
- [ ] Add more LLM providers (Claude, OpenAI)
- [ ] Support more data sources (SQL databases, APIs)
- [ ] Interactive dashboard (Plotly/Dash)
- [ ] Email scheduling for automated weekly reports
- [ ] Mobile app for report viewing
- [ ] Advanced ML models (Prophet, XGBoost)
- [ ] Custom benchmarks per industry/segment

---

**Last Updated**: December 3, 2025  
**Version**: 1.0.0 (Hackathon Release with Unique Features)
