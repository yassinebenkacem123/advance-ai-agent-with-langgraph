import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional 


load_dotenv()


def poll_snapshot_status(snapshot_id: str, max_attemps: int = 60, delay: int = 5) -> bool:
    
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    
    progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for attempt in range(max_attemps):
        try:
            print(f"Polling snapshot status (Attempt {attempt + 1}/{max_attemps})...")

            response = requests.get(progress_url, headers=headers)

            response.raise_for_status()

            progress_data = response.json()

            status = progress_data.get("status")
            
            if status == "ready":
                print("Snapshot is ready.")
                return True
            elif status == "failed":
                print("Snapshot creation failed.")
                return False
            elif status == "running":
                print("Snapshot is still running. Waiting before next poll...")
                time.sleep(delay)
            else:
                print("Unknown status or still in progress. Waiting before next poll...")   
                time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            print(f"Error while polling snapshot status: {e}")
            time.sleep(delay)
        except Exception as e:
            print(f"Unknown error while polling snapshot status: {e}")
            time.sleep(delay)
    

def download_snapshot(snapshot_id: str, output_file: str) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    
    download_url = f"https://api.brightdata.com/datasets/v3/download/{snapshot_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Downloading snapshot to {output_file}...")
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()

        data = response.json()
        print("Successfully downloaded snapshot data.")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error while downloading snapshot: {e}")
        return None
    except Exception as e:
        print(f"Unknown error while downloading snapshot: {e}")
        return None

            