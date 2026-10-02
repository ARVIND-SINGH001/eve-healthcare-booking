def auth(client, email="patient@example.com"):
    response = client.post("/auth/signup", json={
        "name": "Test Patient", "email": email, "password": "password123"
    })
    assert response.status_code == 201
    token = client.post("/auth/login", json={
        "email": email, "password": "password123"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def offering(client, headers):
    centre = client.post("/centres", headers=headers, json={
        "name": "Central Diagnostics", "location": "Main Street"
    }).json()
    item = client.post(f"/centres/{centre['id']}/tests", headers=headers, json={
        "test_name": "CBC", "description": "Blood test", "price": 25.5
    }).json()
    return centre["id"], item["offering_id"]


def booking(client, headers, offering_id):
    response = client.post("/bookings", headers=headers, json={
        "centre_test_id": offering_id,
        "appointment_at": "2099-01-01T10:00:00+05:30",
    })
    assert response.status_code == 201
    return response.json()


def test_centre_booking_and_success_payment(client):
    headers = auth(client)
    centre_id, offer_id = offering(client, headers)
    assert client.get("/centres").json()[0]["id"] == centre_id
    assert client.get(f"/centres/{centre_id}/tests").json()[0]["price"] == 25.5
    item = booking(client, headers, offer_id)
    assert item["status"] == "PENDING"
    result = client.post("/payments", headers=headers, json={
        "booking_id": item["id"], "simulate_result": "SUCCESS"
    })
    assert result.status_code == 201
    assert client.get(f"/bookings/{item['id']}", headers=headers).json()["status"] == "CONFIRMED"


def test_failed_payment_updates_booking(client):
    headers = auth(client)
    _, offer_id = offering(client, headers)
    item = booking(client, headers, offer_id)
    result = client.post("/payments", headers=headers, json={
        "booking_id": item["id"], "simulate_result": "FAILED"
    })
    assert result.status_code == 201
    assert client.get(f"/bookings/{item['id']}", headers=headers).json()["status"] == "FAILED"


def test_webhook_retries_are_idempotent_even_after_a_later_event(client):
    headers = auth(client)
    _, offer_id = offering(client, headers)
    item = booking(client, headers, offer_id)
    first_event = {"provider_event_id": "evt-001", "booking_id": item["id"], "status": "SUCCESS"}
    later_event = {"provider_event_id": "evt-002", "booking_id": item["id"], "status": "FAILED"}
    first = client.post("/payments/webhook", json=first_event)
    assert first.json()["message"] == "Event processed"
    later = client.post("/payments/webhook", json=later_event)
    assert later.json()["message"] == "Event processed"
    retry = client.post("/payments/webhook", json=first_event)
    assert retry.status_code == 200
    assert retry.json()["message"] == "Event already processed"
    assert retry.json()["payment_id"] == first.json()["payment_id"] == later.json()["payment_id"]
    assert client.get(f"/bookings/{item['id']}", headers=headers).json()["status"] == "FAILED"


def test_booking_is_private_and_invalid_ids_are_handled(client):
    one = auth(client, "one@example.com")
    two = auth(client, "two@example.com")
    _, offer_id = offering(client, one)
    item = booking(client, one, offer_id)
    assert client.get(f"/bookings/{item['id']}", headers=two).status_code == 404
    assert client.post("/payments", headers=one, json={
        "booking_id": 999, "simulate_result": "SUCCESS"
    }).status_code == 404
    assert client.post("/payments", json={
        "booking_id": 999, "simulate_result": "SUCCESS"
    }).status_code == 401
