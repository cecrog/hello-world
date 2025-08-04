# 📈 Fintech & Crypto Intelligence Dashboard

A powerful tool to stay up-to-date with the latest fintech and cryptocurrency trends by aggregating content from RSS feeds and Twitter. Built with Python and Streamlit.

![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **📰 RSS Feed Aggregation**: Automatically collects news from 10+ top fintech sources
- **🐦 Twitter Integration**: Monitors fintech influencers and keyword-based tweets
- **🧠 Sentiment Analysis**: AI-powered sentiment scoring for all content
- **📊 Analytics Dashboard**: Beautiful visualizations and trending analysis
- **🔍 Advanced Search**: Search across all collected content with filters
- **⏰ Real-time Updates**: Refresh data on-demand or schedule automatic collection
- **🎯 Smart Filtering**: Filter by time, sentiment, source, and keywords

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RSS Feeds     │    │   Twitter API   │    │   SQLite DB     │
│                 │    │                 │    │                 │
│ • CoinDesk      │───▶│ • Influencers   │───▶│ • Articles      │
│ • The Block     │    │ • Keywords      │    │ • Tweets        │
│ • Decrypt       │    │ • Sentiment     │    │ • Analytics     │
│ • + 7 more      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  Streamlit UI   │
                                              │                 │
                                              │ • Dashboard     │
                                              │ • Analytics     │
                                              │ • Search        │
                                              └─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Twitter API (Optional)

1. Get Twitter API credentials from [developer.twitter.com](https://developer.twitter.com/)
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Add your Twitter API credentials to `.env`

### 3. Collect Initial Data

```bash
python collector.py
```

### 4. Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## 📊 Data Sources

### RSS Feeds (Always Available)
- **CoinDesk** - Leading crypto news
- **The Block** - Crypto industry analysis  
- **Decrypt** - Crypto culture and tech
- **Cointelegraph** - Global crypto news
- **DeFi Pulse** - DeFi ecosystem updates
- **a16z Crypto** - Venture capital insights
- **Fintech Takes** - Fintech industry analysis
- **Andreessen Horowitz** - Tech and finance
- **CB Insights** - Market intelligence
- **TechCrunch Fintech** - Startup news

### Twitter Sources (Requires API)
**Monitored Accounts:**
- @naval, @balajis, @VitalikButerin
- @APompliano, @RyanSAdams, @stani
- @hasufl, @sassal0x, @cburniske
- And 7 more top crypto influencers

**Keyword Monitoring:**
- fintech, defi, crypto, blockchain
- bitcoin, ethereum, web3, dao
- And 20+ more relevant terms

## 🛠️ Usage

### Dashboard Interface

1. **📊 Analytics Tab**
   - Overall sentiment analysis
   - Trending keywords
   - Activity timeline
   - Content distribution

2. **📰 Articles Tab** 
   - Latest RSS articles
   - Sentiment scoring
   - Source attribution
   - Keyword extraction

3. **🐦 Tweets Tab**
   - Recent relevant tweets
   - Engagement metrics
   - Influencer tracking
   - Sentiment analysis

4. **🔍 Search Tab**
   - Full-text search
   - Advanced filters
   - Sentiment range selection
   - Content type filtering

### Data Collection

**Manual Collection:**
```bash
python collector.py
```

**Scheduled Collection (recommended):**
```bash
# Add to crontab for hourly collection
0 * * * * /path/to/python /path/to/collector.py
```

**RSS Only (no Twitter API needed):**
```bash
python rss_aggregator.py
```

## ⚙️ Configuration

### RSS Feeds
Edit `config.py` to add/remove RSS sources:
```python
RSS_FEEDS = {
    "Your Source": "https://example.com/feed.xml",
    # Add more feeds here
}
```

### Keywords
Customize monitored keywords in `config.py`:
```python
FINTECH_KEYWORDS = [
    "your_keyword", "another_term",
    # Add relevant terms
]
```

### Twitter Accounts
Update Twitter influencer list in `config.py`:
```python
TWITTER_ACCOUNTS = [
    "username1", "username2",
    # Add accounts to monitor
]
```

## 📁 Project Structure

```
fintech-intelligence/
├── 📄 requirements.txt      # Python dependencies
├── ⚙️  config.py            # Configuration settings
├── 🗄️  database.py          # Database operations
├── 📰 rss_aggregator.py     # RSS feed collection
├── 🐦 twitter_client.py     # Twitter API integration
├── 🧠 sentiment_analyzer.py # Sentiment analysis
├── 📊 dashboard.py          # Streamlit dashboard
├── 🔄 collector.py          # Data collection script
├── 📝 .env.example          # Environment template
└── 📖 README.md             # This file
```

## 🔧 Advanced Features

### Sentiment Analysis
- Uses TextBlob for natural language processing
- Scores from -1 (very negative) to +1 (very positive)
- Specialized fintech/crypto keyword detection
- Market sentiment aggregation

### Data Storage
- SQLite database for lightweight deployment
- Automatic deduplication
- Indexed searches
- JSON keyword storage

### Performance
- Streamlit caching for fast dashboard loading
- Respects API rate limits
- Efficient database queries
- Background data collection

## 🚀 Deployment Options

### Local Development
```bash
streamlit run dashboard.py
```

### Docker (Coming Soon)
```bash
docker build -t fintech-intelligence .
docker run -p 8501:8501 fintech-intelligence
```

### Cloud Deployment
- Deploy to Streamlit Cloud
- Heroku compatible
- Railway/Render ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only. Not financial advice. Always do your own research before making investment decisions.

## 🆘 Support

- 📧 Create an issue for bug reports
- 💡 Feature requests welcome
- 📖 Check the docs for troubleshooting

---

**Happy fintech monitoring! 📈**
