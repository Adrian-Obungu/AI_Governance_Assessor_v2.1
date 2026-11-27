def inventory_payload(name="Customer support assistant"):
    return {
        "name": name,
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "department": "Customer Operations",
        "business_owner": "Operations Lead",
        "provider": "Internal team",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya", "Uganda"],
        "data_categories": ["customer messages", "account identifiers"],
        "affected_groups": ["customers", "support staff"],
        "review_date": "2027-03-31",
    }


def test_inventory_create_list_and_update(client, test_user):
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/inventory", json=inventory_payload(), headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Customer support assistant"
    assert body["lifecycle_stage"] == "pilot"
    assert body["review_date"] == "2027-03-31"

    listed = client.get("/inventory", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/inventory/{body['id']}",
        json={"lifecycle_stage": "in_production", "review_date": "2027-06-30"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["lifecycle_stage"] == "in_production"
    assert updated.json()["review_date"] == "2027-06-30"


def test_inventory_requires_context_and_valid_lifecycle(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    missing_name = client.post(
        "/inventory", json={"purpose": "Missing name"}, headers=headers
    )
    assert missing_name.status_code == 422

    bad_stage = client.post(
        "/inventory",
        json={**inventory_payload(), "lifecycle_stage": "unknown"},
        headers=headers,
    )
    assert bad_stage.status_code == 422


def test_inventory_isolation_returns_not_found(client, test_user, second_user):
    first_headers = {"Authorization": f"Bearer {test_user['token']}"}
    second_headers = {"Authorization": f"Bearer {second_user['token']}"}
    created = client.post("/inventory", json=inventory_payload(), headers=first_headers)
    system_id = created.json()["id"]

    assert (
        client.get(f"/inventory/{system_id}", headers=second_headers).status_code == 404
    )
    assert (
        client.put(
            f"/inventory/{system_id}",
            json={"name": "Attempted takeover"},
            headers=second_headers,
        ).status_code
        == 404
    )
    assert client.get("/inventory", headers=second_headers).json() == []
