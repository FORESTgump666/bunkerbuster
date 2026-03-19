# BunkerBuster: 4D Geospatial Intelligence Platform

A real-time, browser-based geospatial surveillance and analysis system that integrates multi-source signals into a unified 3D/4D global view.

## Core Capabilities

### 1. 4D Reconstruction
- Time-synced 3D reconstruction of global events
- Replay capability for historical and real-time maneuvers
- Timeline scrubbing with full state snapshots

### 2. Satellite Constellation Tracking
- Real-time tracking of commercial satellites (WorldView Legion, Gaofen-11, etc.)
- Defense satellite tracking via TLE (Two-Line Element) data
- Coverage footprint visualization
- Pass prediction and scheduling

### 3. Multi-Source Signal Integration
- **ADS-B**: Commercial and military aircraft tracking
- **AIS**: Maritime vessel monitoring
- **GPS Jamming**: Interference spike detection and visualization
- **Open-Source Intelligence**: Social media, news, sensor data aggregation

### 4. AI Agent Swarm
- Automated signal capture from distributed sources
- Cache-before-censorship intelligence collection
- Pattern recognition and anomaly detection
- Real-time alerts on breaking events

### 5. Line-of-Sight Analysis
- Automatic satellite coverage visualization
- Field-of-view (FOV) shadow detection
- Area of Interest (AOI) relationship mapping
- Electromagnetic propagation path analysis

### 6. Browser-Based Architecture
- Entirely web-deployed for crisis response
- No client installation required
- Real-time WebSocket data feeds
- Progressive enhancement for low-bandwidth environments

## Tech Stack

### Frontend
- **3D Engine**: Cesium.js (open-source geospatial visualization)
- **UI Framework**: React + TypeScript
- **State Management**: Redux for global state
- **Real-time**: WebSocket client for live data
- **Mapping**: Cesium Ion (free tier for basic layers)

### Backend
- **Runtime**: Node.js + Express
- **Database**: PostgreSQL (timeseries + spatial) + TimescaleDB extension
- **Cache**: Redis for real-time streaming
- **Real-time Protocol**: Socket.io for WebSocket management

### Data Sources (Tactical Mix)
- **Free/Open-Source**:
  - ADS-B Exchange (free aircraft data)
  - OpenSky Network (aircraft)
  - MarineTraffic (public vessel data)
  - CelesTrak (TLE satellite data)
  - NASA Worldview (satellite imagery layers)
  - NORAD Two-Line Elements

- **Acquired on Demand**:
  - Maxar API (WorldView satellite imagery)
  - FlightAware (premium military aircraft)
  - MarineTraffic premium (vessel AIS)
  - Cesium Ion premium tiles (photorealistic 3D)

### AI Agents
- **Framework**: Python with asyncio
- **LLM Integration**: OpenAI API / Open-source LLMs
- **Signal Processing**: NumPy, Pandas, scikit-learn
- **NLP**: Transformers library for news/social monitoring

## Project Structure

```
bunkerbuster/
├── frontend/                  # React + Cesium.js application
│   ├── src/
│   │   ├── components/       # React components (Globe, Timeline, etc.)
│   │   ├── services/         # API clients, WebSocket handlers
│   │   ├── store/            # Redux state management
│   │   └── utils/            # Helper functions
│   ├── package.json
│   └── public/
├── backend/                   # Node.js/Express API server
│   ├── src/
│   │   ├── api/              # REST endpoint handlers
│   │   ├── services/         # Business logic
│   │   ├── data-sources/     # Integrations (ADS-B, AIS, TLE)
│   │   ├── models/           # Database models
│   │   └── middleware/       # Auth, logging, etc.
│   ├── package.json
│   └── config/
├── ai-agents/                 # Python AI agent swarm
│   ├── agents/               # Individual agent implementations
│   ├── signal-processors/    # Signal & intelligence processing
│   ├── models/               # ML models for anomaly detection
│   └── requirements.txt
├── data-pipelines/           # Data ingestion & ETL
│   ├── collectors/           # Source-specific collectors
│   ├── processors/           # Real-time processors
│   ├── caches/               # Temporary signal storage
│   └── docker-compose.yml    # Docker stack orchestration
└── docs/
    ├── ARCHITECTURE.md
    ├── API_SPECIFICATION.md
    ├── DATA_SOURCES.md
    └── DEPLOYMENT.md
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 14+

### Development Setup

1. **Clone and setup**
   ```bash
   cd bunkerbuster
   npm install --prefix frontend
   npm install --prefix backend
   pip install -r ai-agents/requirements.txt
   ```

2. **Start development services**
   ```bash
   docker-compose up -d
   ```

3. **Run backend**
   ```bash
   npm run dev --prefix backend
   ```

4. **Run frontend**
   ```bash
   npm start --prefix frontend
   ```

5. **Start AI agents**
   ```bash
   python ai-agents/main.py
   ```

## Data Flow Architecture

```
External Data Sources
  ├─ ADS-B Exchange (Aircraft)
  ├─ MarineTraffic (Ships)
  ├─ NASA Worldview (Imagery)
  ├─ CelesTrak (TLE/Satellites)
  ├─ Social Media APIs
  └─ News Feeds
         ↓
   Backend Data Collectors
         ↓
   Redis Cache (Real-time)
   PostgreSQL (Persistent)
         ↓
   Data Processors & Enrichment
         ↓
   AI Agent Swarm
   (Pattern Recognition)
         ↓
   Cesium.js Frontend
   (3D Visualization)
```

## Feature Priorities

### Phase 1 (MVP)
- [ ] Basic Cesium.js globe with TLE satellite data
- [ ] ADS-B aircraft layer integration
- [ ] Timeline slider for historical replay
- [ ] WebSocket real-time data updates

### Phase 2
- [ ] AIS maritime layer
- [ ] Line-of-sight satellite coverage footprint
- [ ] GPS jamming indicator layer
- [ ] Basic AI agent signal collection

### Phase 3
- [ ] 4D reconstruction engine
- [ ] Advanced pattern recognition
- [ ] Full AI swarm deployment
- [ ] Production hardening

## Key Data Processing Challenges Solved

1. **Real-time Synchronization**: All timestamps UTC-synced with nanosecond precision
2. **Massive Data Ingestion**: Multi-source streams handled via Redis + TimescaleDB
3. **Line-of-Sight Computation**: GPU-accelerated via WebGL in Cesium
4. **Cache-Before-Censorship**: Distributed edge caching with local replay
5. **Cross-source Correlation**: AI-powered entity resolution across platforms

## Deployment Strategy

- **Development**: Local Docker stack
- **Staging**: Cloud-hosted (AWS/GCP)
- **Production**: Distributed CDN + edge nodes for crisis resilience
- **Offline Mode**: Downloaded data packages for field operations

## Security & Legal Considerations

- All data sources are publicly available or purchased commercially
- GDPR/privacy compliance for vessel and aircraft data
- Rate limiting to avoid overwhelming public data feeds
- Authentication via API keys + OAuth2
- Encryption in transit (TLS) and at rest

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

Proprietary - Internal Use Only

---

**Status**: Early Development  
**Last Updated**: March 2026
