from textblob import TextBlob
import re
from datetime import datetime
from collections import Counter

def analyze_sentiment(text):
    """
    Analyze sentiment of text using TextBlob.
    Returns a score from -1 (very negative) to 1 (very positive).
    """
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def get_sentiment_label(score):
    """Convert sentiment score to human-readable label."""
    if score >= 0.1:
        return "Positive"
    elif score <= -0.1:
        return "Negative"
    else:
        return "Neutral"

def get_sentiment_emoji(score):
    """Get emoji representation of sentiment."""
    if score >= 0.3:
        return "🟢"
    elif score >= 0.1:
        return "🟡"
    elif score <= -0.3:
        return "🔴"
    elif score <= -0.1:
        return "🟠"
    else:
        return "⚪"

def extract_sentiment_keywords(text):
    """Extract words that might indicate strong sentiment."""
    positive_keywords = [
        'bullish', 'pump', 'moon', 'surge', 'rally', 'breakthrough', 'adoption',
        'growth', 'innovative', 'revolutionary', 'excellent', 'amazing', 'huge',
        'partnership', 'acquisition', 'launch', 'success', 'winning', 'explosive'
    ]
    
    negative_keywords = [
        'bearish', 'dump', 'crash', 'fall', 'decline', 'loss', 'hack', 'scam',
        'fraud', 'regulation', 'ban', 'warning', 'risk', 'problem', 'failure',
        'concern', 'investigation', 'lawsuit', 'penalty', 'collapse'
    ]
    
    text_lower = text.lower()
    found_positive = [word for word in positive_keywords if word in text_lower]
    found_negative = [word for word in negative_keywords if word in text_lower]
    
    return {
        'positive': found_positive,
        'negative': found_negative
    }

def analyze_market_sentiment(articles, tweets, timeframe_hours=24):
    """
    Analyze overall market sentiment from recent articles and tweets.
    """
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
    
    sentiments = []
    sources = {'articles': 0, 'tweets': 0}
    
    # Analyze articles
    for article in articles:
        try:
            article_time = datetime.fromisoformat(article.get('created_at', ''))
            if article_time >= cutoff_time:
                sentiments.append(article.get('sentiment_score', 0))
                sources['articles'] += 1
        except:
            # If we can't parse the date, include it anyway
            sentiments.append(article.get('sentiment_score', 0))
            sources['articles'] += 1
    
    # Analyze tweets
    for tweet in tweets:
        try:
            tweet_time = datetime.fromisoformat(tweet.get('stored_at', ''))
            if tweet_time >= cutoff_time:
                sentiments.append(tweet.get('sentiment_score', 0))
                sources['tweets'] += 1
        except:
            sentiments.append(tweet.get('sentiment_score', 0))
            sources['tweets'] += 1
    
    if not sentiments:
        return {
            'overall_sentiment': 0,
            'sentiment_label': 'Neutral',
            'sentiment_emoji': '⚪',
            'total_items': 0,
            'sources': sources,
            'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
        }
    
    # Calculate statistics
    avg_sentiment = sum(sentiments) / len(sentiments)
    
    # Count distribution
    positive_count = len([s for s in sentiments if s > 0.1])
    negative_count = len([s for s in sentiments if s < -0.1])
    neutral_count = len(sentiments) - positive_count - negative_count
    
    return {
        'overall_sentiment': avg_sentiment,
        'sentiment_label': get_sentiment_label(avg_sentiment),
        'sentiment_emoji': get_sentiment_emoji(avg_sentiment),
        'total_items': len(sentiments),
        'sources': sources,
        'distribution': {
            'positive': positive_count,
            'neutral': neutral_count,
            'negative': negative_count
        }
    }

def get_trending_keywords(articles, tweets, min_mentions=2):
    """Extract trending keywords from recent content."""
    all_keywords = []
    
    # Collect keywords from articles
    for article in articles:
        keywords = article.get('keywords', [])
        all_keywords.extend(keywords)
    
    # Collect keywords from tweets
    for tweet in tweets:
        keywords = tweet.get('keywords', [])
        all_keywords.extend(keywords)
    
    # Count occurrences
    keyword_counts = Counter(all_keywords)
    
    # Filter by minimum mentions and return sorted
    trending = {
        keyword: count 
        for keyword, count in keyword_counts.items() 
        if count >= min_mentions
    }
    
    return dict(sorted(trending.items(), key=lambda x: x[1], reverse=True))

def filter_by_sentiment(content_list, min_sentiment=None, max_sentiment=None):
    """Filter content by sentiment score range."""
    filtered = []
    
    for item in content_list:
        sentiment = item.get('sentiment_score', 0)
        
        if min_sentiment is not None and sentiment < min_sentiment:
            continue
        if max_sentiment is not None and sentiment > max_sentiment:
            continue
            
        filtered.append(item)
    
    return filtered

def get_sentiment_summary(content_list):
    """Get a summary of sentiment distribution."""
    if not content_list:
        return {}
    
    sentiments = [item.get('sentiment_score', 0) for item in content_list]
    
    positive = len([s for s in sentiments if s > 0.1])
    negative = len([s for s in sentiments if s < -0.1])
    neutral = len(sentiments) - positive - negative
    
    avg_sentiment = sum(sentiments) / len(sentiments)
    
    return {
        'total': len(content_list),
        'average_sentiment': avg_sentiment,
        'distribution': {
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        },
        'percentages': {
            'positive': round(positive / len(sentiments) * 100, 1),
            'negative': round(negative / len(sentiments) * 100, 1),
            'neutral': round(neutral / len(sentiments) * 100, 1)
        }
    }