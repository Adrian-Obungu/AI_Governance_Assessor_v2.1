def system_payload(name="Customer support assistant"):
    return {
        "name": name,
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
    }


def create_system(client, headers, name="Customer support assistant"):
    response = client.post("/inventory", json=system_payload(name), headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def create_signal(client, headers, system_id):
    response = client.post(
        "/signals",
        json={
            "ai_system_id": system_id,
            "signal_type": "feedback",
            "severity": "low",
            "status": "new",
            "title": "User suggestion",
            "description": "Users suggested clearer explanations.",
            "reported_by": "Support",
            "reported_on": "2027-05-01",
        },
        headers=headers,
    )
    assert response.status_code == 201


def test_activity_combines_and_filters_governance_records(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    create_signal(client, headers, system_id)

    all_events = client.get(f"/activity?ai_system_id={system_id}", headers=headers)
    assert all_events.status_code == 200
    events = all_events.json()
    assert [event["source_type"] for event in events] == ["signal", "inventory"]
    assert events[0]["ai_system_id"] == system_id
    assert events[0]["occurred_at"].startswith("2027-05-01")

    filtered = client.get(
        f"/activity?ai_system_id={system_id}&source_type=signal", headers=headers
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["source_type"] == "signal"


def test_activity_returns_empty_for_another_users_system(
    client, test_user, second_user
):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    response = client.get(f"/activity?ai_system_id={system_id}", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_activity_rejects_invalid_source_type(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/activity?source_type=complaint", headers=headers)
    assert response.status_code == 422
