# EVE Healthcare Booking API

A small FastAPI backend for diagnostic centre test bookings and simulated payments. It uses PostgreSQL for the application database and JWT bearer tokens for protected endpoints.

## Features

- User signup and login with JWT authentication
- Diagnostic centres and the tests and prices each centre offers
- Authenticated test bookings
- Mock payment results: `SUCCESS` or `FAILED`
- Payment webhook with idempotent event handling
- Booking ownership checks
- Request validation and focused API tests

Optional assignment features such as Docker, Redis, background jobs, and rate limiting are not included.

## Requirements

- Python 3.10 or later
- PostgreSQL
- Windows PowerShell, macOS Terminal, or Linux shell

## Run locally

### 1. Create the PostgreSQL database

Start PostgreSQL and create a database named `eve_healthcare`. You can create it using pgAdmin or with the PostgreSQL command line:

```bash
createdb -U postgres eve_healthcare
```

### 2. Create a virtual environment and install dependencies

From the project folder:

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS or Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

### 3. Configure the environment

Copy `.env.example` to `.env`, then set your PostgreSQL password and a private JWT secret.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/eve_healthcare
JWT_SECRET=replace-this-with-a-long-random-secret
```

If your PostgreSQL password contains URL-reserved characters, encode them in the database URL.

### 4. Start the API

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**macOS or Linux**

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and call the endpoints through Swagger UI.

The application creates tables from the SQLAlchemy models when it starts. Alembic migrations are not included. If the schema changes during development, the local database may need to be recreated.

## API endpoints

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| `POST` | `/auth/signup` | No | Register a user |
| `POST` | `/auth/login` | No | Log in and receive a JWT |
| `POST` | `/centres` | Yes | Create a diagnostic centre |
| `GET` | `/centres` | No | List diagnostic centres |
| `POST` | `/centres/{centre_id}/tests` | Yes | Add a test and price offered by a centre |
| `GET` | `/centres/{centre_id}/tests` | No | List a centre’s tests and prices |
| `POST` | `/bookings` | Yes | Book a centre’s test |
| `GET` | `/bookings/{booking_id}` | Yes | Retrieve your own booking |
| `POST` | `/payments` | Yes | Simulate a payment for your booking |
| `POST` | `/payments/webhook` | No | Receive a simulated provider payment event |

For protected endpoints, log in and use the returned `access_token`. In Swagger UI, click **Authorize** and enter the token.

### Signup and login

Create a user:

```http
POST /auth/signup
Content-Type: application/json

{
  "name": "Asha Patient",
  "email": "asha@example.com",
  "password": "password123"
}
```

Log in:

```http
POST /auth/login
Content-Type: application/json

{
  "email": "asha@example.com",
  "password": "password123"
}
```

The login response contains an `access_token`. Send it to protected endpoints as a bearer token.

### Browse centres and their tests

Create a centre using an authenticated request:

```http
POST /centres
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Central Diagnostics",
  "location": "Main Street"
}
```

Add a test offering to that centre:

```http
POST /centres/1/tests
Authorization: Bearer <token>
Content-Type: application/json

{
  "test_name": "Complete Blood Count",
  "description": "Blood test",
  "price": 25.50
}
```

Browse the centres with `GET /centres`. Then use `GET /centres/1/tests` to see the tests and prices offered at that centre.

### Create a booking

Use the offering ID returned when adding the test:

```http
POST /bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "centre_test_id": 1,
  "appointment_at": "2027-01-15T10:00:00+05:30"
}
```

A new booking has status `PENDING`. Its amount is copied from the centre’s test price at booking time.

Retrieve the booking with `GET /bookings/{booking_id}`. Users can retrieve only their own bookings.

### Simulate a payment

Choose a result to make the mock flow predictable:

```http
POST /payments
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking_id": 1,
  "simulate_result": "SUCCESS"
}
```

Use `"FAILED"` to demonstrate a failed payment. A successful payment changes the booking to `CONFIRMED`; a failed payment changes it to `FAILED`. The endpoint returns the payment result and updated payment record. A second mock payment for a booking that already has a payment is rejected.

### Simulate a payment webhook

The webhook represents a payment provider notifying the application of a result. No real provider is connected, so send the request manually through Swagger or from a test:

```http
POST /payments/webhook
Content-Type: application/json

{
  "provider_event_id": "evt-001",
  "booking_id": 2,
  "status": "SUCCESS"
}
```

Send the exact same event again. The application acknowledges the retry without applying it again. A later event with a different ID can update the payment status; replaying an earlier event remains a no-op.

## Database schema

| Table | Purpose |
|---|---|
| `users` | User name, unique email, password hash, and creation time |
| `diagnostic_centres` | Centre name and location |
| `diagnostic_tests` | Shared catalogue of diagnostic tests |
| `centre_tests` | Links a centre to a test and stores that centre’s price |
| `bookings` | User, selected centre-test offering, appointment, captured amount, and booking status |
| `payments` | One payment record per booking, with its latest status and event ID |
| `payment_events` | Unique provider event IDs already processed, used to make webhook retries idempotent |

The centre/test pair is unique in `centre_tests`, preventing the same test from being added twice to one centre. The booking stores its amount so a later price change does not alter an existing booking. Payment and booking status changes are saved together.

## Important assumptions

- This is a simulated payment flow; it does not contact a payment gateway.
- The patient chooses `SUCCESS` or `FAILED` when using `POST /payments` so both outcomes can be demonstrated consistently.
- The webhook is unauthenticated to represent an external provider callback. It has no signature verification because there is no real provider integration.
- Any logged-in user can create centres and add centre test offerings. There is no separate administrator role.
- Users can read only their own bookings. Booking cancellation is not exposed as an API operation.
- `CANCELLED` is an allowed booking status in the database model, but the current API does not set it.
- Tables are created from the models at application startup. Alembic and schema migration history are omitted for simplicity.

## Run the tests

Tests use a local SQLite database and do not need the PostgreSQL server. Run them from the project folder:

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe -m pytest
```

**macOS or Linux**

```bash
.venv/bin/python -m pytest
```

The tests cover centre-first browsing, booking creation, successful and failed payments, webhook retries, booking ownership, and invalid IDs.

## What I would improve with more time

- Add Alembic migrations so database schema changes can be applied safely.
- Add a separate administrator role for managing centres and test offerings.
- Verify webhook signatures when integrating with a real payment provider.
- Expand tests for malformed requests, duplicate signup, and payment state transitions.
- Add an explicit cancellation endpoint if booking cancellation becomes part of the requirements.