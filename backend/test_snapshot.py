def system_payload(name="Customer support assistant", review_date=None):
    return {
        "name": name,
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
        "review_date": review_date,
    }


def create_system(client, headers, name="Customer support assistant", review_date=None):
    response = client.post(
        "/inventory", json=system_payload(name, review_date), headers=headers
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_signal(client, headers, system_id):
    response = client.post(
        "/signals",
        json={
            "ai_system_id": system_id,
            "signal_type": "incident",
            "severity": "high",
            "status": "triaged",
            "title": "Unexpected answer pattern",
            "description": "A user reported an unexpected answer.",
            "reported_by": "Support",
            "reported_on": "2027-05-01",
        },
        headers=headers,
    )
    assert response.status_code == 201


def test_snapshot_reports_coverage_and_human_attention(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers, review_date="2020-01-01")
    create_signal(client, headers, system_id)

    response = client.get(
        f"/governance/snapshots?ai_system_id={system_id}", headers=headers
    )
    assert response.status_code == 200
    snapshot = response.json()[0]
    assert snapshot["ai_system_id"] == system_id
    assert snapshot["coverage"]["inventory"] is True
    assert snapshot["coverage"]["operational_signals"] == 1
    assert snapshot["active_signals"] == 1
    assert snapshot["review_due"] is True
    assert snapshot["attention"][0]["source_type"] == "assessment"
    assert "Start or link" in snapshot["next_action"]


def test_snapshot_filters_and_isolates_users(client, test_user, second_user):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    other_system_id = create_system(client, owner_headers, "Payroll assistant")

    filtered = client.get(
        f"/governance/snapshots?ai_system_id={system_id}", headers=owner_headers
    )
    assert filtered.status_code == 200
    assert [item["ai_system_id"] for item in filtered.json()] == [system_id]

    other_view = client.get(
        f"/governance/snapshots?ai_system_id={system_id}", headers=other_headers
    )
    assert other_view.status_code == 200
    assert other_view.json() == []

    all_view = client.get("/governance/snapshots", headers=owner_headers)
    assert {item["ai_system_id"] for item in all_view.json()} == {
        system_id,
        other_system_id,
    }
