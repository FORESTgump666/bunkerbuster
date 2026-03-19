# Data Sources & Intelligence Integration

This document outlines all data sources for BunkerBuster and how to integrate with them.

## Free/Open-Source Intelligence Feeds

### 1. ADS-B Exchange (Aircraft Tracking)
- **URL**: https://api.adsb.one
- **Cost**: FREE (rates limited)
- **Data**: Real-time civil aviation, ADS-B transponder data
- **Update Frequency**: 5-10 seconds
- **Coverage**: Global
- **API Rate**: ~1000 requests/day recommended
- **Integration**: Already implemented in `backend/src/services/data-collectors/index.ts`

**Example Data**:
```json
{
  "icao": "123AB4",
  "flight": "UAL2345",
  "lat": 40.7128,
  "lon": -74.0060,
  "alt_baro": 35000,
  "gs": 450,
  "track": 180,
  "baro_rate": 2000
}
```

### 2. CelesTrak TLE Data (Satellite Tracking)
- **URL**: https://celestrak.org
- **Cost**: FREE
- **Data**: Two-Line Element sets for active satellites
- **Update Frequency**: 3-5 hours
- **Coverage**: 4000+ active satellites
- **Integration**: Parser in `backend/src/services/data-collectors/index.ts`

**Available Groups**:
- `active.txt` - All active satellites
- `resource.txt` - Resource observation satellites
- `deb.txt` - Debris objects
- `cubesat.txt` - Cubesats
- `military.txt` - Military satellites (estimate)

### 3. OpenSky Network (Aviation)
- **URL**: https://opensky-network.org
- **Cost**: FREE (with registration) or PAID for commercial
- **Data**: ADS-B and MLAT data
- **Update Frequency**: Real-time
- **Coverage**: Global
- **Rate Limit**: 4000 requests/hour (free tier)

**Registration & API**:
```bash
curl -u "username:password" https://opensky-api.org/api/states/all
```

### 4. Harvard Dataverse - Maritime AIS
- **URL**: https://dataverse.harvard.edu
- **Cost**: FREE
- **Data**: Historical and current AIS vessel data
- **Update Frequency**: Variable
- **Integration Point**: For historical ship movement analysis

### 5. NASA Worldview (Satellite Imagery)
- **URL**: https://worldview.earthdata.nasa.gov
- **Cost**: FREE
- **Data**: 900+ satellite imagery layers updated daily
- **Coverage**: Global, multiple wavelengths
- **API**: GIBS (Global Imagery Browse Services)

**Integration Example**:
```typescript
// Add to Cesium viewer
const layer = new Cesium.ImageryLayer(
  new Cesium.BingMapsImageryProvider({
    url: 'https://dev.virtualearth.net',
    key: 'YOUR_BING_KEY'
  })
);
viewer.imageryLayers.add(layer);
```

### 6. NORAD Two-Line Elements
- **URL**: https://celestrak.org/NORAD/elements/
- **Cost**: FREE
- **Data**: Military satellite TLE updates
- **Update Frequency**: Hourly
- **Coverage**: Defense satellites

## Commercial Data Sources (Tactical Acquisition)

### 1. MaxarTechnologies (WorldView Satellites)
- **URL**: https://www.maxar.com
- **Cost**: Per-request pricing, ~$2-5 USD per image
- **Data**: High-resolution satellite imagery (0.3m resolution)
- **Coverage**: Custom tasking, rapid point capture
- **When to Use**: High-priority AOI with time-critical imagery needs

### 2. FlightAware (Military Aircraft)
- **URL**: https://commercial.flightaware.com
- **Cost**: $150-500/month enterprise
- **Data**: Military aircraft transponder data (more complete than free sources)
- **Coverage**: Includes ICAO military registries
- **When to Use**: When tracking specific military assets

### 3. MarineTraffic Premium AIS
- **URL**: https://www.marinetraffic.com
- **Cost**: $99-499/month
- **Data**: Real-time and historical vessel AIS
- **Coverage**: Complete global maritime picture
- **When to Use**: Priority maritime intelligence tasks

### 4. Cesium Ion Premium Tiles
- **URL**: https://cesium.com/platform/cesium-ion/
- **Cost**: Free tier + $49-499/month for premium
- **Data**: Photorealistic 3D world tiles from satellite imagery
- **Coverage**: Global
- **When to Use**: High-fidelity 3D scene reconstruction

### 5. Google Maps Platform
- **URL**: https://cloud.google.com/maps-platform
- **Cost**: $7 USD per 1000 map loads
- **Data**: High-quality base maps, 3D Photorealistic Tiles
- **When to Use**: Alternative to Cesium tiles

## GPS Jamming Detection

### Free Approaches
1. **Crowdsourced Data**: Monitor civil aviation reports of GPS outages
2. **RTK Network Analysis**: Connect to public RTK GNSS networks
3. **Mobile Signal Monitoring**: Use open-source tools like GNURadio

### Paid Integrations
1. **GSA European GNSS Service**: €10k+/year
2. **Electromagnetic Surveillance APIs**: $5k-50k/month

## Social Media / OSINT Integration

### Twitter/X API
```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Search for geolocated tweets
tweets = client.search_recent_tweets(
    query="location:lat,lon -is:retweet",
    tweet_fields=['created_at', 'geo']
)
```
- **Cost**: FREE tier (450 requests/15 min)
- **When to Use**: Real-time event detection

### Telegram Monitoring
- Various open-source bots can monitor public channels
- Cost: FREE
- Use: Breaking crisis detection

### Reddit Data
- Push Shift Archive: Deprecated, use alternative scraping
- Cost: FREE
- Use: Historical event analysis

## Integration Pattern

All data sources follow this pipeline:

```
Raw API/Feed
    ↓
Python Collector (agents/) - Rate limited, batched
    ↓
Redis Pub/Sub Channel: "bunkerbuster:SOURCE:updates"
    ↓
Node.js Backend Consumer
    ↓
PostgreSQL TimescaleDB (Historical)
    ↓
WebSocket → Cesium Frontend
```

### Adding a New Data Source

1. Create collector in `ai-agents/agents/`:
```python
# ai-agents/agents/my_new_source.py
class MySourceMonitor:
    async def run(self):
        # Fetch data
        data = await fetch_data()
        # Publish to Redis
        await self.redis_client.publish(
            'bunkerbuster:my_source:updates',
            json.dumps(formatted_data)
        )
```

2. Register in `ai-agents/main.py`:
```python
self.agents = [
    ADSBMonitor(),
    MySourceMonitor(),  # Add here
    # ...
]
```

3. Subscribe in backend `backend/src/services/websocket.ts`:
```typescript
socket.on('my_source:subscribe', async () => {
    const subscriber = redis.duplicate();
    await subscriber.connect();
    await subscriber.subscribe('bunkerbuster:my_source:updates', (msg) => {
        socket.emit('my_source:update', JSON.parse(msg));
    });
});
```

## Rate Limiting & Cost Optimization

- Poll free APIs every 30+ seconds (not per-second)
- Batch updates: accumulate 100+ records before publishing
- Implement local caching with TTL
- Use webhooks instead of polling when available
- Monitor API quota/cost dashboard daily
- Set up alerts for unexpected API usage

## Authentication & Secrets

All API keys stored in `.env`:
```bash
ADSB_API_KEY=
AIS_API_KEY=
NASA_API_KEY=your-nasa-api-key
MAXAR_API_KEY=
SPACE_TRACK_USERNAME=
SPACE_TRACK_PASSWORD=
```

Never commit `.env` to version control. Copy `.env.example` to `.env` locally.

---

**Last Updated**: March 2026
