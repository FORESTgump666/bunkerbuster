"""
News Aggregator Agent

Monitors news feeds and social media for geolocation
intelligence and publishes structured events.
"""

import asyncio
import feedparser
import logging
import json
from datetime import datetime
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class NewsAggregator:
    """Aggregates news from multiple sources"""
    
    def __init__(self):
        self.redis_client = None
        self.news_sources = [
            'http://feeds.reuters.com/reuters/topNews',
            'http://feeds.bbc.co.uk/news/rss.xml',
            'http://feeds.cnn.com/rss/edition.rss'
        ]
    
    async def initialize(self):
        """Setup connections"""
        self.redis_client = await redis.from_url('redis://localhost')
    
    async def run(self):
        """Continuously monitor news feeds"""
        logger.info('📰 News Aggregator started')
        
        while True:
            try:
                for source in self.news_sources:
                    feed = feedparser.parse(source)
                    
                    for entry in feed.entries[:10]:
                        # Parse entry for geolocation
                        event = {
                            'time': datetime.utcnow().isoformat() + 'Z',
                            'source': source,
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', '')[:200],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', '')
                        }
                        
                        # Publish event
                        await self.redis_client.publish(
                            'bunkerbuster:events:new',
                            json.dumps(event)
                        )
                    
                    logger.info(f'📰 Processed feed: {source}')
                
                # Aggregate every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f'News Aggregator error: {e}')
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Cleanup"""
        if self.redis_client:
            await self.redis_client.close()
