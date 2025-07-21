import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import re



# ---- Load credentials from secrets ----
hostname = "interact.interpublic.com"
client_id = st.secrets["AI_CLIENT_ID"]
client_secret = st.secrets["AI_CLIENT_SECRET"]
token_endpoint_path = "/api/token"
application_id = "test"

# ---- Get access token ----
def get_access_token():
    token_url = f"https://{hostname}{token_endpoint_path}"
    try:
        response = requests.post(
            token_url,
            auth=(client_id, client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={'grant_type': 'client_credentials'}
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        st.error(f"Error obtaining token: {e}")
        return None


def normalize_answer_for_comparison(answer_value):
    """
    Helper function to normalize answers consistent with agent's rules.
    Used for both CSV answers and Recommendation Set answers.
    """
    if pd.isna(answer_value):
        return ""

    normalized_val = str(answer_value).lower().strip()

    if normalized_val == 'n/a' or normalized_val == '':
        return ""

    return normalized_val

# ---- Make API call ----
def call_category_summary_api(payload):
    url = "https://interact.interpublic.com/api/chat-ai/v1/bots/be55b625-70c3-44cd-82e0-8c5de53ca0fd/messages"
    token = get_access_token()
    if not token:
        return None
    headers = {
        'Authorization': f'Bearer {token}',
        'X-APPLICATION-ID': application_id,
        'Content-Type': 'application/json'
    }
    request_body = {
        "files": [],
        "message": payload
    }
    try:
        response = requests.post(url, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

def call_bullet_summary_api(payload):
    url = "https://interact.interpublic.com/api/chat-ai/v1/bots/dc5605d1-cd9f-4a99-8de9-3667ae319d78/messages"
    token = get_access_token()
    if not token:
        return None
    headers = {
        'Authorization': f'Bearer {token}',
        'X-APPLICATION-ID': application_id,
        'Content-Type': 'application/json'
    }
    request_body = {
        "files": [],
        "message": payload
    }
    try:
        response = requests.post(url, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

def call_maturity_gap_api(payload):
    url = "https://interact.interpublic.com/api/chat-ai/v1/bots/1c5f5ea4-0000-4536-af03-ba0e3b493aab/messages"
    token = get_access_token()
    if not token:
        return None
    headers = {
        'Authorization': f'Bearer {token}',
        'X-APPLICATION-ID': application_id,
        'Content-Type': 'application/json'
    }
    request_body = {
        "files": [],
        "message": payload
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None



def parse_response(response_text):
    gaps = []
    gap_entries = re.split(r'\n\d+\.\s+\*\*Heading\*\*:', response_text)

    for entry in gap_entries[1:]:
       heading_match = re.search(r'^(.*?)\n\s*\*\*Context\*\*\:', entry.strip(), re.DOTALL)
       context_match = re.search(r'\*\*Context\*\*\:\s*(.*?)\n\s*\*\*Impact\*\*\:', entry.strip(), re.DOTALL)
       impact_match = re.search(r'\*\*Impact\*\*\:\s*(.*)', entry.strip(), re.DOTALL)

       gaps.append({
            "Heading": heading_match.group(1).strip() if heading_match else "N/A",
            "Context": context_match.group(1).strip() if context_match else "N/A",
            "Impact": impact_match.group(1).strip() if impact_match else "N/A"
     })

    if not gaps:
        st.warning("No matching entries found in the response.")
    return pd.DataFrame(gaps)