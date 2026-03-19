# BunkerBuster Architecture & Design Decisions

## System Overview

BunkerBuster is a distributed, event-driven architecture designed for real-time geospatial intelligence collection and visualization.

```
┌────────────────────────────────────────────────────────────────┐
│                       BROWSER (Cesium.js)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3D Globe Visualization                                   │  │
│  │ - Satellite positions & coverage footprints             │  │
│  │ - Aircraft trails (ADS-B)                              │  │
│  │ - Ship tracks (AIS)                                     │  │
│  │ - GPS interference heat map                             │  │
│  │ - Timeline replay scrubber                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  WebSocket (Socket.io)                                         │
└────────────────────────────────────────────────────────────────┘
                           ↑↓
┌────────────────────────────────────────────────────────────────┐
│                    NODE.JS BACKEND API                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ REST API Endpoints                                       │  │
│  │ - GET /satellites - Current satellite positions        │  │
│  │ - GET /aircraft - Active aircraft                      │  │
│  │ - GET /ships - Active vessels                          │  │
│  │ - GET /events - Reconstructed 4D events               │  │
│  │ - GET /los-analysis - Line of sight data               │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ WebSocket Event Streaming                               │  │
│  │ - Real-time position updates                            │  │
│  │ - Jamming spike alerts                                  │  │
│  │ - Breaking event notifications                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
       ↑↓                           ↑↓                       ↑↓
┌──────────────────┐  ┌────────────────────────┐  ┌──────────────────┐
│   Redis Cache    │  │   PostgreSQL + TS DB   │  │   File Storage   │
│ (Real-time data) │  │  (Historic events)     │  │  (Replay data)   │
└──────────────────┘  └────────────────────────┘  └──────────────────┘
       ↑↓
┌────────────────────────────────────────────────────────────────┐
│              DATA COLLECTION LAYER (Python)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ ADS-B Parser │  │ AIS Decoder  │  │ TLE Updater  │ ...     │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ AI Agent Swarm (Real-time Signal Processing)           │   │
│  │ - News aggregators                                      │   │
│  │ - Social media monitors                                 │   │
│  │ - Anomaly detectors                                     │   │
│  │ - Correlation engines                                   │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
       ↑↓                    ↑↓                       ↑↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ ADS-B Exchange   │  │ MarineTraffic    │  │ CelesTrak TLE    │
│ (Aircraft)       │  │ (Maritime AIS)   │  │ (Satellites)     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
       ...More Sources (NASA, News APIs, Twitter, etc.)
```

## Core Components

### 1. Frontend: Cesium.js 3D Visualization Engine

**File**: `frontend/src/App.tsx`

Features:
- **Globe Rendering**: Cesium's WebGLTiledMapImageryProvider
- **Entity Layers**: Dynamic primitive collections for satellites, aircraft, ships
- **Timeline Widget**: Cesium's Timeline for 4D replay
- **Camera Control**: Orbital mechanics-aware camera system
- **Performance**: Entity clustering for 10k+ objects

**Key Libraries**:
```json
{
  "cesium": "^1.120.0",
  "react": "^18.2.0",
  "react-cesium": "^1.0.0",
  "zustand": "^4.4.0"
}
```

### 2. Backend API Server

**Stack**: Express.js + TypeScript

**API Routes**:
```
POST   /api/auth/login             - Authenticate user
GET    /api/satellites             - Current satellite ephemeris
GET    /api/satellites/:id/coverage - FOV coverage polygon
GET    /api/aircraft               - ADS-B aircraft positions
GET    /api/ships                  - AIS vessel positions
GET    /api/events                 - 4D reconstructed events
GET    /api/events/:id/replay      - Time-series for event
GET    /api/jamming-indicators     - GPS interference data
GET    /api/los-analysis           - Line-of-sight rays
POST   /api/aoi                    - Create Area of Interest
GET    /api/aoi/:id/analytics      - AOI event analytics
WS     /ws                         - WebSocket upgrade
```

### 3. Real-Time Data Pipeline

**Architecture**: Event-driven with Redis pub/sub

**Flow**:
1. **Collection**: Python collectors fetch raw data from APIs
2. **Normalization**: Convert to common schema (timestamp, lat, lon, heading, etc.)
3. **Enrichment**: Add metadata (aircraft type, business rules checks)
4. **Redis Queue**: Publish to topic-specific channels
5. **Backend Consumer**: Node.js subscribes and rebroadcasts to WebSocket clients
6. **Persistence**: Store in TimescaleDB for historical queries

**Example Topic Structure**:
```redis
bunkerbuster:aircraft:updates    -> Position updates
bunkerbuster:ships:updates       -> AIS messages
bunkerbuster:satellites:updates  -> Ephemeris updates
bunkerbuster:jamming:alerts      -> GPS interference spikes
bunkerbuster:events:new          -> New 4D events detected
```

### 4. Satellite Ephemeris & Line-of-Sight

**Engine**: Custom WebGL-accelerated raycaster

**Algorithm**:
```
For each satellite at time T:
  1. Compute position (SGP4 propagation from TLE)
  2. Calculate FOV cone (nadir angle = 45-60° depending on satellite)
  3. Ray-march Earth surface to find illuminated footprint
  4. Check line-of-sight to Area of Interest
  5. If LOS exists, create connection primitive
```

**Performance**: GPU-accelerated, updates every 1-5 seconds

### 5. AI Agent Swarm

**Architecture**: Microservices pattern with message queue

**Agents**:
1. **News Aggregator**: Monitors RSS feeds, extracts coordinates
2. **Social Monitor**: Tracks Twitter/Telegram for eyewitness reports
3. **Signal Detector**: Analyzes ADS-B/AIS for anomalies
4. **Correlation Engine**: Cross-references events across sources
5. **Prediction Agent**: Forecasts satellite passes and aircraft movements

**Deployment**: Kubernetes or Docker Swarm with auto-scaling

### 6. 4D Reconstruction Engine

**Key Concept**: Time-synced snapshots of global state

**Process**:
1. **Ingestion**: All events tagged with UTC timestamp (nanosecond precision)
2. **Bucketing**: Group events into 1-second buckets
3. **Deduplication**: Merge duplicate updates from multiple sources
4. **State Snapshot**: Serialize full world state every 5 seconds
5. **Timeline Index**: Create searchable index by timestamp
6. **Playback**: Client scrubs timeline, backend retrieves snapshots

**Storage Strategy**: 
- Last 72 hours: Redis (fast playback)
- Older: PostgreSQL (query-efficient with retention policy)

## Data Models

### TimescaleDB Hypertable Schemas

```sql
-- Satellite positions (auto-bucketing)
CREATE TABLE satellite_positions (
  time TIMESTAMPTZ NOT NULL,
  satellite_id UUID NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  altitude_km FLOAT NOT NULL,
  velocity_ms FLOAT NOT NULL,
  heading_degrees FLOAT NOT NULL
);
SELECT create_hypertable('satellite_positions', 'time', 
  if_not_exists => TRUE);

-- Aircraft ADS-B messages
CREATE TABLE aircraft_positions (
  time TIMESTAMPTZ NOT NULL,
  icao_code VARCHAR(6) NOT NULL,
  callsign VARCHAR(10),
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  altitude_ft INT,
  velocity_knots FLOAT,
  heading_degrees FLOAT,
  vertical_rate_fpm INT,
  squawk VARCHAR(4)
);
SELECT create_hypertable('aircraft_positions', 'time', 
  if_not_exists => TRUE);

-- Ship AIS messages
CREATE TABLE ship_positions (
  time TIMESTAMPTZ NOT NULL,
  mmsi INT NOT NULL,
  ship_name VARCHAR(120),
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  heading_degrees FLOAT,
  velocity_knots FLOAT,
  draught FLOAT,
  destination VARCHAR(120)
);
SELECT create_hypertable('ship_positions', 'time', 
  if_not_exists => TRUE);

-- GPS jamming indicators
CREATE TABLE jamming_indicators (
  time TIMESTAMPTZ NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  intensity_dbm INT,
  frequency_mhz FLOAT,
  region_name VARCHAR(100)
);
SELECT create_hypertable('jamming_indicators', 'time', 
  if_not_exists => TRUE);

-- 4D Events reconstructions
CREATE TABLE events_4d (
  id UUID PRIMARY KEY,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ,
  event_type VARCHAR(50),
  description TEXT,
  participants JSONB,  -- Array of entity IDs involved
  aoi_id UUID,         -- Area of Interest involved
  correlation_score FLOAT,
  data_snapshot JSONB  -- Full state at event time
);
```

## Real-Time Data Flow Example: Aircraft Tracking

```
1. ADS-B Collector (Python)
   └─ Query: curl https://api.adsb.one/api/aircraft
   └─ Parse: Extract ICAO, lat, lon, heading
   └─ Format: {time: 2026-03-18T14:23:45Z, icao: '123AB4', ...}
   └─ Publish: Redis channel 'bunkerbuster:aircraft:updates'

2. Backend WebSocket Handler (Node.js)
   └─ Subscribe: socket.on('redis:aircraft:updates')
   └─ Store: db.insert('aircraft_positions', data)
   └─ Broadcast: socket.emit('aircraft:position', data)

3. Frontend Cesium Entity
   └─ Listen: websocket.on('aircraft:position')
   └─ Update: entity.position = Cesium.Cartesian3.fromDegrees(...)
   └─ Trail: Add entity to polyline path
   └─ Render: WebGL batch-renders all aircraft

4. UI Sidebar (React)
   └─ Display: "5,432 active aircraft"
   └─ Update: Every message increments counter
```

## Performance Optimization Strategies

### Frontend
- **Entity Pooling**: Reuse Cesium entities instead of recreating
- **Primitive Batching**: Group similar geometries into single batch
- **LOD (Level of Detail)**: Hide entity trails when zoomed out
- **Canvas Clipping**: Only render visible viewport

### Backend
- **Connection Pooling**: PostgreSQL connection pool size = 20
- **Index Strategy**: `CREATE INDEX ON aircraft_positions (time DESC)`
- **Partition Strategy**: Monthly table partitions for old data
- **Caching**: Redis for frequent queries (past 1 hour)

### Data Collection
- **Rate Limiting**: Poll external APIs every 5-30 seconds (not 1/sec)
- **Batching**: Accumulate 100 messages before publishing
- **Compression**: Protocol buffers for Redis serialization

## Failure & Recovery

- **API Downtime**: Fall back to cached data, show staleness warning
- **Database Loss**: Redis replicas + PostgreSQL backup every 30 min
- **WebSocket Disconnect**: Auto-reconnect with exponential backoff
- **Satellite Prediction Errors**: Use multiple TLE sources, vote on consensus

## Scaling Strategy

### Vertical (Single Machine)
- Max ~20k object entities at 30 FPS
- PostgreSQL handles 10k writes/sec

### Horizontal (Multiple Servers)
- Load balance frontend via Nginx
- Redis Cluster for cache sharding
- PostgreSQL read replicas
- Separate microservices for AI agents

## Cost Model (Free Tier Prioritized)

| Component | Free Option | Tactical Upgrade |
|-----------|-------------|------------------|
| 3D Tiles | Cesium Ion (free) | OpenStreetMap + Mapbox (pay-as-you-go) |
| Aircraft | ADS-B Exchange | FlightAware Enterprise |
| Maritime | MarineTraffic | Premium AIS feed |
| Satellites | CelesTrak TLE | Space-Track.org tokens|
| Imagery | NASA Worldview | Maxar API (per-request) |
| Hosting | Docker local/AWS free | AWS EC2 Reserved (production) |

---

**Last Updated**: March 2026
