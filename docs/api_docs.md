# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: Configure via environment

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### POST /auth/signup
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-11-24T05:00:00Z"
}
```

### POST /auth/login
Authenticate and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /auth/reset-password
Request password reset token.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

### POST /auth/reset-password/confirm
Reset password using token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "newsecurepassword123"
}
```

## Assessments

### GET /assessments/questionnaires
Get all questionnaire templates (no auth required).

**Response (200):**
```json
[
  {
    "category": "data_privacy",
    "title": "Data Privacy Assessment",
    "description": "Evaluate data handling...",
    "questions": [...]
  }
]
```

### POST /assessments
Create a new assessment (requires auth).

**Request Body:**
```json
{
  "title": "Q4 2024 Assessment",
  "description": "Optional description"
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Q4 2024 Assessment",
  "status": "draft",
  "created_at": "2024-11-24T05:00:00Z"
}
```

### GET /assessments
List all assessments for current user (requires auth).

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Q4 2024 Assessment",
    "status": "in_progress",
    "results": [...]
  }
]
```

### GET /assessments/{id}
Get assessment details (requires auth).

### POST /assessments/{id}/answers
Submit answers for a category (requires auth).

**Request Body:**
```json
{
  "category": "data_privacy",
  "answers": {
    "dp_1": 10,
    "dp_2": 5,
    "dp_3": 15
  }
}
```

**Response (200):**
```json
{
  "id": 1,
  "category": "data_privacy",
  "score": 92,
  "maturity_level": "optimized",
  "recommendations": "..."
}
```

### GET /assessments/{id}/summary
Get assessment summary with overall score (requires auth).

**Response (200):**
```json
{
  "assessment": {...},
  "overall_score": 85,
  "overall_maturity": "managed",
  "category_scores": {
    "data_privacy": 92,
    "model_risk": 78
  }
}
```

### GET /assessments/{id}/export/csv
Export assessment as CSV (requires auth).

Returns CSV file download.

### GET /assessments/{id}/export/pdf
Export assessment as PDF (requires auth).

Returns PDF file download.

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Validation error message"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate-limited to 60 requests per minute per IP address. Exceeding this limit will result in a 429 Too Many Requests response.
