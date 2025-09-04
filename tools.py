from typing import Optional, List, Dict
from inoreader_client import InoreaderClient
from utils import (
    parse_article, parse_feed, days_to_timestamp,
    format_article_list, format_feed_list, extract_item_ids,
    chunk_list
)
import asyncio
import logging

logger = logging.getLogger(__name__)

async def list_feeds_tool() -> str:
    """List all subscribed feeds"""
    try:
        async with InoreaderClient() as client:
            subscriptions = await client.get_subscription_list()
            feeds = [parse_feed(sub) for sub in subscriptions]
            
            if not feeds:
                return "No feeds found in your Inoreader account."
                
            # Sort by title
            feeds.sort(key=lambda x: x['title'].lower())
            
            result = f"Found {len(feeds)} feeds:\n\n"
            result += format_feed_list(feeds)
            
            return result
            
    except Exception as e:
        logger.error(f"Error listing feeds: {e}")
        return f"Error listing feeds: {str(e)}"

async def list_articles_tool(
    feed_id: Optional[str] = None,
    limit: int = 50,
    unread_only: bool = True,
    days: Optional[int] = None
) -> str:
    """List articles with optional filters"""
    try:
        logger.info(f"list_articles called with: feed_id={feed_id}, limit={limit}, unread_only={unread_only}, days={days}")
        
        async with InoreaderClient() as client:
            newer_than = days_to_timestamp(days) if days else None
            
            logger.info(f"Calling get_stream_contents with stream_id={feed_id}, newer_than={newer_than}")
            
            stream_contents = await client.get_stream_contents(
                stream_id=feed_id,
                count=limit,
                exclude_read=unread_only,
                newer_than=newer_than
            )
            
            logger.info(f"API response type: {type(stream_contents)}")
            
            # Handle both dict and string responses
            if isinstance(stream_contents, str):
                logger.error(f"Unexpected string response: {stream_contents[:200]}")
                return f"Error: API returned unexpected response format"
            
            items = stream_contents.get('items', [])
            logger.info(f"Found {len(items)} items from API")
            
            articles = [parse_article(item) for item in items]
            
            if not articles:
                filters = []
                if unread_only:
                    filters.append("unread")
                if days:
                    filters.append(f"from the last {days} days")
                if feed_id:
                    filters.append(f"in feed {feed_id}")
                    
                filter_str = " ".join(filters) if filters else ""
                return f"No articles found{' ' + filter_str if filter_str else ''}."
                
            result = f"Found {len(articles)} articles"
            if unread_only:
                result += " (unread only)"
            if days:
                result += f" from the last {days} days"
            result += ":\n\n"
            
            result += format_article_list(articles)
            
            return result
            
    except Exception as e:
        logger.error(f"Error listing articles: {e}", exc_info=True)
        return f"Error listing articles: {str(e)}"

async def get_content_tool(article_id: str) -> str:
    """Get full content of an article"""
    try:
        async with InoreaderClient() as client:
            # Get the full content
            result = await client.get_stream_item_contents([article_id])
            items = result.get('items', [])
            
            if not items:
                return f"Article with ID {article_id} not found."
                
            item = items[0]
            article = parse_article(item)
            
            # Build detailed content
            content = f"**{article['title']}**\n"
            content += f"Author: {article['author']}\n"
            content += f"Feed: {article['feed_title']}\n"
            content += f"Date: {article['published_date']}\n"
            
            if article['url']:
                content += f"URL: {article['url']}\n"
                
            content += f"Status: {'Read' if article['is_read'] else 'Unread'}\n"
            
            # Get full content if available
            if 'content' in item:
                full_content = item['content'].get('content', '')
                if full_content:
                    content += f"\n---\n\n{full_content}"
            elif article['summary']:
                content += f"\n---\n\n{article['summary']}"
            else:
                content += "\n---\n\nNo content available for this article."
                
            return content
            
    except Exception as e:
        logger.error(f"Error getting article content: {e}")
        return f"Error getting article content: {str(e)}"

async def mark_as_read_tool(article_ids: List[str]) -> str:
    """Mark articles as read"""
    try:
        if not article_ids:
            return "No article IDs provided."
            
        async with InoreaderClient() as client:
            # Process in chunks if needed
            chunks = chunk_list(article_ids, 20)
            success_count = 0
            
            for chunk in chunks:
                success = await client.mark_as_read(chunk)
                if success:
                    success_count += len(chunk)
                    
            if success_count == len(article_ids):
                return f"Successfully marked {success_count} article(s) as read."
            elif success_count > 0:
                return f"Marked {success_count} out of {len(article_ids)} articles as read."
            else:
                return "Failed to mark articles as read."
                
    except Exception as e:
        logger.error(f"Error marking articles as read: {e}")
        return f"Error marking articles as read: {str(e)}"

async def search_articles_tool(
    query: str,
    limit: int = 50,
    days: Optional[int] = None
) -> str:
    """Search for articles"""
    try:
        async with InoreaderClient() as client:
            newer_than = days_to_timestamp(days) if days else None
            
            result = await client.search(
                query=query,
                count=limit,
                newer_than=newer_than
            )
            
            items = result.get('items', [])
            articles = [parse_article(item) for item in items]
            
            if not articles:
                return f"No articles found matching '{query}'"
                
            response = f"Found {len(articles)} articles matching '{query}'"
            if days:
                response += f" from the last {days} days"
            response += ":\n\n"
            
            response += format_article_list(articles)
            
            return response
            
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        return f"Error searching articles: {str(e)}"

async def summarize_article_tool(article_id: str) -> str:
    """Generate a summary of an article"""
    try:
        # First get the article content
        content = await get_content_tool(article_id)
        
        if "not found" in content.lower() or "error" in content.lower():
            return content
            
        # Create a summary prompt
        lines = content.split('\n')
        title = lines[0].replace('**', '')
        
        # Extract the main content
        content_start = content.find('---')
        if content_start != -1:
            main_content = content[content_start + 3:].strip()
        else:
            main_content = content
            
        # Generate summary
        summary = f"**Summary of: {title}**\n\n"
        
        # Basic summarization logic (in production, this would use AI)
        sentences = main_content.replace('\n', ' ').split('. ')
        key_sentences = sentences[:3] if len(sentences) > 3 else sentences
        
        summary += "Key points:\n"
        for i, sentence in enumerate(key_sentences, 1):
            if sentence.strip():
                summary += f"{i}. {sentence.strip()}.\n"
                
        return summary
        
    except Exception as e:
        logger.error(f"Error summarizing article: {e}")
        return f"Error summarizing article: {str(e)}"

async def analyze_articles_tool(
    article_ids: List[str],
    analysis_type: str
) -> str:
    """Analyze multiple articles"""
    try:
        if not article_ids:
            return "No article IDs provided for analysis."
            
        async with InoreaderClient() as client:
            # Get full content for all articles
            result = await client.get_stream_item_contents(article_ids)
            items = result.get('items', [])
            
            if not items:
                return "No articles found for the provided IDs."
                
            articles = [parse_article(item) for item in items]
            
            # Perform analysis based on type
            if analysis_type == "summary":
                return await _analyze_summary(articles)
            elif analysis_type == "trends":
                return await _analyze_trends(articles)
            elif analysis_type == "sentiment":
                return await _analyze_sentiment(articles)
            elif analysis_type == "keywords":
                return await _analyze_keywords(articles)
            else:
                return f"Unknown analysis type: {analysis_type}"
                
    except Exception as e:
        logger.error(f"Error analyzing articles: {e}")
        return f"Error analyzing articles: {str(e)}"

async def _analyze_summary(articles: List[Dict]) -> str:
    """Generate a summary of multiple articles"""
    result = f"**Summary of {len(articles)} articles:**\n\n"
    
    for i, article in enumerate(articles[:5], 1):  # Limit to 5 for brevity
        result += f"{i}. **{article['title']}**\n"
        result += f"   - Feed: {article['feed_title']}\n"
        result += f"   - Date: {article['published_date']}\n"
        if article['summary']:
            summary_preview = article['summary'][:150] + "..." if len(article['summary']) > 150 else article['summary']
            result += f"   - Preview: {summary_preview}\n"
        result += "\n"
        
    return result

async def _analyze_trends(articles: List[Dict]) -> str:
    """Analyze trends in articles"""
    # Simple word frequency analysis
    word_freq = {}
    feeds_count = {}
    
    for article in articles:
        # Count feed frequency
        feed = article['feed_title']
        feeds_count[feed] = feeds_count.get(feed, 0) + 1
        
        # Count word frequency in titles
        words = article['title'].lower().split()
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
                
    # Get top trends
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    top_feeds = sorted(feeds_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    result = f"**Trend Analysis of {len(articles)} articles:**\n\n"
    
    result += "Top Keywords:\n"
    for word, count in top_words:
        result += f"- {word}: {count} occurrences\n"
        
    result += "\nMost Active Feeds:\n"
    for feed, count in top_feeds:
        result += f"- {feed}: {count} articles\n"
        
    return result

async def _analyze_sentiment(articles: List[Dict]) -> str:
    """Analyze sentiment of articles"""
    # Simple sentiment analysis based on keywords
    positive_words = {'good', 'great', 'excellent', 'positive', 'success', 'win', 'best', 'innovation', 'growth'}
    negative_words = {'bad', 'poor', 'negative', 'fail', 'loss', 'worst', 'crisis', 'problem', 'issue'}
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for article in articles:
        text = (article['title'] + ' ' + (article['summary'] or '')).lower()
        
        pos_score = sum(1 for word in positive_words if word in text)
        neg_score = sum(1 for word in negative_words if word in text)
        
        if pos_score > neg_score:
            positive_count += 1
        elif neg_score > pos_score:
            negative_count += 1
        else:
            neutral_count += 1
            
    result = f"**Sentiment Analysis of {len(articles)} articles:**\n\n"
    result += f"- Positive: {positive_count} ({positive_count/len(articles)*100:.1f}%)\n"
    result += f"- Negative: {negative_count} ({negative_count/len(articles)*100:.1f}%)\n"
    result += f"- Neutral: {neutral_count} ({neutral_count/len(articles)*100:.1f}%)\n"
    
    return result

async def _analyze_keywords(articles: List[Dict]) -> str:
    """Extract keywords from articles"""
    # Simple keyword extraction
    word_freq = {}
    
    for article in articles:
        text = (article['title'] + ' ' + (article['summary'] or '')).lower()
        words = text.split()
        
        for word in words:
            # Filter out common words and short words
            if len(word) > 4 and word not in {'their', 'there', 'which', 'would', 'could', 'should', 'about'}:
                word_freq[word] = word_freq.get(word, 0) + 1
                
    # Get top keywords
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
    
    result = f"**Top Keywords from {len(articles)} articles:**\n\n"
    for word, count in top_keywords:
        result += f"- {word}: {count} occurrences\n"
        
    return result

async def get_stats_tool() -> str:
    """Get statistics about unread articles"""
    try:
        async with InoreaderClient() as client:
            unread_counts = await client.get_unread_count()
            
            total_unread = 0
            feed_stats = []
            
            for item in unread_counts:
                count = item.get('count', 0)
                if count > 0 and item.get('id', '').startswith('feed/'):
                    total_unread += count
                    feed_stats.append({
                        'id': item['id'],
                        'count': count
                    })
                    
            result = f"**Inoreader Statistics:**\n\n"
            result += f"Total unread articles: {total_unread}\n\n"
            
            if feed_stats:
                # Sort by count
                feed_stats.sort(key=lambda x: x['count'], reverse=True)
                
                result += "Top feeds with unread articles:\n"
                for stat in feed_stats[:10]:  # Show top 10
                    feed_name = stat['id'].replace('feed/', '')
                    # Try to get a cleaner name
                    if '://' in feed_name:
                        feed_name = feed_name.split('://')[-1]
                    result += f"- {feed_name}: {stat['count']} unread\n"
                    
            return result
            
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return f"Error getting stats: {str(e)}"