"""
Correlation Engine Agent

Correlates data from multiple sources to identify
related events and create 4D reconstructions.
"""

import asyncio
import logging
import json
import redis.asyncio as redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """Correlates and reconstructs events"""
    
    def __init__(self):
        self.redis_client = None
        self.event_buffer = []
    
    async def initialize(self):
        """Setup connections"""
        self.redis_client = await redis.from_url('redis://localhost')
    
    async def run(self):
        """Listen to all events and correlate"""
        logger.info('🔗 Correlation Engine started')
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(
            'bunkerbuster:aircraft:updates',
            'bunkerbuster:ships:updates',
            'bunkerbuster:satellites:updates',
            'bunkerbuster:events:new',
            'bunkerbuster:anomalies'
        )
        
        while True:
            try:
                message = await pubsub.get_message(timeout=5)
                
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Add to event buffer
                    self.event_buffer.append({
                        'channel': message.get('channel'),
                        'data': data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    # Correlate every N events
                    if len(self.event_buffer) > 100:
                        await self.correlate_events()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f'Correlation Engine error: {e}')
    
    async def correlate_events(self):
        """Correlate events in buffer"""
        # Remove old events (older than 5 minutes)
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        self.event_buffer = [
            e for e in self.event_buffer
            if datetime.fromisoformat(e['timestamp']) > cutoff
        ]
        
        # Find correlated events
        correlations = await self.find_correlations()
        
        # Publish reconstructions
        for correlation in correlations:
            await self.redis_client.publish(
                'bunkerbuster:4d-reconstructions',
                json.dumps(correlation)
            )
        
        logger.info(f'🔗 Found {len(correlations)} correlated events')
    
    async def find_correlations(self):
        """Find related events"""
        correlations = []
        
        # Group events by area/time
        for i, event1 in enumerate(self.event_buffer):
            for event2 in self.event_buffer[i+1:]:
                if self.are_correlated(event1, event2):
                    correlations.append({
                        'events': [event1, event2],
                        'correlation_score': 0.85,
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return correlations
    
    def are_correlated(self, event1, event2):
        """Check if two events are spatially/temporally correlated"""
        # Simplified: just check if within 10 minutes
        t1 = datetime.fromisoformat(event1['timestamp'])
        t2 = datetime.fromisoformat(event2['timestamp'])
        
        time_diff = abs((t2 - t1).total_seconds())
        return time_diff < 600  # 10 minutes
    
    async def shutdown(self):
        """Cleanup"""
        if self.redis_client:
            await self.redis_client.close()
