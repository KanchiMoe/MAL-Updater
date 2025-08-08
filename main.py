import logging
import os
import sys
import requests
import backoff

# --- Logging Configuration ---
DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL") or logging.DEBUG
logging.getLogger().setLevel(DEFAULT_LOG_LEVEL)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

# --- Configuration ---
MAL_USERNAME = os.getenv("MAL_USERNAME")

# --- Request Handler ---
@backoff.on_exception(
    backoff.constant,
    requests.exceptions.RequestException,
    interval=60,
    max_tries=5,
    jitter=None,
    giveup=lambda e: e.response is not None and e.response.status_code == 200
)
def request_handler(requested_url: str) -> bool:
    try:
        response = requests.get(requested_url, timeout=10)
        logging.debug("Response status: %s for URL: %s", response.status_code, requested_url)

        if response.status_code == 200:
            return True

        logging.critical("Failed to retrieve page. URL: %s, Status Code: %d", requested_url, response.status_code)
        return False

    except requests.exceptions.RequestException as e:
        logging.critical("Request to %s failed: %s", requested_url, e)
        return False

# --- Update Function ---
def update_site(name: str, base_url: str, update_path: str):
    logging.info("Starting %s update...", name)
    full_url = f"{base_url}/{MAL_USERNAME}{update_path}"
    logging.debug("Constructed URL: %s", full_url)

    if request_handler(full_url):
        logging.info("%s update successful.", name)
    else:
        logging.critical("%s update failed.", name)
        sys.exit(2)

# --- Main Execution ---
def main():
    logging.debug("Starting main process...")

    if not MAL_USERNAME:
        logging.critical("No MAL_USERNAME set.")
        sys.exit(1)

    update_site("mal-badges", "https://www.mal-badges.com/users", "/update")
    update_site("anime.plus", "https://anime.plus", "?referral=search") # /queue-add

if __name__ == "__main__":
    main()
