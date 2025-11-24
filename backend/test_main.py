import pytest


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_signup(client):
    """Test user signup"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data


def test_signup_duplicate_email(client, test_user):
    """Test signup with duplicate email"""
    response = client.post(
        "/auth/signup",
        json={
            "email": test_user["email"],
            "password": "password123"
        }
    )
    assert response.status_code == 400


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user["email"],
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_password_reset_request(client, test_user):
    """Test password reset request"""
    response = client.post(
        "/auth/reset-password",
        json={"email": test_user["email"]}
    )
    assert response.status_code == 200


def test_create_assessment(client, test_user):
    """Test creating an assessment"""
    response = client.post(
        "/assessments",
        json={
            "title": "Test Assessment",
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Assessment"
    assert data["status"] == "draft"


def test_list_assessments(client, test_user):
    """Test listing assessments"""
    # Create an assessment first
    client.post(
        "/assessments",
        json={"title": "Test Assessment"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    response = client.get(
        "/assessments",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_questionnaires(client):
    """Test getting questionnaire templates"""
    response = client.get("/assessments/questionnaires")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4  # Four categories


def test_submit_answers(client, test_user):
    """Test submitting category answers"""
    # Create assessment
    create_response = client.post(
        "/assessments",
        json={"title": "Test Assessment"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assessment_id = create_response.json()["id"]
    
    # Submit answers
    response = client.post(
        f"/assessments/{assessment_id}/answers",
        json={
            "category": "data_privacy",
            "answers": {
                "dp_1": 10,
                "dp_2": 5,
                "dp_3": 15,
                "dp_4": 10,
                "dp_5": 15
            }
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "data_privacy"
    assert data["score"] > 0


def test_get_assessment_summary(client, test_user):
    """Test getting assessment summary"""
    # Create assessment
    create_response = client.post(
        "/assessments",
        json={"title": "Test Assessment"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assessment_id = create_response.json()["id"]
    
    # Submit answers
    client.post(
        f"/assessments/{assessment_id}/answers",
        json={
            "category": "data_privacy",
            "answers": {"dp_1": 10, "dp_2": 5, "dp_3": 15, "dp_4": 10, "dp_5": 15}
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    # Get summary
    response = client.get(
        f"/assessments/{assessment_id}/summary",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "category_scores" in data


def test_export_csv(client, test_user):
    """Test CSV export"""
    # Create assessment
    create_response = client.post(
        "/assessments",
        json={"title": "Test Assessment"},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assessment_id = create_response.json()["id"]
    
    response = client.get(
        f"/assessments/{assessment_id}/export/csv",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_unauthorized_access(client):
    """Test accessing protected endpoint without auth"""
    response = client.get("/assessments")
    assert response.status_code == 403
