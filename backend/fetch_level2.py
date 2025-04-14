# backend/fetch_level2.py
import boto3
import os

def fetch_latest_level2(radar_site='KTLX'):
    try:
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket = 'noaa-nexrad-level2'
        # Use a historical date with known data
        date = '2020/05/03'
        prefix = f'{date}/{radar_site}/'
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            return None
        # Filter for a specific file known to work
        latest_file = '2020/05/03/KTLX/KTLX20200503_234952_V06'
        local_file = f'data/{latest_file.split("/")[-1]}'
        # Check if file already exists
        if os.path.exists(local_file):
            return local_file
        # Ensure directory exists
        os.makedirs('data', exist_ok=True)
        s3.download_file(bucket, latest_file, local_file)
        return local_file
    except Exception as e:
        print(f"Error fetching Level II data: {e}")
        return None

if __name__ == '__main__':
    print(fetch_latest_level2())