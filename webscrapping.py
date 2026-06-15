import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from snapshot_operation import poll_snapshot_status, download_snapshot

load_dotenv()


DATASET_ID = os.getenv("DATASET_ID")


def _make_api_request(url, params=None, json=None, timeout: int = 30):
    """Make a POST request to the BrightData API and safely parse the JSON response."""
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    if not api_key:
        print("ERROR: BRIGHTDATA_API_KEY is not set in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=json,
            timeout=timeout
        )

        # Log non-2xx for easier debugging
        if not response.ok:
            print(f"API request failed: HTTP {response.status_code} — {response.text[:300]}")
            response.raise_for_status()

        raw_text = response.text.strip()
        if not raw_text:
            print(f"API returned an empty response body (HTTP {response.status_code}).")
            return None

        return response.json()

    except requests.exceptions.Timeout:
        print(f"API request timed out after {timeout}s.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Unknown Error: {e}")
        return None
    


def serp_search(query, engine="google"):
    """Search Google or Bing via the BrightData SERP proxy and return organic results."""
    if engine == "google":
        base_url = "https://www.google.com/search"
    elif engine == "bing":
        base_url = "https://www.bing.com/search"
    else:
        raise ValueError(f"Unknown engine: {engine}")

    url = "https://api.brightdata.com/request"

    payload = {
        "zone": "serp_api1",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format": "raw"
    }

    # SERP requests render real pages — allow up to 120 seconds
    full_response = _make_api_request(url, json=payload, timeout=120)

    if not full_response:
        return None

    extracted_data = {
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", [])
    }

    return extracted_data


def _trigger_and_download_snapshot(trigger_url, params, data, operation='operation'):
    """Trigger a BrightData dataset snapshot, poll until ready, then download it."""

    trigger_result = _make_api_request(trigger_url, params=params, json=data, timeout=30)

    if not trigger_result:
        print("Trigger request failed.")
        return None

    snapshot_id = trigger_result.get("snapshot_id")

    if not snapshot_id:
        print(f"No snapshot_id in trigger response. Full response: {trigger_result}")
        return None

    if not poll_snapshot_status(snapshot_id):
        print("Snapshot polling failed or snapshot is not ready.")
        return None

    raw_data = download_snapshot(snapshot_id)
    return raw_data


def reddit_search_api(keyword, date="All time", sort_by="Hot", num_of_posts=40):
    
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"

    params = {
        "dataset_id": DATASET_ID,
        "include_errors":"true",
        "type":"discover_new",
        "discover_by":"keyword",

    }


    
    data = [
        {
            "keyword":keyword,
            "date":date,
            "sort_by":sort_by,
            "num_of_posts":num_of_posts
        }
    ]


    raw_data = _trigger_and_download_snapshot(
        trigger_url, 
        params, 
        data, 
        operation='reddit_search'
    )

    if not raw_data:
        return None
    

    parsed_data = []
    for item in raw_data:
        parsed_item = {
            "title": item.get("title"),
            "url": item.get("url"),        
        }
        parsed_data.append(parsed_item)

    return {
        "parsed_data": parsed_data,
        "total_found": len(parsed_data)
    }



def reddit_post_retrieval(urls, days_back=10, load_all_replies=False, comment_limit=""):
    if not urls:
        return None
    
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    params = {
        "dataset_id": "gd_lvzdpsdlw09j6t702",
        "include_errors":"true",

    }
    

    data = [
        {
            "url": url,
            "days_back": days_back,
            "load_all_replies": load_all_replies,
            "comment_limit": comment_limit
        }
        for url in urls
    ]


    raw_data = _trigger_and_download_snapshot(
        trigger_url,
        params,
        data,
        operation='reddit_post_retrieval'
    )
    if not raw_data:
        return None
    
    parsed_data = []
    for item in raw_data:
        parsed_item = {
            "comment_id": item.get("comment_id"),
            "content": item.get("comment"),
            "date": item.get("date_posted"),
        }
        parsed_data.append(parsed_item)

    return {
        "parsed_data": parsed_data,
        "total_comments": len(parsed_data)
    }
