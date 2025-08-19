from components.home import show_home
from components.search_result import show_search_results

import streamlit as st

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    page = st.session_state["page"]

    if page == "home":
        show_home()
    elif page == "search":
        show_search_results()
    else:
        st.error("存在しないページです。")

if __name__ == "__main__":
    main()
