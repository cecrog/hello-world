import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from database import (
    get_recent_articles, get_recent_tweets, search_content, init_database
)
from sentiment_analyzer import (
    analyze_market_sentiment, get_trending_keywords, filter_by_sentiment,
    get_sentiment_summary, get_sentiment_emoji, get_sentiment_label
)
from rss_aggregator import fetch_rss_feeds
from twitter_client import TwitterClient
from config import RSS_FEEDS, TWITTER_ACCOUNTS

# Page configuration
st.set_page_config(
    page_title="Fintech & Crypto Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .sentiment-positive {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        text-align: center;
    }
    .sentiment-negative {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%);
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        text-align: center;
    }
    .sentiment-neutral {
        background: linear-gradient(90deg, #a8a8a8 0%, #c7c7c7 100%);
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from database with caching."""
    articles = get_recent_articles(limit=200)
    tweets = get_recent_tweets(limit=200)
    return articles, tweets

def main():
    # Initialize database
    init_database()
    
    # Header
    st.title("📈 Fintech & Crypto Intelligence Dashboard")
    st.markdown("Stay updated with the latest fintech and crypto trends from RSS feeds and Twitter")
    
    # Sidebar
    with st.sidebar:
        st.header("🛠 Controls")
        
        # Data refresh
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            with st.spinner("Fetching RSS feeds..."):
                new_articles = fetch_rss_feeds()
            
            with st.spinner("Fetching tweets..."):
                twitter_client = TwitterClient()
                new_tweets = twitter_client.collect_all_tweets()
            
            st.success(f"✅ Collected {new_articles} articles and {new_tweets} tweets")
            st.experimental_rerun()
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        
        # Time filter
        time_filter = st.selectbox(
            "Time Range",
            ["Last 24 hours", "Last 3 days", "Last 7 days", "Last 30 days", "All time"]
        )
        
        # Content type filter
        content_type = st.selectbox(
            "Content Type",
            ["All", "Articles Only", "Tweets Only"]
        )
        
        # Sentiment filter
        sentiment_filter = st.selectbox(
            "Sentiment",
            ["All", "Positive Only", "Negative Only", "Neutral Only"]
        )
        
        # Source filter
        st.subheader("📰 Sources")
        selected_sources = st.multiselect(
            "RSS Sources",
            list(RSS_FEEDS.keys()),
            default=list(RSS_FEEDS.keys())
        )
        
        # Twitter accounts filter
        selected_accounts = st.multiselect(
            "Twitter Accounts",
            TWITTER_ACCOUNTS,
            default=TWITTER_ACCOUNTS[:5]  # Default to first 5
        )
        
        st.markdown("---")
        
        # Search
        st.subheader("🔎 Search")
        search_query = st.text_input("Search keywords")
    
    # Load data
    articles, tweets = load_data()
    
    # Filter data based on sidebar selections
    # Time filtering
    if time_filter != "All time":
        hours_map = {
            "Last 24 hours": 24,
            "Last 3 days": 72,
            "Last 7 days": 168,
            "Last 30 days": 720
        }
        cutoff_time = datetime.now() - timedelta(hours=hours_map[time_filter])
        
        articles = [
            a for a in articles 
            if datetime.fromisoformat(a.get('created_at', '1900-01-01')) >= cutoff_time
        ]
        tweets = [
            t for t in tweets 
            if datetime.fromisoformat(t.get('stored_at', '1900-01-01')) >= cutoff_time
        ]
    
    # Source filtering
    if selected_sources:
        articles = [a for a in articles if a.get('source') in selected_sources]
    
    if selected_accounts:
        tweets = [t for t in tweets if t.get('username') in selected_accounts]
    
    # Sentiment filtering
    if sentiment_filter != "All":
        sentiment_map = {
            "Positive Only": (0.1, 1.0),
            "Negative Only": (-1.0, -0.1),
            "Neutral Only": (-0.1, 0.1)
        }
        min_sent, max_sent = sentiment_map[sentiment_filter]
        articles = filter_by_sentiment(articles, min_sent, max_sent)
        tweets = filter_by_sentiment(tweets, min_sent, max_sent)
    
    # Search filtering
    if search_query:
        search_results = search_content(search_query)
        # Filter articles and tweets based on search
        article_links = {r[2] for r in search_results if r[7] == 'article'}
        tweet_ids = {r[0] for r in search_results if r[6] == 'tweet'}
        
        articles = [a for a in articles if a.get('link') in article_links]
        tweets = [t for t in tweets if t.get('tweet_id') in tweet_ids]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📰 Articles</h3>
            <h2>{len(articles)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🐦 Tweets</h3>
            <h2>{len(tweets)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sentiment_data = analyze_market_sentiment(articles, tweets)
        sentiment_emoji = sentiment_data['sentiment_emoji']
        sentiment_label = sentiment_data['sentiment_label']
        st.markdown(f"""
        <div class="metric-card">
            <h3>{sentiment_emoji} Sentiment</h3>
            <h2>{sentiment_label}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        trending = get_trending_keywords(articles, tweets)
        top_keyword = list(trending.keys())[0] if trending else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔥 Trending</h3>
            <h2>{top_keyword}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "📰 Articles", "🐦 Tweets", "🔍 Search"])
    
    with tab1:
        st.header("📊 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment analysis
            st.subheader("😊 Sentiment Analysis")
            sentiment_data = analyze_market_sentiment(articles, tweets)
            
            if sentiment_data['total_items'] > 0:
                # Pie chart for sentiment distribution
                fig_sentiment = px.pie(
                    values=list(sentiment_data['distribution'].values()),
                    names=['Positive', 'Neutral', 'Negative'],
                    title="Sentiment Distribution",
                    color_discrete_map={
                        'Positive': '#38ef7d',
                        'Negative': '#ff6b6b',
                        'Neutral': '#a8a8a8'
                    }
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
                
                # Sentiment metrics
                st.metric(
                    "Overall Sentiment Score",
                    f"{sentiment_data['overall_sentiment']:.3f}",
                    delta=f"{sentiment_data['sentiment_label']}"
                )
            else:
                st.info("No data available for sentiment analysis")
        
        with col2:
            # Trending keywords
            st.subheader("🔥 Trending Keywords")
            trending = get_trending_keywords(articles, tweets, min_mentions=1)
            
            if trending:
                keywords_df = pd.DataFrame([
                    {"Keyword": k, "Mentions": v} for k, v in list(trending.items())[:10]
                ])
                
                fig_keywords = px.bar(
                    keywords_df,
                    x="Mentions",
                    y="Keyword",
                    orientation='h',
                    title="Top Keywords",
                    color="Mentions",
                    color_continuous_scale="viridis"
                )
                fig_keywords.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_keywords, use_container_width=True)
            else:
                st.info("No trending keywords found")
        
        # Source activity over time
        st.subheader("📈 Activity Over Time")
        
        if articles or tweets:
            # Prepare time series data
            all_content = []
            
            for article in articles:
                all_content.append({
                    'date': datetime.fromisoformat(article.get('created_at', '1900-01-01')).date(),
                    'type': 'Article',
                    'source': article.get('source', 'Unknown')
                })
            
            for tweet in tweets:
                all_content.append({
                    'date': datetime.fromisoformat(tweet.get('stored_at', '1900-01-01')).date(),
                    'type': 'Tweet',
                    'source': tweet.get('username', 'Unknown')
                })
            
            if all_content:
                content_df = pd.DataFrame(all_content)
                daily_counts = content_df.groupby(['date', 'type']).size().reset_index(name='count')
                
                fig_timeline = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    color='type',
                    title="Content Volume Over Time"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
    
    with tab2:
        st.header("📰 Latest Articles")
        
        if articles:
            for article in articles[:20]:  # Show top 20
                sentiment_score = article.get('sentiment_score', 0)
                sentiment_emoji = get_sentiment_emoji(sentiment_score)
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**{article['title']}**")
                        st.markdown(f"*{article['source']}* - {article.get('published_date', 'No date')}")
                        if article.get('description'):
                            st.markdown(f"{article['description'][:200]}...")
                        
                        if article.get('keywords'):
                            keywords_str = " ".join([f"`{k}`" for k in article['keywords'][:5]])
                            st.markdown(f"**Keywords:** {keywords_str}")
                        
                        st.markdown(f"[Read More]({article['link']})")
                    
                    with col2:
                        st.markdown(f"**Sentiment**")
                        st.markdown(f"{sentiment_emoji} {get_sentiment_label(sentiment_score)}")
                        st.markdown(f"**Score:** {sentiment_score:.2f}")
                    
                    st.markdown("---")
        else:
            st.info("No articles found matching your filters")
    
    with tab3:
        st.header("🐦 Latest Tweets")
        
        if tweets:
            for tweet in tweets[:20]:  # Show top 20
                sentiment_score = tweet.get('sentiment_score', 0)
                sentiment_emoji = get_sentiment_emoji(sentiment_score)
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**@{tweet['username']}**")
                        st.markdown(f"{tweet['content']}")
                        st.markdown(f"*{tweet.get('created_at', 'No date')}*")
                        
                        if tweet.get('keywords'):
                            keywords_str = " ".join([f"`{k}`" for k in tweet['keywords'][:5]])
                            st.markdown(f"**Keywords:** {keywords_str}")
                        
                        # Engagement metrics
                        retweets = tweet.get('retweet_count', 0)
                        likes = tweet.get('like_count', 0)
                        st.markdown(f"🔄 {retweets} | ❤️ {likes}")
                    
                    with col2:
                        st.markdown(f"**Sentiment**")
                        st.markdown(f"{sentiment_emoji} {get_sentiment_label(sentiment_score)}")
                        st.markdown(f"**Score:** {sentiment_score:.2f}")
                    
                    st.markdown("---")
        else:
            st.info("No tweets found matching your filters")
    
    with tab4:
        st.header("🔍 Advanced Search")
        
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_term = st.text_input("Search term", value=search_query)
            search_type = st.radio("Search in", ["All", "Articles", "Tweets"])
        
        with search_col2:
            min_sentiment = st.slider("Minimum sentiment", -1.0, 1.0, -1.0, 0.1)
            max_sentiment = st.slider("Maximum sentiment", -1.0, 1.0, 1.0, 0.1)
        
        if st.button("🔍 Search") and search_term:
            search_results = search_content(search_term, search_type.lower())
            
            if search_results:
                st.success(f"Found {len(search_results)} results")
                
                for result in search_results[:20]:
                    if result[7] == 'article':  # Article
                        st.markdown(f"📰 **{result[0]}**")
                        st.markdown(f"*{result[3]}* - {result[4]}")
                        if result[1]:
                            st.markdown(f"{result[1][:200]}...")
                        st.markdown(f"[Read More]({result[2]})")
                    else:  # Tweet
                        st.markdown(f"🐦 **@{result[1]}**")
                        st.markdown(f"{result[2]}")
                        st.markdown(f"*{result[3]}*")
                    
                    st.markdown("---")
            else:
                st.info("No results found")

if __name__ == "__main__":
    main()