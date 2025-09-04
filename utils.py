import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

def parse_article(item: Dict) -> Dict:
    """Parse an article item into a simplified format"""
    article = {
        'id': item.get('id', ''),
        'title': item.get('title', 'No title'),
        'published': item.get('published', 0),
        'published_date': datetime.fromtimestamp(item.get('published', 0)).isoformat() if item.get('published') else None,
        'author': item.get('author', 'Unknown'),
        'feed_title': item.get('origin', {}).get('title', 'Unknown feed'),
        'feed_id': item.get('origin', {}).get('streamId', ''),
        'categories': [cat.get('label', '') if isinstance(cat, dict) else str(cat) for cat in item.get('categories', [])],
        'is_read': any('state/com.google/read' in (cat.get('id', '') if isinstance(cat, dict) else str(cat)) for cat in item.get('categories', [])),
        'url': None,
        'summary': None
    }
    
    # Extract URL
    if 'alternate' in item:
        for alt in item['alternate']:
            if alt.get('type') == 'text/html':
                article['url'] = alt.get('href')
                break
                
    # Extract summary
    if 'summary' in item:
        summary = item['summary'].get('content', '')
        # Clean HTML tags
        summary = re.sub('<[^<]+?>', '', summary)
        # Truncate to reasonable length
        article['summary'] = summary[:500] + '...' if len(summary) > 500 else summary
        
    return article

def parse_feed(subscription: Dict) -> Dict:
    """Parse a subscription into a simplified format"""
    return {
        'id': subscription.get('id', ''),
        'title': subscription.get('title', 'Untitled'),
        'url': subscription.get('url', ''),
        'htmlUrl': subscription.get('htmlUrl', ''),
        'categories': [cat.get('label', '') for cat in subscription.get('categories', [])],
        'firstItemMsec': subscription.get('firstitemmsec', 0)
    }

def days_to_timestamp(days: int) -> int:
    """Convert days to Unix timestamp (for newer_than parameter)"""
    date = datetime.now() - timedelta(days=days)
    return int(date.timestamp())

def format_article_list(articles: List[Dict]) -> str:
    """Format a list of articles for display"""
    if not articles:
        return "No articles found."
        
    result = []
    for i, article in enumerate(articles, 1):
        status = "✓" if article['is_read'] else "•"
        result.append(f"{i}. {status} {article['title']}")
        result.append(f"   Feed: {article['feed_title']}")
        result.append(f"   Date: {article['published_date']}")
        if article['url']:
            result.append(f"   URL: {article['url']}")
        result.append("")
        
    return "\n".join(result)

def format_feed_list(feeds: List[Dict]) -> str:
    """Format a list of feeds for display"""
    if not feeds:
        return "No feeds found."
        
    result = []
    for i, feed in enumerate(feeds, 1):
        result.append(f"{i}. {feed['title']}")
        if feed['categories']:
            result.append(f"   Categories: {', '.join(feed['categories'])}")
        result.append(f"   URL: {feed['url']}")
        result.append("")
        
    return "\n".join(result)

def extract_item_ids(articles: List[Dict]) -> List[str]:
    """Extract item IDs from a list of articles"""
    return [article['id'] for article in articles if article.get('id')]

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]