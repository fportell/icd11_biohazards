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
    """
    Callback function that updates `gphin` status in the full JSON structure
    and saves the entire JSON file, ensuring only the selected entry is modified.
    """
    # Update the specific entry in full_data without losing the structure
    entry_ref["gphin"] = st.session_state[unique_key]
    
    # Save the full JSON structure
    save_json(full_data, file_path)

# Recursive function to process the JSON hierarchy
def process_hierarchy(data, full_data, file_path, prefix=""):
    """
    Recursively display and edit JSON data, handling both dictionaries and lists.
    """
    if isinstance(data, dict):
        # Display fields if they exist
        code = data.get("code", "N/A")
        title = data.get("title", "Unknown")
        icdurl = data.get("icdurl", "#")
        gphin = data.get("gphin", False)

        # Create a unique key for Streamlit widgets
        unique_key = prefix + (code or "root")

        # Use Streamlit columns to display title and radio buttons horizontally
        col1, col2 = st.columns([5, 2])  # First column larger for hazard details

        with col1:
            # Display the hazard title with clickable ICD URL
            st.markdown(f"**{code}**: [{title}]({icdurl})")

        with col2:
            # Use radio buttons inline with automatic saving on change
            status = st.radio(
                "Status",
                options=["Accept", "Reject"],
                index=0 if gphin else 1,
                key=unique_key,
                horizontal=True,
                on_change=update_status,  # Trigger save function on change
                args=(unique_key, full_data, file_path, data),
            )

        # Process nested children if they exist
        for i, child in enumerate(data.get("child", [])):
            st.write("---")  # Add a separator
            process_hierarchy(child, full_data, file_path, prefix=f"{unique_key}_child_{i}")

    elif isinstance(data, list):
        # Iterate through each item in the list
        for i, item in enumerate(data):
            st.write(f"### Entry {i + 1}")
            process_hierarchy(item, full_data, file_path, prefix=f"{prefix}_list_{i}")

# main
if 'app_ID' not in st.session_state:
        st.session_state.app_ID = ''

st.session_state.app_ID = 'SORT'


st.title("ICD JSON File Manager")

# List JSON files in the host directory
try:
    json_files = [f for f in os.listdir(JSON_DIRECTORY) if f.endswith(".json")]
except FileNotFoundError:
    st.error(f"Directory '{JSON_DIRECTORY}' not found.")

if not json_files:
    st.warning("No JSON files found in the specified directory.")

# Dropdown to select a JSON file
selected_file = st.selectbox("Select a JSON file:", json_files)

if selected_file:
    file_path = os.path.join(JSON_DIRECTORY, selected_file)
    try:
        # Load the selected JSON file
        data = load_json(file_path)
        st.success(f"Loaded '{selected_file}' successfully!")

        # Display and edit the JSON hierarchy
        st.header("Manage hazard list:")
        process_hierarchy(data, data, file_path)  # Pass full_data for reference

    except Exception as e:
        st.error(f"Error processing the JSON file: {e}")