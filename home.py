import streamlit as st

if 'app_ID' not in st.session_state:
    st.session_state.app_ID = ''

st.session_state.app_ID = 'HOME'

navigator = st.navigation(
  [
    st.Page(
      "selected_items_viewer.py",
      default=True
    ),
    st.Page(
      "json_manager.py"
    )
  ]
)

navigator.run()
