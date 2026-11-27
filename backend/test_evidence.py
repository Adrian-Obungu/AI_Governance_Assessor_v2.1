def system_payload():
    return {
        "name": "Customer support assistant",
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
    }


def evidence_payload(system_id, assessment_id=None):
    return {
        "ai_system_id": system_id,
        "assessment_id": assessment_id,
        "title": "AI use policy",
        "description": "The current internal policy describing approved use and review responsibilities.",
        "evidence_type": "policy",
        "source_location": "https://example.test/policies/ai-use",
        "owner": "Risk and Compliance",
        "collected_on": "2026-11-27",
        "review_date": "2027-03-31",
        "status": "submitted",
        "reviewer_notes": "Awaiting annual review.",
    }


def create_system(client, headers):
    response = client.post("/inventory", json=system_payload(), headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def test_evidence_create_list_filter_and_update(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    assessment = client.post(
        "/assessments",
        json={"title": "Evidence-linked review", "ai_system_id": system_id},
        headers=headers,
    )
    assert assessment.status_code == 201

    created = client.post(
        "/evidence",
        json=evidence_payload(system_id, assessment.json()["id"]),
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "submitted"
    assert body["review_date"] == "2027-03-31"

    filtered = client.get(
        f"/evidence?ai_system_id={system_id}&status=submitted", headers=headers
    )
    assert filtered.status_code == 200
    assert [record["id"] for record in filtered.json()] == [body["id"]]

    updated = client.put(
        f"/evidence/{body['id']}",
        json={
            "status": "reviewed",
            "reviewer_notes": "Reviewed by the governance lead.",
        },
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "reviewed"


def test_evidence_validates_type_and_required_system(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    invalid = client.post(
        "/evidence",
        json={
            "ai_system_id": 99999,
            "title": "Invalid evidence",
            "description": "This should not be accepted.",
            "evidence_type": "unknown",
        },
        headers=headers,
    )
    assert invalid.status_code == 422

    system_id = create_system(client, headers)
    bad_status = client.post(
        "/evidence",
        json={**evidence_payload(system_id), "status": "unknown"},
        headers=headers,
    )
    assert bad_status.status_code == 422


def test_evidence_isolation_and_invalid_cross_user_links(
    client, test_user, second_user
):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    created = client.post(
        "/evidence", json=evidence_payload(system_id), headers=owner_headers
    )
    assert created.status_code == 201
    record_id = created.json()["id"]

    assert (
        client.get(f"/evidence/{record_id}", headers=other_headers).status_code == 404
    )
    assert (
        client.put(
            f"/evidence/{record_id}",
            json={"title": "Attempted takeover"},
            headers=other_headers,
        ).status_code
        == 404
    )
    assert client.get("/evidence", headers=other_headers).json() == []

    invalid_link = client.post(
        "/evidence",
        json=evidence_payload(99999),
        headers=other_headers,
    )
    assert invalid_link.status_code == 404
