import pytest
from unittest.mock import Mock, patch
from cli.api_client import APIClient


def test_api_client_initialization():
    """Test API client initialization"""
    client = APIClient()
    assert client.base_url == "http://localhost:8000"
    assert "Authorization" not in client.headers
    
    client_with_token = APIClient(token="test_token")
    assert client_with_token.headers["Authorization"] == "Bearer test_token"


@patch('cli.api_client.requests.post')
def test_login(mock_post):
    """Test login method"""
    mock_response = Mock()
    mock_response.json.return_value = {"access_token": "test_token", "token_type": "bearer"}
    mock_post.return_value = mock_response
    
    client = APIClient()
    result = client.login("test@example.com", "password123")
    
    assert result["access_token"] == "test_token"
    mock_post.assert_called_once()


@patch('cli.api_client.requests.get')
def test_list_assessments(mock_get):
    """Test list assessments method"""
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": 1, "title": "Test Assessment", "status": "draft"}
    ]
    mock_get.return_value = mock_response
    
    client = APIClient(token="test_token")
    result = client.list_assessments()
    
    assert len(result) == 1
    assert result[0]["title"] == "Test Assessment"
    mock_get.assert_called_once()


@patch('cli.api_client.requests.post')
def test_create_assessment(mock_post):
    """Test create assessment method"""
    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "title": "New Assessment"}
    mock_post.return_value = mock_response
    
    client = APIClient(token="test_token")
    result = client.create_assessment("New Assessment", "Description")
    
    assert result["id"] == 1
    assert result["title"] == "New Assessment"
    mock_post.assert_called_once()
