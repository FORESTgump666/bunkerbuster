"""
Signal Processor Agent

Processes raw signals for anomalies, pattern recognition,
and data enrichment.
"""

import asyncio
import logging
import json
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class SignalProcessor:
    """Processes and enriches signals"""
    
    def __init__(self):
        self.redis_client = None
    
    async def initialize(self):
        """Setup connections"""
        self.redis_client = await redis.from_url('redis://localhost')
        self.pubsub = self.redis_client.pubsub()
    
    async def run(self):
        """Listen to signals and process them"""
        logger.info('⚙️  Signal Processor started')
        
        await self.pubsub.subscribe('bunkerbuster:aircraft:updates')
        
        while True:
            try:
                message = await self.pubsub.get_message(timeout=5)
                
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Process aircraft batch
                    if 'batch' in data:
                        processed = await self.process_aircraft(data['batch'])
                        logger.info(f'⚙️  Processed {len(processed)} aircraft')
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f'Signal Processor error: {e}')
    
    async def process_aircraft(self, batch):
        """Enrich aircraft data"""
        processed = []
        
        for ac in batch:
            # Detect anomalies
            anomaly_score = self.detect_anomalies(ac)
            
            # Enrich with metadata
            enriched = {
                **ac,
                'anomaly_score': anomaly_score,
                'processed_at': json.dumps({}).split('"')[0]  # Current ISO time
            }
            
            # Publish if anomalous
            if anomaly_score > 0.5:
                await self.redis_client.publish(
                    'bunkerbuster:anomalies',
                    json.dumps(enriched)
                )
            
            processed.append(enriched)
        
        return processed
    
    def detect_anomalies(self, aircraft):
        """Simple anomaly detection"""
        score = 0.0
        
        # High altitude anomaly
        if aircraft.get('altitude_ft', 0) > 45000:
            score += 0.3
        
        # Rapid altitude change
        if abs(aircraft.get('vertical_rate_fpm', 0)) > 5000:
            score += 0.2
        
        # Unusual heading changes
        if aircraft.get('heading_degrees') is not None:
            score += 0.1
        
        return min(score, 1.0)
    
    async def shutdown(self):
        """Cleanup"""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
