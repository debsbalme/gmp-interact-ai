import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

st.set_page_config(page_title="Interact API CSV Uploader", layout="centered")
st.title("📄 CSV to Interact API")

# ---- Load credentials from secrets ----
hostname = "interact.interpublic.com"
client_id = st.secrets["AI_CLIENT_ID"]
client_secret = st.secrets["AI_CLIENT_SECRET"]
token_endpoint_path = "/api/token"
api_endpoint_path = "https://interact.interpublic.com/api/chat-ai/v1/bots/be55b625-70c3-44cd-82e0-8c5de53ca0fd/messages"
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

# ---- Make API call ----
def call_interact_api(message_payload):
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
        "message": message_payload
    }

    try:
        response = requests.post(api_endpoint_path, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

# ---- Upload CSV and Process ----
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded CSV Preview")
        st.dataframe(df.head())

        subset = df[df["Category"] != "Business"]
        subset_data = subset[['Category', 'Question', 'Answer']]
        message_payload = subset_data.replace({np.nan: ''}).to_csv(sep='\t', index=False, header=True)

        st.subheader("📡 Sending Data to API...")
        api_response = call_interact_api(message_payload)

        if api_response:
            st.success("✅ API call successful!")
            if "message" in api_response:
                st.text_area("📬 API Response Message", api_response["message"], height=300)
            else:
                st.json(api_response)
        else:
            st.error("❌ API call failed.")
    except Exception as e:
        st.error(f"Error processing file: {e}")