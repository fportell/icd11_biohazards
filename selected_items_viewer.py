import json
import streamlit as st

# Specify the list of JSON files to load
JSON_FILES = ["./databases/aetiology.json", "./databases/antimicrobial_resistance.json", "./databases/infectious_agents.json", "./databases/infectious_and_vectorborne.json", "./databases/opioids.json"]


# Load JSON from a file path
def load_hierarchy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Flatten the hierarchy into a list of tuples (code, name, URL, full data)
def flatten_hierarchy(data):
    flattened = []
    if isinstance(data, dict):
        # Only consider entries where "gphin" is true
        if data.get("gphin", True):
            code = data.get("code", "N/A")
            title = data.get("title", "Unknown")
            icdurl = data.get("icdurl", "#")
            flattened.append((code, title, icdurl, data))

        for child in data.get("child", []):  # Process children recursively
            flattened.extend(flatten_hierarchy(child))
    return flattened


# Main app

if 'app_ID' not in st.session_state:
    st.session_state.app_ID = ''

st.session_state.app_ID = 'VIEW'


st.title("Hazard selection (ICD-11)")

try:
    all_data = []
    for file_path in JSON_FILES:
        # Load each JSON file
        data = load_hierarchy(file_path)
        if not isinstance(data, dict):  # Ensure each JSON root is a dictionary
            raise ValueError(f"File {file_path} has an invalid format.")
        all_data.extend(flatten_hierarchy(data))

    if all_data:
        st.success("All JSON files loaded and processed successfully!")
    else:
        st.warning("No valid data found in the specified files.")

except Exception as e:
    st.error(f"Error processing JSON files: {e}")

# Prepare display options for the multiselect
display_options = [f"{code} {title}" for code, title, _, _ in all_data]

# Display a multiselect box for the user to choose one or more items
selected_items = st.multiselect(
    "Select one or more items:",
    all_data,
    format_func=lambda x: f"{x[0]} {x[1]}" if x else "Unknown",
)

if selected_items:
    st.subheader("Selected hazard:")
    for code, title, icdurl, _ in selected_items:
        # Render the selected items with hyperlinks
        st.markdown(f"- **{code}**: [{title}]({icdurl})")
