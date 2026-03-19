"""
ADS-B Monitor Agent

Monitors aircraft positions from ADS-B Exchange
and publishes updates to Redis for global consumption.
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class ADSBMonitor:
    """Monitors ADS-B Exchange API for live aircraft tracking"""
    
    def __init__(self):
        self.adsb_url = 'https://api.adsb.one/api/aircraft'
        self.redis_client = None
        self.session = None
    
    async def initialize(self):
        """Setup connections"""
        self.redis_client = await redis.from_url('redis://localhost')
        self.session = aiohttp.ClientSession()
    
    async def run(self):
        """Continuously fetch and publish aircraft data"""
        logger.info('📡 ADS-B Monitor started')
        
        while True:
            try:
                async with self.session.get(self.adsb_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        aircraft_list = data.get('ac', [])
                        
                        # Format and publish
                        batch = []
                        for ac in aircraft_list[:500]:  # Limit batch size
                            batch.append({
                                'time': datetime.utcnow().isoformat() + 'Z',
                                'icao_code': ac.get('icao'),
                                'callsign': ac.get('flight', '').strip(),
                                'latitude': ac.get('lat'),
                                'longitude': ac.get('lon'),
                                'altitude_ft': ac.get('alt_baro'),
                                'velocity_knots': ac.get('gs'),
                                'heading_degrees': ac.get('track'),
                                'vertical_rate_fpm': ac.get('baro_rate'),
                                'squawk': ac.get('squawk'),
                                'aircraft_type': ac.get('type')
                            })
                        
                        await self.redis_client.publish(
                            'bunkerbuster:aircraft:updates',
                            json.dumps({'batch': batch, 'count': len(aircraft_list)})
                        )
                        
                        logger.info(f'✈️  Published {len(aircraft_list)} aircraft')
                    
                    await asyncio.sleep(10)  # Poll every 10 seconds
                    
            except asyncio.TimeoutError:
                logger.warning('ADS-B API timeout')
            except Exception as e:
                logger.error(f'ADS-B Monitor error: {e}')
                await asyncio.sleep(30)
    
    async def shutdown(self):
        """Cleanup"""
        if self.redis_client:
            await self.redis_client.close()
        if self.session:
            await self.session.close()
