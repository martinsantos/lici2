import requests
import json
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URLS = {
    "documents": "http://localhost:4324/api/documents",
    "recon": "http://localhost:4324/api/recon",
    "licitaciones": "http://localhost:4324/api/licitaciones"
}

def test_endpoints():
    endpoints = [
        ("documents", "/", {"skip": 0, "limit": 10}),  # Documents list
        ("recon", "/templates", {}),  # Recon templates list
        ("licitaciones", "/", {"skip": 0, "limit": 10})  # Licitaciones list
    ]
    
    for service, endpoint, params in endpoints:
        try:
            full_url = f"{BASE_URLS[service]}{endpoint}"
            logger.info(f"Testing endpoint: {full_url}")
            logger.info(f"Params: {params}")
            
            response = requests.get(full_url, params=params)
            logger.info(f"Endpoint {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    logger.info(json.dumps(json_response, indent=2)[:500])  # Print first 500 chars of JSON
                except ValueError:
                    logger.error("Response is not JSON")
            else:
                logger.error(f"Error accessing {endpoint}: {response.text}")
                
                # Additional error handling
                try:
                    error_details = response.json()
                    logger.error(f"Error details: {error_details}")
                except ValueError:
                    logger.error("Could not parse error response")
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to {endpoint}")
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {str(e)}")
            traceback.print_exc()

def test_root():
    try:
        response = requests.get("http://localhost:4324/")
        logger.info("Root Endpoint Status: %s", response.status_code)
        logger.info("Root Response: %s", response.json())
    except Exception as e:
        logger.error("Error accessing root endpoint: %s", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    test_root()
    test_endpoints()
