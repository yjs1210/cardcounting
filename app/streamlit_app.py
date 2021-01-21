import streamlit as st
import numpy as np
import os, urllib
import sys
import plotly.graph_objects as go
from scipy import stats
import scipy.stats
import statsmodels.stats.api as sms
import pickle


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return m, m - h, m + h


ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from simulator import hard_policy, soft_policy, split_policy, betting_policy
from blackjack import (
    Actions,
    Cards,
    Deck,
    Player,
    resolve_player_action,
    Hand,
    PlayerResultTypes,
    resolve_dealer_action,
    DealerResultTypes,
    play,
    resolve_environment,
    parallel_processing,
)

# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Show Instructions", "Show Cached Scenarios", "Run Custom Simulation"],
    )
    if app_mode == "Show Instructions":
        st.sidebar.success(
            'To continue select "Show Cached Scenarios or Run Simulation".'
        )
    elif app_mode == "Show Cached Scenarios":
        readme_text.empty()
        show_cached()
    elif app_mode == "Run Custom Simulation":
        readme_text.empty()
        run_sims()


def show_cached():
    st.sidebar.success("To continue select one of the pre-computed simulations.")
    scenarios = st.sidebar.selectbox(
        "Choose a Cached Scenario",
        ["Vegas Rules Aggressive Betting", "Vegas Rules Conservative Betting"],
    )
    if scenarios == "Vegas Rules Aggressive Betting":
        st.markdown(
            "Below is a result of 5000 session samples of 1000 hands under standard Las Vegas Rules(hit soft 17 and late surrender allowed). Bet sizes employed are $25 for counts of 0 and negatives, and multipliers of 8 for count of 1, 16 for count of 2 and 32 for count of 3+"
        )
        file = open("data/vegas_aggressive_bets_results.obj", "rb")
        results = pickle.load(file)
        results = [i * 25 for i in results]
        layout_results(results)
    if scenarios == "Vegas Rules Conservative Betting":
        st.markdown(
            "Below is a result of 5000 session samples of 1000 hands under standard Las Vegas Rules(hit soft 17 and late surrender allowed). Bet sizes employed are $25 for counts of 0 and negatives, and multipliers of 4 for count of 1, 8 for count of 2 and 16 for count of 3+"
        )
        file = open("data/vegas_conservative_bets_results.obj", "rb")
        results = pickle.load(file)
        results = [i * 25 for i in results]
        layout_results(results)


def run_sims():

    button_start = st.sidebar.button("Start Sim")
    bet_size = st.sidebar.number_input("Bet Size: ", value=1, step=1)
    num_samples = st.sidebar.number_input(
        "Number of Sessions: ", min_value=1, max_value=1000, value=100, step=1
    )
    iterations = st.sidebar.number_input(
        "Number of Hands per Session: ",
        min_value=1,
        max_value=10000,
        value=1000,
        step=1,
    )
    num_decks = st.sidebar.number_input(
        "Number of decks in a shoe: ", min_value=1, max_value=8, value=6, step=1
    )
    cut_card_threshhold = st.sidebar.number_input(
        "Dealer Cut Card Proportion",
        min_value=0.01,
        max_value=0.5,
        value=0.35,
        step=0.01,
    )

    bet_multipler_neg = st.sidebar.slider(
        "Betting multiplier for count of 0 and negatives", 0, 100, 1
    )
    bet_multiplier_1 = st.sidebar.slider("Betting multiplier for count of 1", 1, 100, 8)
    bet_multiplier_2 = st.sidebar.slider(
        "Betting multiplier for count of 2", 1, 100, 16
    )
    bet_multiplier_3 = st.sidebar.slider(
        "Betting multiplier for count of 3", 1, 100, 32
    )
    bet_multiplier_4 = st.sidebar.slider(
        "Betting multiplier for count of 4", 1, 100, 32
    )
    bet_multiplier_5 = st.sidebar.slider(
        "Betting multiplier for count of 5+", 1, 100, 32
    )

    if button_start:
        wager_amts = [
            bet_multipler_neg,
            bet_multipler_neg,
            bet_multipler_neg,
            bet_multiplier_1,
            bet_multiplier_2,
            bet_multiplier_3,
            bet_multiplier_4,
            bet_multiplier_5,
        ]
        ranges = [0, 0, 1, 2, 3, 4, 5]
        betting_policy = (wager_amts, ranges)
        try:
            warning = st.warning("Running simulations. Please hold...")
            progress_bar = st.progress(0)
            chunks = run_in_chunks(num_samples, 10)
            final_results = []
            for idx, n_samples_small in enumerate(chunks):
                player = Player(
                    bankroll=1000,
                    hard_policy=hard_policy,
                    soft_policy=soft_policy,
                    split_policy=split_policy,
                    betting_policy=betting_policy,
                )
                results = parallel_processing(
                    player,
                    num_decks=num_decks,
                    iterations=iterations,
                    n_samples=n_samples_small,
                    threshold=cut_card_threshhold,
                )
                final_results = final_results + results
                progress_bar.progress(min(idx / len(chunks), 1.0))
            final_results = [i * bet_size for i in final_results]
            layout_results(final_results)

        finally:
            if warning is not None:
                warning.empty()
            if progress_bar is not None:
                progress_bar.empty()


def layout_results(final_results):
    statistics, p_value = run_t_test(final_results)
    mean, conf_low, conf_high = get_conf_interval(final_results, 0.9)
    result = "Likely Profitable" if mean > 0 else "Likely Not profitable"
    st.markdown("## Simulation Result: {}".format(result))
    draw_plotly_histogram(final_results)
    st.markdown("Average Profits per Session: ${}".format(round(mean, 2)))
    st.markdown("One-tailed test p-value: {}".format(round(p_value, 3)))
    st.markdown(
        "90% Confidence Interval: [{}, {}]".format(
            round(conf_low, 3), round(conf_high, 3)
        )
    )
    draw_plotly_boxplot(final_results)
    st.markdown("Most Profitable Session: ${}".format(round(np.max(final_results), 2)))
    st.markdown("Median Session: ${}".format(round(np.median(final_results), 2)))
    st.markdown("Least Profitable Session: ${}".format(round(np.min(final_results), 2)))


def run_in_chunks(num: int, divisor: int):
    quotient, remainder = divmod(num, divisor)
    return (
        [divisor] * quotient + [remainder] if remainder != 0 else [divisor] * quotient
    )


def draw_plotly_histogram(results):
    fig = go.Figure(data=[go.Histogram(x=results)])
    fig.update_layout(
        title_text="Sampled Results",  # title of plot
        title_x=0.5,
        xaxis_title_text="Profit($)",  # xaxis label
        yaxis_title_text="Frequency",  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
    )
    st.plotly_chart(fig, use_container_width=True)


def draw_plotly_boxplot(results):
    fig = go.Figure(
        data=[
            go.Box(
                y=results,
                boxpoints="all",  # can also be outliers, or suspectedoutliers, or False
                jitter=0.3,  # add some jitter for a better separation between points
                pointpos=-1.8,  # relative position of points wrt box
            )
        ]
    )
    fig.update_layout(title_text="Profits($)", xaxis_title="Distribution", title_x=0.5)

    st.plotly_chart(fig, use_container_width=True)


def run_t_test(final_results):
    return stats.ttest_1samp(final_results, 0, alternative="greater")


def get_conf_interval(final_results, confidence=0.95):
    a = 1.0 * np.array(final_results)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return m, m - h, m + h


@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = "https://raw.githubusercontent.com/yjs1210/cardcounting/master/app/" + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


if __name__ == "__main__":
    main()
