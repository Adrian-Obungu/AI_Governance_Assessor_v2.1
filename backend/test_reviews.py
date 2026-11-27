def system_payload():
    return {
        "name": "Customer support assistant",
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
    }


def review_payload(system_id, assessment_id=None, reassessment_id=None):
    return {
        "ai_system_id": system_id,
        "assessment_id": assessment_id,
        "reassessment_id": reassessment_id,
        "reviewer": "Governance lead",
        "review_date": "2027-03-31",
        "decision": "reassess",
        "material_change": True,
        "change_summary": "The provider changed its data-retention terms.",
        "next_review_date": "2027-06-30",
        "reviewer_notes": "Run a focused reassessment before continued use.",
    }


def create_system(client, headers):
    response = client.post("/inventory", json=system_payload(), headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def create_assessment(client, headers, system_id, title):
    response = client.post(
        "/assessments",
        json={"title": title, "ai_system_id": system_id},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_review_create_filter_and_update(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    assessment_id = create_assessment(client, headers, system_id, "Initial review")
    reassessment_id = create_assessment(
        client, headers, system_id, "Focused reassessment"
    )

    created = client.post(
        "/reviews",
        json=review_payload(system_id, assessment_id, reassessment_id),
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["decision"] == "reassess"
    assert body["material_change"] is True
    assert body["next_review_date"] == "2027-06-30"

    filtered = client.get(
        f"/reviews?ai_system_id={system_id}&decision=reassess&material_change=true",
        headers=headers,
    )
    assert filtered.status_code == 200
    assert [record["id"] for record in filtered.json()] == [body["id"]]

    updated = client.put(
        f"/reviews/{body['id']}",
        json={"decision": "continue", "material_change": False},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["decision"] == "continue"
    assert updated.json()["material_change"] is False


def test_review_validates_decision_and_context(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    assessment_id = create_assessment(client, headers, system_id, "Initial review")
    invalid = client.post(
        "/reviews",
        json={**review_payload(system_id, assessment_id), "decision": "approve"},
        headers=headers,
    )
    assert invalid.status_code == 422

    other_system_id = create_system(client, headers)
    mismatch = client.post(
        "/reviews",
        json=review_payload(other_system_id, assessment_id),
        headers=headers,
    )
    assert mismatch.status_code == 404


def test_review_isolation_and_inaccessible_reassessment(client, test_user, second_user):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    review = client.post(
        "/reviews", json=review_payload(system_id), headers=owner_headers
    )
    assert review.status_code == 201
    review_id = review.json()["id"]

    assert client.get(f"/reviews/{review_id}", headers=other_headers).status_code == 404
    assert (
        client.put(
            f"/reviews/{review_id}",
            json={"reviewer": "Attempted takeover"},
            headers=other_headers,
        ).status_code
        == 404
    )
    assert client.get("/reviews", headers=other_headers).json() == []
    assert (
        client.post(
            "/reviews",
            json=review_payload(system_id),
            headers=other_headers,
        ).status_code
        == 404
    )
