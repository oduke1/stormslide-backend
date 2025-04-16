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
    except Exception as e:
        logger.error(f"Error fetching Level III data: {e}", exc_info=True)
        return {
            'success': False,
            'status_code': None,
            'data': [],
            'error': str(e)
        }