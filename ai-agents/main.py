#!/usr/bin/env python3
"""
BunkerBuster AI Agent Swarm - Main Entry Point

Coordinates distributed intelligence agents for:
- Real-time signal collection
- Pattern recognition & correlation
- Anomaly detection
- News aggregation
"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import agents
from agents.adsb_monitor import ADSBMonitor
from agents.news_aggregator import NewsAggregator
from agents.signal_processor import SignalProcessor
from agents.correlation_engine import CorrelationEngine

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BunkerBuster')

class AgentSwarm:
    """Coordinates all AI agents"""
    
    def __init__(self):
        self.agents = []
        self.running = False
    
    async def initialize(self):
        """Initialize all agents"""
        logger.info('🤖 Initializing AI Agent Swarm...')
        
        self.agents = [
            ADSBMonitor(),
            NewsAggregator(),
            SignalProcessor(),
            CorrelationEngine()
        ]
        
        for agent in self.agents:
            await agent.initialize()
            logger.info(f'✅ {agent.__class__.__name__} initialized')
    
    async def run(self):
        """Run all agents concurrently"""
        self.running = True
        logger.info('🚀 Starting Agent Swarm...')
        
        try:
            tasks = [agent.run() for agent in self.agents]
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info('⏸️  Agent Swarm interrupted')
            self.running = False
        except Exception as e:
            logger.error(f'❌ Agent Swarm error: {e}')
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        logger.info('🛑 Shutting down Agent Swarm...')
        
        for agent in self.agents:
            try:
                await agent.shutdown()
            except Exception as e:
                logger.error(f'Error shutting down {agent.__class__.__name__}: {e}')
        
        logger.info('✅ Agent Swarm shutdown complete')

async def main():
    """Main entry point"""
    swarm = AgentSwarm()
    
    try:
        await swarm.initialize()
        await swarm.run()
    except KeyboardInterrupt:
        logger.info('Shutting down...')
    finally:
        await swarm.shutdown()

if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════╗
║                                                    ║
║    🌍 BunkerBuster AI Agent Swarm                 ║
║    Tactical Geospatial Intelligence Platform      ║
║                                                    ║
║    Starting at: {datetime.now().isoformat()}      ║
║                                                    ║
╚════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
