import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
load_dotenv()


DATASET_ID = os.getenv("DATASET_ID")

def _make_api_request(url, json=None):

    api_key = os.getenv("BRIGHTDATA_API_KEY")


    headers = {
        "Authorization":f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=json
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e :
        print(f"Unkown Error: {e}")
        return None
    


def serp_search(query, engine="google"):
    if engine == "google":
        base_url = f"https://www.google.com/search"

    elif engine == "bing":
        base_url = f"https://www.bing.com/search"

    else:
        raise ValueError(f"Unknown engine: {engine}")
    

    url = "https://api.brightdata.com/request"

    payload = {
        "zone":"serp_api1",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format":"raw"
    }

    full_response =  _make_api_request(url, json=payload)
    
    if not full_response:
        return None
    
    extracted_data = {
        "knowledge":full_response.get("knowledge",{}),
        "organic":full_response.get("organic", [])
    }
    
    print(extracted_data)
    return extracted_data


def _trigger_and_download_snapshot(trigger_url, params, data, operation='operation'):

    trigger_result = _make_api_request(trigger_url, json={"params":params, "data":data})

    if not trigger_result:
        print("Trigger request failed.")
        return None
    
    snapshot_id = trigger_result.get("snapshot_id")
    
    if not snapshot_id:
        print("No snapshot_id returned from trigger request.")
        return None
    
    #TODO : Poll the snapshot status until it's ready, then download the snapshot data.
    


def reddit_search(keyword, date="All Time", sort_by="Hot", num_of_posts=60):
    
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


    raw_data = None

    if not raw_data:
        return None
    
    #TODO : return a result
    return None
