#!/usr/bin/env python3
"""
Initialize BunkerBuster Database

Creates all necessary tables and indexes for the system
"""

import asyncpg
import asyncio
from config import config

async def init_database():
    """Create database schema"""
    
    # Connect to database
    conn = await asyncpg.connect(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        database=config.db.name
    )
    
    try:
        print("📊 Initializing database schema...")
        
        # Create extension if not exists
        await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE')
        print("✅ TimescaleDB extension enabled")
        
        # Aircraft positions hypertable
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS aircraft_positions (
            time TIMESTAMPTZ NOT NULL,
            icao_code VARCHAR(6) NOT NULL,
            callsign VARCHAR(10),
            latitude FLOAT,
            longitude FLOAT,
            altitude_ft INT,
            velocity_knots FLOAT,
            heading_degrees FLOAT,
            vertical_rate_fpm INT,
            squawk VARCHAR(4),
            aircraft_type VARCHAR(50),
            source VARCHAR(50)
        );
        
        SELECT create_hypertable('aircraft_positions', 'time', if_not_exists => TRUE);
        CREATE INDEX IF NOT EXISTS idx_aircraft_positions_icao_time 
            ON aircraft_positions (icao_code, time DESC)
            WHERE icao_code IS NOT NULL;
        ''')
        print("✅ Aircraft positions table created")
        
        # Satellites hypertable
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS satellite_positions (
            time TIMESTAMPTZ NOT NULL,
            satellite_id UUID NOT NULL,
            satellite_name VARCHAR(120),
            latitude FLOAT,
            longitude FLOAT,
            altitude_km FLOAT,
            velocity_ms FLOAT,
            heading_degrees FLOAT
        );
        
        SELECT create_hypertable('satellite_positions', 'time', if_not_exists => TRUE);
        CREATE INDEX IF NOT EXISTS idx_satellite_positions_id_time 
            ON satellite_positions (satellite_id, time DESC);
        ''')
        print("✅ Satellite positions table created")
        
        # Ships hypertable
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS ship_positions (
            time TIMESTAMPTZ NOT NULL,
            mmsi INT NOT NULL,
            ship_name VARCHAR(120),
            latitude FLOAT,
            longitude FLOAT,
            heading_degrees FLOAT,
            velocity_knots FLOAT,
            destination VARCHAR(120)
        );
        
        SELECT create_hypertable('ship_positions', 'time', if_not_exists => TRUE);
        CREATE INDEX IF NOT EXISTS idx_ship_positions_mmsi_time 
            ON ship_positions (mmsi, time DESC);
        ''')
        print("✅ Ship positions table created")
        
        # Areas of interest
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS areas_of_interest (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            radius_km FLOAT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        ) WITHOUT OIDS;
        ''')
        print("✅ Areas of Interest table created")
        
        # Events
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS events_4d (
            id UUID PRIMARY KEY,
            event_type VARCHAR(50),
            description TEXT,
            start_time TIMESTAMPTZ NOT NULL,
            end_time TIMESTAMPTZ,
            correlation_score FLOAT,
            aoi_id UUID,
            created_at TIMESTAMPTZ DEFAULT NOW()
        ) WITHOUT OIDS;
        
        CREATE INDEX IF NOT EXISTS idx_events_4d_time 
            ON events_4d (start_time DESC);
        ''')
        print("✅ Events 4D table created")
        
        print("\n✅ Database initialization complete!")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(init_database())
