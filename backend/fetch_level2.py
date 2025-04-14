# backend/fetch_level2.py
import boto3
import os
from datetime import datetime, timedelta

def fetch_latest_level2(radar_site: str = 'KTLH') -> str | None:
    try:
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket = 'noaa-nexrad-level2'
        # Use the most recent date (try today and work backwards)
        current_date = datetime.now(tz=datetime.UTC)  # Fix deprecation warning
        for i in range(7):  # Try the last 7 days
            date = (current_date - timedelta(days=i)).strftime('%Y/%m/%d')
            prefix = f'{date}/{radar_site}/'
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if 'Contents' in response and len(response['Contents']) > 0:
                # Found data for this date
                latest_file = max(response['Contents'], key=lambda x: x['LastModified'])['Key']
                local_file = f'data/{latest_file.split("/")[-1]}'
                # Check if file already exists
                if os.path.exists(local_file):
                    return local_file
                # Ensure directory exists
                os.makedirs('data', exist_ok=True)
                s3.download_file(bucket, latest_file, local_file)
                return local_file
        print("No recent Level II data found for the last 7 days")
        return None
    except Exception as e:
        print(f"Error fetching Level II data: {e}")
        return None

if __name__ == '__main__':
    print(fetch_latest_level2())