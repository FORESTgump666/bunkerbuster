#!/usr/bin/env python3
"""
Utility scripts for system management
"""

import asyncio
import json
import redis.asyncio as redis
from datetime import datetime

async def check_system_health():
    """Check all system components"""
    print("🏥 System Health Check\n")
    
    # Check Redis
    try:
        r = await redis.from_url('redis://localhost')
        info = await r.info()
        print(f"✅ Redis: {info['redis_version']} (memory: {info['used_memory_human']})")
        await r.close()
    except Exception as e:
        print(f"❌ Redis: {e}")
    
    # Check database size
    import asyncpg
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/bunkerbuster')
        
        # Count records
        aircraft_count = await conn.fetchval('SELECT COUNT(*) FROM aircraft_positions')
        satellite_count = await conn.fetchval('SELECT COUNT(*) FROM satellite_positions')
        
        print(f"📊 Database:")
        print(f"   - Aircraft records: {aircraft_count:,}")
        print(f"   - Satellite records: {satellite_count:,}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Database: {e}")

async def clear_old_data(hours: int = 72):
    """Delete data older than N hours"""
    import asyncpg
    
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/bunkerbuster')
    
    cutoff_hours = hours
    before = await conn.fetchval(f"""
        DELETE FROM aircraft_positions 
        WHERE time < NOW() - INTERVAL '{cutoff_hours} hours'
    """)
    
    print(f"🗑️  Deleted aircraft records older than {cutoff_hours} hours")
    
    await conn.close()

async def export_snapshot(filename: str):
    """Export current state snapshot"""
    r = await redis.from_url('redis://localhost')
    
    snapshot = {
        'timestamp': datetime.utcnow().isoformat(),
        'aircraft': {},
        'satellites': {},
        'events': []
    }
    
    # Export from Redis
    keys = await r.keys('*')
    for key in keys[:100]:  # Limit snapshot size
        value = await r.get(key)
        snapshot['aircraft'][key] = json.loads(value) if value else None
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"💾 Exported snapshot to {filename}")
    await r.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'health':
            asyncio.run(check_system_health())
        elif command == 'clear':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 72
            asyncio.run(clear_old_data(hours))
        elif command == 'export':
            filename = sys.argv[2] if len(sys.argv) > 2 else 'snapshot.json'
            asyncio.run(export_snapshot(filename))
    else:
        print("""
Usage: utils.py <command> [args]

Commands:
  health          - Check system health
  clear [hours]   - Delete data older than N hours (default: 72)
  export [file]   - Export current snapshot (default: snapshot.json)
        """)
