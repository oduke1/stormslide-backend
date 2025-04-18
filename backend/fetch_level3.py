import requests
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        check_rate_limit(response)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        if response.status_code == 200:
            data = response.json()
            return {
                'success': data.get('success', False),
                'status_code': response.status_code,
                'data': data.get('response', []),
                'error': data.get('error', None)
            }
        return {
            'success': False,
            'status_code': response.status_code,
            'data': [],
            'error': f"HTTP {response.status_code}: {response.reason}"
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit exceeded for Level III data, delaying and retrying")
            time.sleep(10)  # Wait 10 seconds before retrying
            return fetch_level3_tvs(location)  # Retry the request
        logger.error(f"Error fetching Level III data: {str(e)}", exc_info=True)
        return {
            'success': False,
            'status_code': e.response.status_code if e.response else None,
            'data': [],
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error fetching Level III data: {str(e)}", exc_info=True)
        return {
            'success': False,
            'status_code': None,
            'data': [],
            'error': str(e)
        }

if __name__ == '__main__':
    result = fetch_level3_tvs()
    print(result)