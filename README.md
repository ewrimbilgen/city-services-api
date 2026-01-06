
# City Services API Platform

A lightweight API platform that provides information about city services such as **libraries, parks, and health clinics**.  
This project demonstrates **API fundamentals**, **proper HTTP semantics**, **caching**, **real-time updates**, **GraphQL**, and a **clear versioning strategy**.

---

## 📌 Portfolio Project

This project was built as a **product-focused API design exercise** to demonstrate:
- REST API fundamentals and HTTP semantics
- Caching with ETag / 304 Not Modified
- Real-time updates using WebSockets
- Flexible querying with GraphQL
- API versioning and deprecation strategy

**Role:** Product Manager / API Designer  
**Scope:** API design, implementation, roadmap, documentation  

---

## 1. API Fundamentals

### Statelessness
The API is stateless:
- Each request contains all information needed to process it
- No server-side sessions are stored
- Any client can make any request independently

### Client–Server Model
- Client: web app, mobile app, or curl
- Server: City Services API
- Responsibilities are clearly separated

---

## 2. REST API Design

### Base URL
```

/api/v1

```

### Resource: Service
Example fields:
- `id`
- `type` (library, park, clinic)
- `name`
- `address`
- `hours`
- `updatedAt`

### Endpoints

| Method | Endpoint | Description | Status Codes |
|------|--------|------------|-------------|
| POST | `/api/v1/services` | Create service | 201, 400 |
| GET | `/api/v1/services` | List services | 200 |
| GET | `/api/v1/services/{id}` | Get service by ID | 200, 304, 404 |
| PUT | `/api/v1/services/{id}` | Replace service | 200, 400, 404 |
| PATCH | `/api/v1/services/{id}` | Update service | 200, 404 |
| DELETE | `/api/v1/services/{id}` | Delete service | 204, 404 |

---

## 3. HTTP Caching (ETag)

The API uses HTTP caching to improve performance.

### How it works
1. Server returns an `ETag` header
2. Client sends `If-None-Match`
3. Server returns `304 Not Modified` if unchanged

This avoids sending the same data repeatedly.

---

## 4. Real-Time Updates (WebSockets)

Polling is inefficient for real-time changes.

### WebSocket endpoint
```

ws://127.0.0.1:5000/ws

```

### Event
- `serviceCreated` — sent when a new service is created

---

## 5. GraphQL API

GraphQL is provided for flexible data retrieval.

### Endpoint
```

POST /graphql

````

### Example query
```graphql
{
  services {
    id
    name
    type
  }
}
````

---

## 6. REST vs SOAP vs GraphQL

| Feature      | REST        | SOAP              | GraphQL        |
| ------------ | ----------- | ----------------- | -------------- |
| Protocol     | HTTP        | XML / WS-*        | HTTP           |
| Flexibility  | Medium      | Low               | High           |
| Payload size | Fixed       | Large             | Client-defined |
| Typical use  | Public APIs | Legacy enterprise | Modern UIs     |

---

## 7. Versioning Strategy

Current version:

```
/api/v1
```

Rules:

* Backward-compatible changes stay in v1
* Breaking changes require `/api/v2`
* Old versions are deprecated gradually

---

## 8. Running Locally

```bash
python app.py
```

Server:

```
http://127.0.0.1:5000
```

---

## 9. curl Examples

Create service:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/services \
  -H "Content-Type: application/json" \
  -d '{"type":"library","name":"Central Library","address":"Main St 1"}'
```

List services:

```bash
curl http://127.0.0.1:5000/api/v1/services
```

GraphQL query:

```bash
curl -X POST http://127.0.0.1:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ services { id name } }"}'
```

---

## 10. Outcome

This project demonstrates:

* Correct REST and HTTP semantics
* Stateless API design
* Efficient caching
* Real-time updates
* Flexible GraphQL querying
* Scalable API versioning

```

---

