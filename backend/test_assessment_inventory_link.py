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


def test_assessment_can_link_to_owned_inventory_system(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system = client.post("/inventory", json=inventory_payload(), headers=headers)
    assert system.status_code == 201
    system_id = system.json()["id"]

    created = client.post(
        "/assessments",
        json={"title": "Context-linked review", "ai_system_id": system_id},
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["ai_system_id"] == system_id
    assert body["ai_system"]["name"] == "Customer support assistant"

    fetched = client.get(f"/assessments/{body['id']}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["ai_system"]["purpose"]


def test_legacy_assessment_remains_unlinked(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.post(
        "/assessments", json={"title": "Unlinked legacy-style review"}, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["ai_system_id"] is None
    assert response.json()["ai_system"] is None


def test_assessment_cannot_link_to_another_users_inventory(client, test_user, second_user):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system = client.post("/inventory", json=inventory_payload(), headers=owner_headers)
    system_id = system.json()["id"]

    create_response = client.post(
        "/assessments",
        json={"title": "Cross-user attempt", "ai_system_id": system_id},
        headers=other_headers,
    )
    assert create_response.status_code == 404

    assessment = client.post(
        "/assessments", json={"title": "Later link attempt"}, headers=other_headers
    )
    assert assessment.status_code == 201
    update_response = client.put(
        f"/assessments/{assessment.json()['id']}",
        json={"ai_system_id": system_id},
        headers=other_headers,
    )
    assert update_response.status_code == 404
