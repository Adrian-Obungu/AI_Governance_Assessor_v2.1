from sqlalchemy import inspect

from backend.conftest import engine


def _create_assessment(client, token):
    response = client.post(
        "/assessments",
        json={"title": "Phase 4 integrity assessment"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _privacy_answers():
    return {"dp_1": 10, "dp_2": 5, "dp_3": 15, "dp_4": 10, "dp_5": 15}


def test_result_schema_has_phase4_metadata_and_unique_constraint(client, test_db):
    result_columns = {
        column["name"] for column in inspect(engine).get_columns("assessment_results")
    }
    assert {
        "questionnaire_version",
        "questionnaire_snapshot",
        "scoring_version",
    }.issubset(result_columns)

    unique_constraints = inspect(engine).get_unique_constraints("assessment_results")
    assert any(
        constraint["name"] == "uq_assessment_results_assessment_category"
        and constraint["column_names"] == ["assessment_id", "category"]
        for constraint in unique_constraints
    )


def test_repeating_a_category_submission_updates_one_result(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    assessment_id = _create_assessment(client, test_user["token"])
    payload = {"category": "data_privacy", "answers": _privacy_answers()}

    first = client.post(
        f"/assessments/{assessment_id}/answers", json=payload, headers=headers
    )
    second = client.post(
        f"/assessments/{assessment_id}/answers", json=payload, headers=headers
    )
    assert first.status_code == 200
    assert second.status_code == 200

    detail = client.get(f"/assessments/{assessment_id}", headers=headers)
    assert detail.status_code == 200
    results = detail.json()["results"]
    assert len(results) == 1
    assert results[0]["category"] == "data_privacy"


def test_incomplete_answers_are_rejected(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    assessment_id = _create_assessment(client, test_user["token"])
    response = client.post(
        f"/assessments/{assessment_id}/answers",
        json={"category": "data_privacy", "answers": {"dp_1": 10}},
        headers=headers,
    )
    assert response.status_code == 422


def test_completed_assessment_cannot_regress_status(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    assessment_id = _create_assessment(client, test_user["token"])
    response = client.put(
        f"/assessments/{assessment_id}",
        json={"status": "completed"},
        headers=headers,
    )
    assert response.status_code == 409
