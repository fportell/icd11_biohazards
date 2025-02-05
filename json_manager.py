import json
import os
import streamlit as st

# Specify the directory on the host containing the JSON files
JSON_DIRECTORY = "./databases"

# Load the JSON file
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Save the full JSON structure
def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Function to handle radio button change and save automatically
def update_status(unique_key, full_data, file_path, entry_ref):
    """ Updates `gphin` status in the JSON file while preserving hierarchy. """
    entry_ref["gphin"] = st.session_state[unique_key]
    save_json(full_data, file_path)

# Recursive function to process and display JSON hierarchy with indentation
def process_hierarchy(data, full_data, file_path, depth=0, prefix=""):
    """
    Recursively display JSON data with indentation based on hierarchy depth.
    """
    indent = "&nbsp;" * depth * 4  # Indentation using HTML non-breaking spaces

    if isinstance(data, dict):
        code = data.get("code", "N/A")
        title = data.get("title", "Unknown")
        icdurl = data.get("icdurl", "#")
        gphin = data.get("gphin", False)

        unique_key = prefix + (code or "root")

        # Use columns for better formatting
        col1, col2 = st.columns([5, 2])

        with col1:
            # Display indented hazard title with clickable ICD URL
            st.markdown(f"{indent}**{code}**: [{title}]({icdurl})", unsafe_allow_html=True)

        with col2:
            # Radio button for status selection
            st.radio(
                "Status",
                options=["Accept", "Reject"],
                index=0 if gphin else 1,
                key=unique_key,
                horizontal=True,
                on_change=update_status,
                args=(unique_key, full_data, file_path, data),
            )

        # Process nested children with increased depth
        for i, child in enumerate(data.get("child", [])):
            process_hierarchy(child, full_data, file_path, depth + 2, prefix=f"{unique_key}_child_{i}")

    elif isinstance(data, list):
        # Iterate through list items with proper indentation
        for i, item in enumerate(data):
            process_hierarchy(item, full_data, file_path, depth, prefix=f"{prefix}_list_{i}")

# Main app
if 'app_ID' not in st.session_state:
    st.session_state.app_ID = ''

st.session_state.app_ID = 'SORT'

st.title("ICD JSON File Manager")

# List available JSON files
try:
    json_files = [f for f in os.listdir(JSON_DIRECTORY) if f.endswith(".json")]
except FileNotFoundError:
    st.error(f"Directory '{JSON_DIRECTORY}' not found.")
    json_files = []

if not json_files:
    st.warning("No JSON files found in the specified directory.")
else:
    selected_file = st.selectbox("Select a JSON file:", json_files)

    if selected_file:
        file_path = os.path.join(JSON_DIRECTORY, selected_file)
        try:
            data = load_json(file_path)
            st.success(f"Loaded '{selected_file}' successfully!")

            # Display and edit JSON hierarchy with indentation
            st.header("Manage Hazard List:")
            process_hierarchy(data, data, file_path, depth=0)

        except Exception as e:
            st.error(f"Error processing the JSON file: {e}")
