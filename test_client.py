import requests
import logging
import os
import sys


BASE_URL = os.environ.get("API_URL", "http://host.docker.internal:8000")
DIVIDE_ENDPOINT = f"{BASE_URL}/divide"
LOG_DIR = "/app/logs/"  # Path inside the Docker container
LOG_FILE = os.path.join(LOG_DIR, "test_results.log")


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


def run_test_case(
    name,
    url,
    method,
    payload,
    expected_status,
    expected_response_key=None,
    expected_response_value=None,
):
    """
    Executes a single test case, logs the request/response, and asserts the outcome.
    """
    logger.info(f"--- Running Test Case: {name} ---")
    logger.info(f"Request URL: {url}")
    logger.info(f"Request Method: {method}")
    logger.info(f"Request Payload: {payload}")

    try:
        if method.upper() == "POST":
            response = requests.post(url, json=payload)
        elif method.upper() == "GET":
            response = requests.get(url, params=payload)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return False

        logger.info(f"HTTP Status Code: {response.status_code}")
        try:
            json_response = response.json()
            logger.info(f"Full JSON Response: {json_response}")
        except requests.exceptions.JSONDecodeError:
            json_response = None
            logger.info(f"Response is not JSON: {response.text}")

        # Assertions
        assert (
            response.status_code == expected_status
        ), f"Expected status {expected_status}, got {response.status_code}"

        if expected_response_key and json_response:
            assert (
                expected_response_key in json_response
            ), f"Expected key '{expected_response_key}' not found in response"
            assert (
                json_response[expected_response_key] == expected_response_value
            ), f"Expected '{expected_response_key}': {expected_response_value}, got {json_response[expected_response_key]}"

        logger.info(f"Test Case '{name}' PASSED.")
        return True

    except requests.exceptions.ConnectionError as e:
        logger.error(
            f"Network error: Could not connect to the service at {url}. Is the FastAPI service running? Error: {e}"
        )
        logger.info(f"Test Case '{name}' FAILED due to connection error.")
        return False
    except AssertionError as e:
        logger.error(f"Assertion failed for test case '{name}': {e}")
        logger.info(f"Test Case '{name}' FAILED.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during test case '{name}': {e}")
        logger.info(f"Test Case '{name}' FAILED due to unexpected error.")
        return False


if __name__ == "__main__":
    logger.info("--- Starting FastAPI Service Tests ---")

    # Test Case 1: Successful Division
    success_payload = {"numerator": 10, "denominator": 2}
    run_test_case(
        "Successful Division",
        DIVIDE_ENDPOINT,
        "POST",
        success_payload,
        200,
        "result",
        5.0,
    )

    # Test Case 2: Division by Zero Error
    zero_division_payload = {"numerator": 10, "denominator": 0}
    run_test_case(
        "Division by Zero Error",
        DIVIDE_ENDPOINT,
        "POST",
        zero_division_payload,
        400,
        "detail",
        "Division by zero is not permitted.",
    )

    logger.info("--- FastAPI Service Tests Finished ---")
