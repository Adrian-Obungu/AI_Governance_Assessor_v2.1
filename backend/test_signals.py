def system_payload(name="Customer support assistant"):
    return {
        "name": name,
        "purpose": "Answer common customer questions using approved knowledge sources.",
        "lifecycle_stage": "pilot",
        "geographies": ["Kenya"],
        "data_categories": ["customer messages"],
        "affected_groups": ["customers"],
    }


def finding_payload(system_id, evidence_id):
    return {
        "ai_system_id": system_id,
        "evidence_id": evidence_id,
        "title": "Missing owner",
        "conclusion": "The review does not identify an accountable owner.",
        "priority": "high",
        "owner": "Operations",
        "remediation_action": "Assign a named owner.",
    }


def evidence_payload(system_id):
    return {
        "ai_system_id": system_id,
        "title": "AI use policy",
        "description": "Approved use and review responsibilities.",
        "evidence_type": "policy",
    }


def signal_payload(system_id, finding_id=None, review_id=None):
    return {
        "ai_system_id": system_id,
        "finding_id": finding_id,
        "review_id": review_id,
        "signal_type": "incident",
        "severity": "high",
        "status": "triaged",
        "title": "Unexpected response pattern",
        "description": "Support staff reported an unexpected answer pattern that needs review.",
        "reported_by": "Customer Operations",
        "reported_on": "2027-04-05",
        "owner": "AI Operations",
        "response_action": "Review recent examples and confirm whether the finding needs updating.",
        "reviewer_notes": "Keep customer identifiers out of this record.",
    }


def create_system(client, headers, name="Customer support assistant"):
    response = client.post("/inventory", json=system_payload(name), headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def create_finding_context(client, headers, system_id):
    evidence = client.post(
        "/evidence", json=evidence_payload(system_id), headers=headers
    )
    assert evidence.status_code == 201
    finding = client.post(
        "/findings",
        json=finding_payload(system_id, evidence.json()["id"]),
        headers=headers,
    )
    assert finding.status_code == 201
    return finding.json()["id"]


def test_signal_create_filter_and_update(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    finding_id = create_finding_context(client, headers, system_id)
    created = client.post(
        "/signals",
        json=signal_payload(system_id, finding_id=finding_id),
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["signal_type"] == "incident"
    assert body["severity"] == "high"
    assert body["reported_on"] == "2027-04-05"

    filtered = client.get(
        f"/signals?ai_system_id={system_id}&signal_type=incident&severity=high&status=triaged",
        headers=headers,
    )
    assert filtered.status_code == 200
    assert [record["id"] for record in filtered.json()] == [body["id"]]

    updated = client.put(
        f"/signals/{body['id']}",
        json={"status": "closed", "response_action": "Closed after review."},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "closed"


def test_signal_validates_type_and_context(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    system_id = create_system(client, headers)
    invalid = client.post(
        "/signals",
        json={**signal_payload(system_id), "signal_type": "complaint"},
        headers=headers,
    )
    assert invalid.status_code == 422

    other_system_id = create_system(client, headers, "Payroll assistant")
    mismatch = client.post(
        "/signals",
        json=signal_payload(other_system_id, finding_id=99999),
        headers=headers,
    )
    assert mismatch.status_code == 404


def test_signal_isolation(client, test_user, second_user):
    owner_headers = {"Authorization": f"Bearer {test_user['token']}"}
    other_headers = {"Authorization": f"Bearer {second_user['token']}"}
    system_id = create_system(client, owner_headers)
    created = client.post(
        "/signals", json=signal_payload(system_id), headers=owner_headers
    )
    assert created.status_code == 201
    signal_id = created.json()["id"]

    assert client.get(f"/signals/{signal_id}", headers=other_headers).status_code == 404
    assert (
        client.put(
            f"/signals/{signal_id}",
            json={"title": "Attempted takeover"},
            headers=other_headers,
        ).status_code
        == 404
    )
    assert client.get("/signals", headers=other_headers).json() == []
    assert (
        client.post(
            "/signals",
            json=signal_payload(system_id),
            headers=other_headers,
        ).status_code
        == 404
    )
