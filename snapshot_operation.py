import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional


load_dotenv()


def _safe_parse_json(response: requests.Response) -> Optional[Dict[str, Any]]:
    """Safely parse a single-object JSON response body.
    Returns None if the body is empty or unparseable.
    """
    raw_text = response.text.strip()
    if not raw_text:
        print(f"API returned an empty response body (HTTP {response.status_code}).")
        return None
    try:
        return response.json()
    except Exception as e:
        print(f"Failed to parse JSON response: {e}. Body: {raw_text[:200]}")
        return None


def _parse_ndjson(response: requests.Response) -> Optional[List[Dict[str, Any]]]:
    """Parse a Newline-Delimited JSON (NDJSON) response body.

    BrightData's snapshot download endpoint returns one JSON object per line
    rather than a single JSON array. This function reads each non-empty line
    and deserialises it independently, collecting the results into a list.

    Returns None if the body is empty; skips lines that cannot be parsed.
    """
    import json
    raw_text = response.text.strip()
    if not raw_text:
        print(f"API returned an empty response body (HTTP {response.status_code}).")
        return None

    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Skipping malformed NDJSON line {line_no}: {e}. Content: {line[:120]}")

    if not records:
        print("NDJSON body contained no valid records.")
        return None

    return records


def poll_snapshot_status(snapshot_id: str, max_attemps: int = 30, delay: int = 15) -> bool:
    """Poll BrightData snapshot status until ready, failed, or max attempts reached."""

    api_key = os.getenv("BRIGHTDATA_API_KEY")
    if not api_key:
        print("ERROR: BRIGHTDATA_API_KEY is not set in environment variables.")
        return False

    progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for attempt in range(max_attemps):
        try:
            print(f"Polling snapshot status (Attempt {attempt + 1}/{max_attemps})...")

            response = requests.get(progress_url, headers=headers, timeout=30)

            if response.status_code == 401:
                print("ERROR: Unauthorized (401) — check your BRIGHTDATA_API_KEY.")
                return False

            response.raise_for_status()

            progress_data = _safe_parse_json(response)
            if progress_data is None:
                time.sleep(delay)
                continue

            status = progress_data.get("status")

            if status == "ready":
                print("Snapshot is ready.")
                return True
            elif status == "failed":
                print(f"Snapshot creation failed. Details: {progress_data}")
                return False
            elif status in ("running", "pending", "initializing"):
                records = progress_data.get("records_collected", "?")
                print(f"Snapshot is still {status} ({records} records so far). Waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"Unknown status '{status}'. Full response: {progress_data}. Waiting {delay}s...")
                time.sleep(delay)

        except requests.exceptions.Timeout:
            print(f"Request timed out on attempt {attempt + 1}. Retrying in {delay}s...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Error while polling snapshot status: {e}")
            time.sleep(delay)
        except Exception as e:
            print(f"Unknown error while polling snapshot status: {e}")
            time.sleep(delay)

    print("Snapshot polling timed out after max attempts.")
    return False

def download_snapshot(snapshot_id: str) -> Optional[List[Dict[str, Any]]]:
    """Download the completed BrightData snapshot data.

    The endpoint returns NDJSON (one JSON object per line), so the result is
    always a list of records.
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    if not api_key:
        print("ERROR: BRIGHTDATA_API_KEY is not set in environment variables.")
        return None

    download_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        print("Downloading snapshot...")
        # stream=True so large responses are not buffered all at once
        response = requests.get(download_url, headers=headers, stream=True, timeout=120)

        if response.status_code == 401:
            print("ERROR: Unauthorized (401) — check your BRIGHTDATA_API_KEY.")
            return None

        response.raise_for_status()

        # BrightData returns NDJSON — one record per line
        data = _parse_ndjson(response)
        if data is not None:
            print(f"Successfully downloaded snapshot data ({len(data)} records).")
        return data

    except requests.exceptions.Timeout:
        print("Snapshot download timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading snapshot: {e}")
        return None
    except Exception as e:
        print(f"Unknown error while downloading snapshot: {e}")
        return None

            