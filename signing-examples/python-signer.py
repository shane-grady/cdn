"""
Python ECDSA Signature Implementation for LIAM API

This script provides functions to sign requests using ECDSA SHA256
for authentication with the LIAM API.

Dependencies:
  pip install cryptography requests
"""

import json
import base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend


def sign_request(request_body, private_key_pem):
    """
    Sign a request body with ECDSA SHA256

    Args:
        request_body (dict or str): The request body to sign
        private_key_pem (str): PEM formatted private key

    Returns:
        str: Base64 encoded DER signature
    """
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode() if isinstance(private_key_pem, str) else private_key_pem,
        password=None,
        backend=default_backend()
    )

    # Convert request body to JSON string if it's a dict
    payload = json.dumps(request_body, separators=(',', ':')) if isinstance(request_body, dict) else request_body

    # Sign with ECDSA SHA256 (DER format is default)
    signature = private_key.sign(
        payload.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )

    # Convert to base64
    return base64.b64encode(signature).decode('utf-8')


def make_authenticated_request(endpoint, payload, api_key, private_key):
    """
    Make an authenticated request to LIAM API

    Args:
        endpoint (str): API endpoint (e.g., 'memory/create')
        payload (dict): Request payload
        api_key (str): Your API key
        private_key (str): Your private key (PEM format)

    Returns:
        dict: API response
    """
    # Sign the request
    signature = sign_request(payload, private_key)

    # Make the API request
    url = f"https://api.liam.netxd.com/api/{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'apiKey': api_key,
        'signature': signature
    }

    response = requests.post(url, json=payload, headers=headers)

    # Check for errors
    if response.status_code >= 400:
        print(f"API Error: {response.status_code}")
        print(response.json())
        response.raise_for_status()

    return response.json()


def create_user_profile(name, identification, api_key, private_key):
    """
    Create a new user profile (auto-generates userkey)

    Args:
        name (str): User's name
        identification (str): Unique identifier for the user
        api_key (str): Your API key
        private_key (str): Your private key

    Returns:
        str: Auto-generated userkey
    """
    payload = {
        "name": name,
        "identification": identification,
        "identificationType": "UNIQUE_ID"
    }

    result = make_authenticated_request(
        'auth/create-profile',
        payload,
        api_key,
        private_key
    )

    return result['data']['userkey']


def create_memory(user_key, content, tag, session_id, api_key, private_key):
    """
    Create a memory for a user

    Args:
        user_key (str): User's key
        content (str): Memory content
        tag (str): Memory tag
        session_id (str): Session ID
        api_key (str): Your API key
        private_key (str): Your private key

    Returns:
        dict: API response
    """
    payload = {
        "userKey": user_key,
        "content": content,
        "tag": tag or "",
        "sessionId": session_id
    }

    return make_authenticated_request(
        'memory/create',
        payload,
        api_key,
        private_key
    )


def list_memories(user_key, query="", tokens=None, api_key="", private_key=""):
    """
    List memories for a user

    Args:
        user_key (str): User's key
        query (str): Search query
        tokens (list): Search tokens
        api_key (str): Your API key
        private_key (str): Your private key

    Returns:
        dict: API response with memories
    """
    payload = {
        "userKey": user_key,
        "query": query,
        "tokens": tokens or []
    }

    return make_authenticated_request(
        'memory/list',
        payload,
        api_key,
        private_key
    )


def forget_memory(user_key, query_hash, api_key, private_key):
    """
    Delete a memory

    Args:
        user_key (str): User's key
        query_hash (str): Hash of the memory to delete
        api_key (str): Your API key
        private_key (str): Your private key

    Returns:
        dict: API response
    """
    payload = {
        "userKey": user_key,
        "queryHash": query_hash
    }

    return make_authenticated_request(
        'memory/forget',
        payload,
        api_key,
        private_key
    )


def list_tags(user_key, api_key, private_key):
    """
    List all tags for a user

    Args:
        user_key (str): User's key
        api_key (str): Your API key
        private_key (str): Your private key

    Returns:
        dict: API response with tags
    """
    payload = {
        "userKey": user_key
    }

    return make_authenticated_request(
        'memory/list-tag',
        payload,
        api_key,
        private_key
    )


# Example usage
if __name__ == "__main__":
    # Your credentials
    API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0'
    PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----"""

    try:
        # Create a user
        print("Creating user...")
        user_key = create_user_profile(
            'John Doe',
            'unique_user_456',
            API_KEY,
            PRIVATE_KEY
        )
        print(f"User created! UserKey: {user_key}")

        # Create a memory
        print("\nCreating memory...")
        memory_result = create_memory(
            user_key,
            'I love Italian food',
            'preferences',
            '2025020300001',
            API_KEY,
            PRIVATE_KEY
        )
        print(f"Memory created: {memory_result}")

        # List memories
        print("\nListing memories...")
        memories = list_memories(
            user_key,
            'food',
            [],
            API_KEY,
            PRIVATE_KEY
        )
        print(f"Memories: {json.dumps(memories, indent=2)}")

        # List tags
        print("\nListing tags...")
        tags = list_tags(user_key, API_KEY, PRIVATE_KEY)
        print(f"Tags: {tags}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
