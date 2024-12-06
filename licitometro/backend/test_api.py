import pytest
from datetime import datetime
import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:4324/api"

@pytest.fixture
def template_data():
    return {
        "nombre": f"Test Template {datetime.now().isoformat()}",
        "descripcion": "Template for testing",
        "config": {
            "url": "https://example.com",
            "frequency": "daily"
        },
        "features": [
            {"name": "title", "selector": "h1"},
            {"name": "description", "selector": "p.description"}
        ]
    }

@pytest.fixture
def created_template(template_data):
    """Create a template and return its ID for testing"""
    url = f"{BASE_URL}/templates"
    response = requests.post(url, json=template_data)
    if response.status_code == 200:
        return response.json()["template_id"]
    return None

def test_create_template(template_data):
    """Test creating a new template"""
    url = f"{BASE_URL}/templates"
    try:
        logger.info(f"Testing POST {url}")
        response = requests.post(url, json=template_data)
        response.raise_for_status()
        data = response.json()
        assert "template_id" in data
        assert data["message"] == "Template created successfully"
        logger.info(f"Template created successfully with ID: {data['template_id']}")
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        logger.error(f"Response: {response.text}")
        raise

def test_list_templates():
    """Test listing all templates"""
    url = f"{BASE_URL}/templates"
    try:
        logger.info(f"Testing GET {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
        logger.info(f"Successfully retrieved {len(data['templates'])} templates")
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        logger.error(f"Response: {response.text}")
        raise

def test_get_template(created_template):
    """Test getting a specific template"""
    if not created_template:
        pytest.skip("No template was created")
    
    url = f"{BASE_URL}/templates/{created_template}"
    try:
        logger.info(f"Testing GET {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        assert "id" in data
        assert data["id"] == created_template
        logger.info(f"Successfully retrieved template {created_template}")
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        logger.error(f"Response: {response.text}")
        raise

def test_start_scraping(created_template):
    """Test starting a scraping job"""
    if not created_template:
        pytest.skip("No template was created")
    
    url = f"{BASE_URL}/templates/{created_template}/scrape"
    try:
        logger.info(f"Testing POST {url}")
        response = requests.post(url)
        response.raise_for_status()
        data = response.json()
        assert "job_id" in data
        logger.info(f"Successfully started scraping job {data['job_id']}")
    except Exception as e:
        logger.error(f"Error starting scraping: {str(e)}")
        logger.error(f"Response: {response.text}")
        raise

def test_get_scraping_status(created_template):
    """Test getting scraping status"""
    if not created_template:
        pytest.skip("No template was created")
    
    url = f"{BASE_URL}/templates/{created_template}/status"
    try:
        logger.info(f"Testing GET {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        assert "status" in data
        logger.info(f"Successfully retrieved scraping status: {data['status']}")
    except Exception as e:
        logger.error(f"Error getting scraping status: {str(e)}")
        logger.error(f"Response: {response.text}")
        raise

def run_tests():
    """Run all tests"""
    try:
        # Test template creation and listing
        test_create_template(template_data())
        test_list_templates()
        
        # Test scraping functionality
        created_template_id = created_template(template_data())
        if created_template_id:
            test_get_template(created_template_id)
            test_start_scraping(created_template_id)
            test_get_scraping_status(created_template_id)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_tests()
