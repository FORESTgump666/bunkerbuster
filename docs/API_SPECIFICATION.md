# API Specification

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently token-based (JWT). Implement before production.

```bash
# Future endpoint
POST /auth/login
{
  "username": "user",
  "password": "pass"
}

# Returns
{
  "access_token": "eyJhbGc...",
  "expires_in": 86400
}
```

## Real-time Data (WebSocket)

Connect to `ws://localhost:5000` with Socket.io client.

### Aircraft Updates
```typescript
// Subscribe
socket.emit('aircraft:subscribe');

// Listen
socket.on('aircraft:update', (data: {
  batch: Aircraft[];
  count: number;
  timestamp: string;
}) => {
  // Handle aircraft update
});
```

### Satellite Updates
```typescript
socket.emit('satellites:subscribe');
socket.on('satellites:update', (data) => {
  // Handle satellite update
});
```

## REST Endpoints

### Satellites

```http
GET /api/satellites?since=2026-03-18T00:00:00Z

Response 200:
{
  "data": [
    {
      "time": "2026-03-18T14:23:45Z",
      "satellite_id": "550e8400-e29b-41d4-a716-446655440000",
      "satellite_name": "NORAD ID 25544",
      "latitude": 51.6435,
      "longitude": 80.4278,
      "altitude_km": 408,
      "velocity_ms": 7660,
      "heading_degrees": 89.5
    }
  ],
  "count": 1
}
```

```http
GET /api/satellites/{satellite_id}

Response 200:
{
  "data": [
    { /* historical positions */ }
  ]
}
```

```http
GET /api/satellites/{satellite_id}/coverage

Response 200:
{
  "data": {
    "center": { "lat": 51.6435, "lon": 80.4278 },
    "radius_km": 2400,
    "altitude_km": 408,
    "fov_half_angle_degrees": 22.5
  }
}
```

### Aircraft

```http
GET /api/aircraft?since=2026-03-18T14:00:00Z

Response 200:
{
  "data": [
    {
      "time": "2026-03-18T14:23:45Z",
      "icao_code": "123AB4",
      "callsign": "UAL2345",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "altitude_ft": 35000,
      "velocity_knots": 450,
      "heading_degrees": 180,
      "vertical_rate_fpm": 2000,
      "squawk": "1234",
      "aircraft_type": "B789",
      "source": "adsb-exchange"
    }
  ],
  "count": 50
}
```

```http
GET /api/aircraft/{icao_code}

Response 200:
{
  "data": [
    { /* track history */ }
  ]
}
```

### Ships

```http
GET /api/ships?since=2026-03-18T00:00:00Z

Response 200:
{
  "data": [
    {
      "time": "2026-03-18T14:23:45Z",
      "mmsi": 247320170,
      "ship_name": "CONTAINER SHIP NAME",
      "callsign": "SHIP",
      "latitude": 35.8617,
      "longitude": 139.0406,
      "heading_degrees": 90,
      "velocity_knots": 15,
      "navstat": 0,
      "draught": 12.5,
      "destination": "Tokyo",
      "flag": "JP"
    }
  ],
  "count": 123
}
```

```http
GET /api/ships/{mmsi}

Response 200:
{
  "data": [{ /* ship track history */ }]
}
```

### Jamming Indicators

```http
GET /api/jamming-indicators?since=2026-03-18T00:00:00Z

Response 200:
{
  "data": [
    {
      "time": "2026-03-18T14:23:45Z",
      "latitude": 50.1109,
      "longitude": 8.6821,
      "intensity_dbm": -80,
      "frequency_mhz": 1575.42,
      "region_name": "Eastern Europe",
      "confidence": 0.92,
      "duration_seconds": 300
    }
  ],
  "count": 5
}
```

### Events & 4D Reconstruction

```http
GET /api/events?limit=100&offset=0

Response 200:
{
  "data": [
    {
      "id": "event-uuid-123",
      "start_time": "2026-03-18T12:00:00Z",
      "end_time": "2026-03-18T12:30:00Z",
      "event_type": "convergence",
      "description": "Aircraft convoy detected near AOI-1",
      "participants": ["123AB4", "456CD7"],
      "aoi_id": "aoi-uuid-1",
      "correlation_score": 0.95,
      "data_snapshot": { /* full 4D state */ }
    }
  ],
  "count": 42
}
```

```http
GET /api/events/{id}

Response 200:
{
  "data": { /* single event */ }
}
```

### Areas of Interest (AOI)

```http
GET /api/aoi

Response 200:
{
  "data": [
    {
      "id": "aoi-uuid-1",
      "name": "Port Authority Zone",
      "description": "Strategic port area",
      "latitude": 35.8617,
      "longitude": 139.0406,
      "radius_km": 50,
      "is_active": true
    }
  ]
}
```

```http
POST /api/aoi

Request:
{
  "name": "New AOR",
  "latitude": 35.8617,
  "longitude": 139.0406,
  "radius_km": 100
}

Response 201:
{
  "data": { /* created AOI */ }
}
```

```http
GET /api/aoi/{id}/analytics

Response 200:
{
  "data": {
    "aircraft_passes": 42,
    "ships_detected": 15,
    "satellites_overhead": 7,
    "events_in_period": 3,
    "last_activity": "2026-03-18T14:20:00Z"
  }
}
```

## Error Responses

```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-03-18T14:23:45Z"
}
```

### Common Status Codes
- `200 OK` - Request succeeded
- `201 Created` - Resource created
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

- **WebSocket**: Unlimited
- **REST**: 100 requests per 15 minutes per IP
- **No authentication**: 10 requests per 15 minutes

```headers
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645017000
```

## Pagination

```http
GET /api/aircraft?limit=50&offset=100

# Returns items 100-150
```

## Timestamps

All timestamps in ISO 8601 format (UTC):
```
2026-03-18T14:23:45Z
```

---

**Last Updated**: March 2026
