import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import os, urllib, cv2
import sys
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from simulator import hard_policy, soft_policy, split_policy, betting_policy
from blackjack import Actions, Cards, Deck, Player, resolve_player_action, Hand, PlayerResultTypes, resolve_dealer_action, DealerResultTypes, play, resolve_environment, parallel_processing

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
    
    bet_size = st.sidebar.text_input('Bet Size: ')
    bet_multipler_neg = st.sidebar.slider("Betting multiplier for count of 0 and negatives", 1, 100, 0)
    bet_multiplier_1 = st.sidebar.slider("Betting multiplier for count of 1", 1, 100, 0)
    bet_multiplier_2 = st.sidebar.slider("Betting multiplier for count of 2", 1, 100, 0)
    bet_multiplier_3 = st.sidebar.slider("Betting multiplier for count of 3", 1, 100, 0)
    bet_multiplier_4 = st.sidebar.slider("Betting multiplier for count of 4", 1, 100, 0)
    bet_multiplier_5 = st.sidebar.slider("Betting multiplier for count of 5+", 1, 100, 0)
    button_start = st.sidebar.button('Start Sim')


    if button_start:
        results = []
        for i in range(100):
            player = Player(bankroll=10000, hard_policy=hard_policy, soft_policy=soft_policy, split_policy=split_policy, betting_policy=betting_policy)
            deck = Deck(6)
            # need a way to get deck count
            resolve_environment(player, deck, 6, 1000, .35)
            results.append(player.bankroll - 10000)
        fig, ax = plt.subplots()
        ax.hist(results, bins=20)
        st.pyplot(fig)

        

@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/yjs1210/cardcounting/master/app/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


if __name__ == "__main__":
    main()