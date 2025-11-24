import requests
from typing import Optional, Dict, Any
from cli.config import API_BASE_URL


class APIClient:
    """Client for interacting with the AI Governance Assessor API"""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = API_BASE_URL
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()
    
    def list_assessments(self) -> list:
        """List all assessments"""
        response = requests.get(
            f"{self.base_url}/assessments",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_assessment(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new assessment"""
        response = requests.post(
            f"{self.base_url}/assessments",
            json={"title": title, "description": description},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_assessment(self, assessment_id: int) -> Dict[str, Any]:
        """Get assessment details"""
        response = requests.get(
            f"{self.base_url}/assessments/{assessment_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_summary(self, assessment_id: int) -> Dict[str, Any]:
        """Get assessment summary"""
        response = requests.get(
            f"{self.base_url}/assessments/{assessment_id}/summary",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def export_csv(self, assessment_id: int, output_file: str):
        """Export assessment as CSV"""
        response = requests.get(
            f"{self.base_url}/assessments/{assessment_id}/export/csv",
            headers=self.headers
        )
        response.raise_for_status()
        with open(output_file, 'wb') as f:
            f.write(response.content)
    
    def export_pdf(self, assessment_id: int, output_file: str):
        """Export assessment as PDF"""
        response = requests.get(
            f"{self.base_url}/assessments/{assessment_id}/export/pdf",
            headers=self.headers
        )
        response.raise_for_status()
        with open(output_file, 'wb') as f:
            f.write(response.content)
