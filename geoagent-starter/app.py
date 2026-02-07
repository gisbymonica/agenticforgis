import os
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from agents.spatial_navigator import agent_executor # Importing your brain

st.set_page_config(page_title="Agentic GIS Portal", layout="wide")

st.title("🗺️ Agentic GIS Control Center")
st.markdown("### Moving from Static ETL to Autonomous Spatial Reasoning")
m = leafmap.Map(center=[0, 0], zoom=2)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("Settings")
    
    # Try to read API key from environment variables or Streamlit secrets
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ API Key loaded from environment")
        else:
            api_key = st.text_input("API Key (optional - will use environment if available)", type="password")
            if not api_key:
                st.warning("⚠️ No API key found. Will use default configuration.")
    except:
        api_key = st.text_input("API Key", type="password")
    
    uploaded_file = st.file_uploader("Upload Source GIS Data", type=['geojson', 'shp', 'zip'])
    if uploaded_file:
    # Save the file to the data/ directory for the agent to access
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded to {save_path}")
        m.add_geojson(save_path, layer_name="Original (Broken)", 
                  style={'color': 'red', 'fillOpacity': 0.3})
    st.info("The agent will automatically handle CRS mismatches and schema drift. It would also check for any topology errors and fix them.")

# --- Main Layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("The Agent's Thought Process")
    user_prompt = st.text_area("What is your spatial task?", 
                                placeholder="e.g., 'Check if these fire hydrants fall within the flood zone. If the CRS is wrong, fix it.'")
    
    if st.button("Execute Task"):
        if not api_key:
            st.error("Please enter an API key.")
        else:
            with st.spinner("Agent is reasoning..."):
                
                if user_prompt and uploaded_file:
                    # We pass the filename clearly in the query to help the agent
                    save_path = './data/' + uploaded_file.name
                    full_query = f"Using the file at {save_path}, {user_prompt}"
                    print(f"Test Action: Uploaded file saved to {save_path}")
                    response = agent_executor.invoke({"messages": [("user", full_query)]})
                    st.success("Task Completed")
                    st.markdown("### Agent Output")
                    st.write(response["messages"][-1].content)

                    # Check if a new 'fixed' WZfile was created to offer a download
                    fixed_path = save_path.replace(".geojson", "_fixed.geojson")
                    if os.path.exists(fixed_path):
                        m.add_geojson(fixed_path, layer_name="Fixed Data", style={'color': 'green', 'fillOpacity': 0.3})
                        with open(fixed_path, "rb") as f:
                            st.download_button("Download Repaired File", f, file_name="fixed_data.geojson")
                else:
                    st.warning("Please upload a file and enter a prompt.")

with col2:
    st.subheader("Spatial Output")
    
    m.to_streamlit(height=500)

st.divider()
st.caption("Built by Monica for Spatial Architects | Part of the Agentic Journey Series")