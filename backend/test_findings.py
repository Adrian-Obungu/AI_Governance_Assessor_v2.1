def system_payload():
    return {
        "name": "Customer support assistant",
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
    }


def evidence_payload(system_id):
    return {
        "ai_system_id": system_id,
        "title": "AI use policy",
        "description": "The current internal policy describing approved use and review responsibilities.",
        "evidence_type": "policy",
    }


def finding_payload(system_id, evidence_id, assessment_id=None):
    return {
        "ai_system_id": system_id,
        "evidence_id": evidence_id,
        "assessment_id": assessment_id,
        "title": "Owner review is not documented",
        "conclusion": "The current review record does not show who approved the support workflow.",
        "priority": "high",
        "owner": "Customer Operations",
        "remediation_action": "Assign a named review owner and record the approval decision.",
        "due_date": "2027-02-28",
        "status": "open",
        "reviewer_notes": "Discuss at the next governance meeting.",
    }


def create_system(client, headers):
    response = client.post("/inventory", json=system_payload(), headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def create_evidence(client, headers, system_id):
    response = client.post(
        "/evidence", json=evidence_payload(system_id), headers=headers
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_finding_create_filter_and_update(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    evidence_id = create_evidence(client, headers, system_id)
    assessment = client.post(
        "/assessments",
        json={"title": "Finding-linked review", "ai_system_id": system_id},
        headers=headers,
    )
    assert assessment.status_code == 201

    created = client.post(
        "/findings",
        json=finding_payload(system_id, evidence_id, assessment.json()["id"]),
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["priority"] == "high"
    assert body["remediation_action"].startswith("Assign")
    assert body["due_date"] == "2027-02-28"

    filtered = client.get(
        f"/findings?ai_system_id={system_id}&status=open&priority=high",
        headers=headers,
    )
    assert filtered.status_code == 200
    assert [record["id"] for record in filtered.json()] == [body["id"]]

    updated = client.put(
        f"/findings/{body['id']}",
        json={"status": "in_progress", "owner": "Risk and Compliance"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"


def test_finding_validates_values_and_context_links(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    evidence_id = create_evidence(client, headers, system_id)
    invalid = client.post(
        "/findings",
        json={**finding_payload(system_id, evidence_id), "priority": "urgent"},
        headers=headers,
    )
    assert invalid.status_code == 422

    mismatched_evidence = client.post(
        "/findings",
        json=finding_payload(system_id, 99999),
        headers=headers,
    )
    assert mismatched_evidence.status_code == 404


def test_finding_isolation_and_cross_system_evidence_rejection(
    client, test_user, second_user
):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    evidence_id = create_evidence(client, owner_headers, system_id)
    created = client.post(
        "/findings",
        json=finding_payload(system_id, evidence_id),
        headers=owner_headers,
    )
    assert created.status_code == 201
    finding_id = created.json()["id"]

    assert (
        client.get(f"/findings/{finding_id}", headers=other_headers).status_code == 404
    )
    assert (
        client.put(
            f"/findings/{finding_id}",
            json={"title": "Attempted takeover"},
            headers=other_headers,
        ).status_code
        == 404
    )
    assert client.get("/findings", headers=other_headers).json() == []
    assert (
        client.post(
            "/findings",
            json=finding_payload(system_id, evidence_id),
            headers=other_headers,
        ).status_code
        == 404
    )
