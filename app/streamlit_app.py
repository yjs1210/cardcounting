import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import os, urllib, cv2


# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox("Choose the app mode",
        ["Show instructions", "Show Cached Scenarios", "Run Simulation"])
    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Show Cached Scenarios or Run Simulation".')
    elif app_mode == "Show Cached Scenarios":
        readme_text.empty()
    elif app_mode == "Run Simulation":
        readme_text.empty()
        run_sims()

def run_sims():
    
    bet_multipler_neg = st.sidebar.slider("Betting multiplier for count of 0 and negatives", 1, 100, 0)
    bet_multiplier_1 = st.sidebar.slider("Betting multiplier for count of 1", 1, 100, 0)
    bet_multiplier_2 = st.sidebar.slider("Betting multiplier for count of 2", 1, 100, 0)
    bet_multiplier_3 = st.sidebar.slider("Betting multiplier for count of 3", 1, 100, 0)
    bet_multiplier_4 = st.sidebar.slider("Betting multiplier for count of 4", 1, 100, 0)
    bet_multiplier_5 = st.sidebar.slider("Betting multiplier for count of 5+", 1, 100, 0)

if __name__ == "__main__":
    main()