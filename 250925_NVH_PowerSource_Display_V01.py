import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="NVH Plot Viewer",
    page_icon="📊",
    layout="wide"
)
# --- GitHub URL Configuration ---
# IMPORTANT: Replace these with your GitHub username and repository name
GITHUB_USERNAME = "meliaph-monitech"
GITHUB_REPO = "NVH_PowerSource_Plotly_Viz"
# This is the path to your manifest file and plots folder in the repo
# Since your files are in the root of the repository, this should be empty.
PATH_TO_DATA = "" 

# Construct the base URL for raw content
base_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/{PATH_TO_DATA}"
# --- Data Loading ---
@st.cache_data
def load_manifest():
    manifest_url = f"{base_url}/manifest.csv"
    try:
        df = pd.read_csv(manifest_url)
        return df
    except Exception as e:
        st.error(f"Could not load manifest file from GitHub. Please check your username, repo, and file path.")
        st.error(e)
        return pd.DataFrame() # Return empty df on error

manifest_df = load_manifest()

# --- App ---
st.title("📊 NVH Power Source & Plasma Data Viewer")
st.markdown("Use the filters on the left to select and view the generated plots.")

if not manifest_df.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    
    # Get unique values for filters from the manifest
    unique_dates = sorted(manifest_df['date'].unique(), reverse=True)
    unique_status1 = sorted(manifest_df['status1'].unique())
    unique_status2 = sorted(manifest_df['status2'].unique())
    unique_shuttles = sorted(manifest_df['shuttle'].unique())

    # Create the widgets
    selected_date = st.sidebar.selectbox("Select Date (YYMMDD)", unique_dates)
    
    # Filter for the selected date first to make other selections faster
    date_filtered_df = manifest_df[manifest_df['date'] == selected_date]
    
    selected_status1 = st.sidebar.multiselect("Select Machine Status 1", sorted(date_filtered_df['status1'].unique()))
    selected_status2 = st.sidebar.multiselect("Select Machine Status 2", sorted(date_filtered_df['status2'].unique()))
    selected_shuttles = st.sidebar.multiselect("Select Shuttle(s)", sorted(date_filtered_df['shuttle'].unique()))
    
    # --- Filtering Logic ---
    filtered_plots = date_filtered_df.copy()
    if selected_status1:
        filtered_plots = filtered_plots[filtered_plots['status1'].isin(selected_status1)]
    if selected_status2:
        filtered_plots = filtered_plots[filtered_plots['status2'].isin(selected_status2)]
    if selected_shuttles:
        filtered_plots = filtered_plots[filtered_plots['shuttle'].isin(selected_shuttles)]

    # --- Display Plots ---
    if not filtered_plots.empty:
        st.header(f"Displaying {len(filtered_plots)} Plot(s) for {selected_date}")
        for _, row in filtered_plots.iterrows():
            plot_url = f"{base_url}/plot_outputs/{row['filename']}"
            
            st.subheader(f"Plot: {row['status1']}_{row['status2']} on Shuttle {row['shuttle']}")
            st.components.v1.iframe(plot_url, height=600, scrolling=True)
            st.markdown("---") # Separator
    else:
        st.warning("No plots match the selected filter criteria.")
else:
    st.warning("Manifest file is empty or could not be loaded.")
