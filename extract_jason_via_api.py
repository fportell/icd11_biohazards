import requests
import certifi
import json
import time


# Your ICD API credentials
client_id = '790fde83-5c52-448b-b681-627a309a8946_d27186e1-3bbc-4c31-a2e3-b367eb5e222a'
client_secret = 'pGTKUx0EHuSib8nHrJd/YGpWOZt2F913mtgI3EReS2Y='
token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
scope = 'icdapi_access'
grant_type = 'client_credentials'

# Get the access token
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': scope,
    'grant_type': grant_type
}
response = requests.post(token_endpoint, data=payload, verify=certifi.where())
response.raise_for_status()
token = response.json().get('access_token')

# Set headers for the GET request
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Accept-Language': 'en',  # Change language if needed
    'API-Version': 'v2'
}

def fetch_entity_data(uri):
    """Fetch entity data from the ICD API."""
    try:
        entity_response = requests.get(uri, headers=headers, verify=certifi.where())
        entity_response.raise_for_status()
        return entity_response.json()
    except requests.RequestException as e:
        print(f"Error retrieving entity information for URI {uri}: {e}")
        return None

def build_hierarchy(uri, delay=1):
    """
    Recursively build the hierarchy starting from the given URI.
    """
    entity_data = fetch_entity_data(uri)
    if not entity_data:
        return None

    # Extract relevant information
    title = entity_data.get('title', {}).get('@value', 'N/A')
    code = entity_data.get('code', 'N/A')
    icdurl = entity_data.get('browserUrl', 'N/A')
    parent = entity_data.get('parent', 'N/A')
    child_uris = entity_data.get('child', [])

    print(f"Parsing: {uri}")
    print(f"    Name: {title}")
    print(f"    Number of child: {len(child_uris)}")


    # Build the hierarchy
    hierarchy = {
        'title': title,
        'code': code,
        'uri': uri,
        'icdurl': icdurl,
        'gphin': False,
        'parent': parent,
        'child': []
    }

    # Recursively process child
    for child_uri in child_uris:
        time.sleep(delay)  # Introduce a delay before making the next API call
        child_hierarchy = build_hierarchy(child_uri)
        if child_hierarchy:
            hierarchy['child'].append(child_hierarchy)

    return hierarchy

def print_hierarchy(hierarchy, level=0):
    """
    Recursively print the hierarchy with one value per line and indentation.
    """
    if not hierarchy:
        return
    indent = "  " * level
    print(f"{indent}Name: {hierarchy['title']}, Code: {hierarchy['code']}")
    for child in hierarchy.get('child', []):
        print_hierarchy(child, level + 1)

def save_json_to_file(hierarchy, filename):
    """
    Save the hierarchy as a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, ensure_ascii=False, indent=2)

# Top-level entity URI (Infectious Agents)
# top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/437215757'

# Top-level entity URI (Opioids)
# top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/448177412'

# Top level vaccines
# top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/164949870'

# Top level for Certain infectious or parasitic diseases
# top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/1435254666'

# Top level for Aetiology
# top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/71556738'

# Top level for Finding of microorganism resistant to antimicrobial drugs (1882742628)
top_level_uri = 'http://id.who.int/icd/release/11/2024-01/mms/1882742628'



# Build the full hierarchy
full_hierarchy = build_hierarchy(top_level_uri)

# Print or save the hierarchy
# print(json.dumps(full_hierarchy, indent=2))

# Print the hierarchy in a custom format
print_hierarchy(full_hierarchy)

# Save the hierarchy to a JSON file
save_json_to_file(full_hierarchy, 'antimicrobial_resistance.json')
print("\nHierarchy saved to 'antimicrobial_resistance.json'")
