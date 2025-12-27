import streamlit as st
from legacy.modules import grammar_practice, admin_standards, learning_mode, add_passage, view_history

st.set_option("client.showErrorDetails", True)
# ---------- Streamlit Page Config ----------
st.set_page_config(
    page_title="Homework Helper",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Sidebar Navigation ----------
st.sidebar.title("📚 Homework Helper")
menu = st.sidebar.radio(
    "Navigation",
    ["Learning Mode", "View History", "Add Passage", "Grammar Practice", "Admin"],
    help="Choose what you'd like to do today!"
)

# ---------- Page Routing ----------
if menu == "Learning Mode":
    learning_mode.show()
elif menu == "View History":
    view_history.show()
elif menu == "Add Passage":
    add_passage.show()
elif menu == "Grammar Practice":
    grammar_practice.show()
elif menu == "Admin":
    admin_standards.show()


# ---------- Sidebar Footer ----------
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ for learning :blue[together].")
# st.sidebar.