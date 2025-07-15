import pytest
import requests
import logging
import os
import sys


BASE_URL = os.environ.get("API_URL", "http://host.docker.internal:8000")
DIVIDE_ENDPOINT = f"{BASE_URL}/divide"
LOG_DIR = "/app/logs/"  # Path inside the Docker container
LOG_FILE = os.path.join(LOG_DIR, "test_results.log")


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


def make_request(url, method, payload, logger):
    """
    Makes an HTTP request and returns the response.
    """
    logger.info(f"Request URL: {url}")
    logger.info(f"Request Method: {method}")
    logger.info(f"Request Payload: {payload}")

    if method.upper() == "POST":
        response = requests.post(url, json=payload)
    elif method.upper() == "GET":
        response = requests.get(url, params=payload)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    logger.info(f"HTTP Status Code: {response.status_code}")
    try:
        json_response = response.json()
        logger.info(f"Full JSON Response: {json_response}")
    except requests.exceptions.JSONDecodeError:
        json_response = None
        logger.info(f"Response is not JSON: {response.text}")

    return response, json_response


def test_successful_division(logger):
    """Test successful division operation."""
    payload = {"numerator": 10, "denominator": 2}
    
    response, json_response = make_request(DIVIDE_ENDPOINT, "POST", payload, logger)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert json_response is not None, "Response should be JSON"
    assert "result" in json_response, "Expected key 'result' not found in response"
    assert json_response["result"] == 5.0, f"Expected result: 5.0, got {json_response['result']}"


def test_division_by_zero_error(logger):
    """Test division by zero error handling."""
    payload = {"numerator": 10, "denominator": 0}
    
    response, json_response = make_request(DIVIDE_ENDPOINT, "POST", payload, logger)
    
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    assert json_response is not None, "Response should be JSON"
    assert "detail" in json_response, "Expected key 'detail' not found in response"
    assert json_response["detail"] == "Division by zero is not permitted.", f"Expected detail: 'Division by zero is not permitted.', got {json_response['detail']}"
