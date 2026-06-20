# NCDC Tree Inventory API - Documentation

## Base URL

```
http://localhost:5000  (Development)
https://your-domain.com/api  (Production)
```

## Response Format

All responses are in JSON format.

## Error Handling

Errors return HTTP status codes with error messages:
- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

---

## Key Endpoints

### Trees Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trees` | Get all trees |
| GET | `/tree/<id>` | Get tree by ID |
| POST | `/tree` | Create new tree |
| PUT | `/tree/<id>` | Update tree |
| DELETE | `/tree/<id>` | Delete tree |

### Spatial Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trees/near?lat=&lon=&radius=` | Find trees within radius |
| GET | `/trees/freguesia/<name>` | Get trees by parish |
| GET | `/trees/species/<species>` | Get trees by species |

### Images & Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tree/<id>/images` | Get tree images |
| POST | `/tree/<id>/image` | Upload image |
| GET | `/tree-images/<path>` | Serve image |

### Comments & Maintenance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tree/<id>/comments` | Get comments |
| POST | `/tree/<id>/comment` | Add comment |
| GET | `/tree/<id>/maintenance` | Get maintenance history |
| POST | `/tree/<id>/maintenance` | Add maintenance record |

### Bulk Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bulk-import/json` | Import trees from JSON |
| POST | `/bulk-import/csv` | Import trees from CSV |

---

## Example Requests

### Get All Trees
```bash
curl http://localhost:5000/trees
```

### Get Trees Near Location
```bash
curl "http://localhost:5000/trees/near?lat=38.7223&lon=-9.1393&radius=500"
```

### Create Tree
```bash
curl -X POST http://localhost:5000/tree \
  -H "Content-Type: application/json" \
  -d '{
    "tree_id": 999,
    "nome_vulga": "Oak",
    "especie": "Quercus robur",
    "lat": 38.7223,
    "lon": -9.1393
  }'
```

### Upload Image
```bash
curl -F "image=@photo.jpg" http://localhost:5000/tree/1/image
```

---

## Performance

- Response time: < 500ms typical
- Spatial queries: < 1000ms
- Bulk import: ~5000 trees/minute
- Max concurrent connections: 200

---

**Last Updated**: 2026-06-20
