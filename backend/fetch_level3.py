import requests
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504, 592])
session.mount('https://', HTTPAdapter(max_retries=retries))

def check_rate_limit(response):
    """Check Xweather rate-limit headers and delay if necessary."""
    remaining_minute = int(response.headers.get('X-RateLimit-Remaining-Minute', 999))
    remaining_period = int(response.headers.get('X-RateLimit-Remaining-Period', 999))
    reset_minute = response.headers.get('X-RateLimit-Reset-Minute', None)
    
    logger.info(f"Rate limits - Remaining Minute: {remaining_minute}, Remaining Period: {remaining_period}, Reset Minute: {reset_minute}")
    
    if remaining_minute <= 5:
        logger.warning("Nearing minutely rate limit, delaying request")
        time.sleep(5)

def fetch_level3_tvs(location='KTLH'):
    try:
        api_key = '2qRfyRrVeDB22pw0Z2mCbAiJrHS0G0FLVi9wLR3Z'
        client_id = 'HIXM4oS25l3yBhWDFrM4k'
        url = f'https://api.aerisapi.com/stormcells/closest?p={location}&query=tvs:1,mda:1&limit=10&client_id={client_id}&client_secret={api_key}'
        response = session.get(url, timeout=10)
        response.raise_for_status()
        check_rate_limit(response)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        data = response.json()
        return {
            'success': data.get('success', False),
            'status_code': response.status_code,
            'data': data.get('response', []),
            'error': data.get('error', None)
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit exceeded, delaying and retrying")
            time.sleep(10)
            return fetch_level3_tvs(location)
        logger.error(f"Error fetching Level III data: {e}", exc_info=True)
        return {
            'success': False,
            'status_code': e.response.status_code if e.response else None,
            'data': [],
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error fetching Level III data: {e}", exc_info=True)
        return {
            'success': False,
            'status_code': None,
            'data': [],
            'error': str(e)
        }

if __name__ == '__main__':
    result = fetch_level3_tvs()
    print(result)