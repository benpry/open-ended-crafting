"""
Interactive Message Value Analysis Visualization

This Streamlit app creates interactive visualizations of message value
by various variables like sender performance, receiver performance,
message length, etc. Hovering over data points shows the message text.

Run with: streamlit run scripts/make_streamlit_visualization.py
"""

import re
import textwrap
from glob import glob

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pyprojroot import here
from scipy import stats


def wrap_text_for_hover(text, width=60):
    """Wrap text to a maximum width, inserting <br> tags for line breaks."""
    if not isinstance(text, str):
        return str(text)
    # Use textwrap to wrap, then join with <br> for HTML
    wrapped_lines = textwrap.wrap(text, width=width, break_long_words=True)
    return "<br>".join(wrapped_lines)


@st.cache_data
def load_and_process_data():
    """Load and process all data needed for visualizations."""

    # Load simulation files to compute message values
    message_sim_files = glob(str(here("data/simulations/gameplay_message_*.csv")))
    message_sim_files = [f for f in message_sim_files if re.search(r"message_\d+", f)]

    df_all_sims = pd.DataFrame()
    for filename in message_sim_files:
        df = pd.read_csv(filename)
        df["trial_id"] = re.search(r"message_(\d+)", filename).group(1)
        df_all_sims = pd.concat([df_all_sims, df])

    # Compute average scores in each simulation
    df_scores = (
        df_all_sims[(df_all_sims["score"].notna()) & (df_all_sims["chain_pos"] == 0)]
        .sort_values("timestep")
        .groupby(["round_num", "chain_id", "trial_id"])
        .tail(1)
        .reset_index(drop=True)
    )
    df_scores = (
        df_scores.groupby(["trial_id", "chain_id"])["score"].mean().reset_index()
    )
    df_scores["trial_id"] = df_scores["trial_id"].astype(int)
    message_values = df_scores.groupby("trial_id")["score"].mean()

    # Load gameplay and messages data
    df_gameplay = pd.read_csv(
        here("data/human-data/experiment-1/processed/gameplay.csv")
    )
    df_messages = pd.read_csv(
        here("data/human-data/experiment-1/processed/messages.csv")
    )
    df_messages["message_value"] = df_messages["trial_id"].map(message_values)

    # Calculate average score per participant
    participant_scores = (
        df_gameplay.groupby(["chain_id", "participant_id", "chain_pos"])["score"]
        .mean()
        .reset_index()
    )
    participant_scores.columns = [
        "chain_id",
        "participant_id",
        "chain_pos",
        "avg_score",
    ]
    participant_scores = participant_scores.sort_values(["chain_id", "chain_pos"])

    # Find adjacent chain positions and calculate score changes
    adjacent_pairs = []
    for chain_id in participant_scores["chain_id"].unique():
        chain_data = participant_scores[
            participant_scores["chain_id"] == chain_id
        ].sort_values("chain_pos")

        for i in range(len(chain_data) - 1):
            current = chain_data.iloc[i]
            next_pos = chain_data.iloc[i + 1]

            if next_pos["chain_pos"] == current["chain_pos"] + 1:
                score_change = next_pos["avg_score"] - current["avg_score"]
                adjacent_pairs.append(
                    {
                        "chain_id": chain_id,
                        "sender_participant_id": current["participant_id"],
                        "sender_chain_pos": current["chain_pos"],
                        "sender_avg_score": current["avg_score"],
                        "receiver_participant_id": next_pos["participant_id"],
                        "receiver_chain_pos": next_pos["chain_pos"],
                        "receiver_avg_score": next_pos["avg_score"],
                        "score_change": score_change,
                    }
                )

    df_adjacent = pd.DataFrame(adjacent_pairs)

    # Merge sender/receiver performance with messages
    df_messages = df_messages.merge(
        df_adjacent[
            [
                "chain_id",
                "sender_participant_id",
                "sender_chain_pos",
                "sender_avg_score",
                "receiver_avg_score",
                "score_change",
            ]
        ],
        left_on=["chain_id", "participant_id", "chain_pos"],
        right_on=["chain_id", "sender_participant_id", "sender_chain_pos"],
        how="left",
    )

    # Clean up redundant columns
    df_messages = df_messages.drop(
        columns=["sender_participant_id", "sender_chain_pos"]
    )

    # Add message length
    df_messages["message_length"] = df_messages["message"].apply(len)

    # Create a truncated message for hover display
    df_messages["message_preview"] = df_messages["message"].apply(
        lambda x: x[:150] + "..." if len(x) > 150 else x
    )

    # Create a wrapped message for hover display (with line breaks)
    df_messages["message_wrapped"] = df_messages["message"].apply(
        lambda x: wrap_text_for_hover(x, width=60)
    )

    return df_messages


def add_regression_line(fig, df, x_col, y_col, color="black", name="Regression"):
    """Add a regression line to a plotly figure."""
    df_valid = df[[x_col, y_col]].dropna()
    if len(df_valid) < 3:
        return fig

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_valid[x_col], df_valid[y_col]
    )

    x_range = np.linspace(df_valid[x_col].min(), df_valid[x_col].max(), 100)
    y_pred = slope * x_range + intercept

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode="lines",
            line=dict(color=color, width=2, dash="solid"),
            name=f"{name} (r={r_value:.2f}, p={p_value:.3f})",
            hoverinfo="skip",
        )
    )

    return fig


def create_scatter_plot(
    df, x_col, y_col, x_label, y_label, title, color_by_domain=True
):
    """Create an interactive scatter plot with hover showing message text."""

    df_plot = df[df[y_col].notna()].copy()
    if x_col != "chain_pos":
        df_plot = df_plot[df_plot[x_col].notna()]

    if color_by_domain:
        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            color="domain",
            hover_data={
                "message_wrapped": True,
                x_col: ":.1f",
                y_col: ":.1f",
                "domain": True,
                "chain_id": True,
                "chain_pos": True,
            },
            opacity=0.8,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
    else:
        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            hover_data={
                "message_wrapped": True,
                x_col: ":.1f",
                y_col: ":.1f",
                "domain": True,
            },
            opacity=0.8,
            title=title,
        )

    # Add overall regression line
    fig = add_regression_line(
        fig,
        df_plot,
        x_col,
        y_col,
        color="rgba(50,50,50,0.8)",
        name="Overall",
    )

    # Add per-domain regression lines if coloring by domain
    if color_by_domain:
        colors = px.colors.qualitative.Set2
        for i, domain in enumerate(df_plot["domain"].unique()):
            domain_df = df_plot[df_plot["domain"] == domain]
            fig = add_regression_line(
                fig,
                domain_df,
                x_col,
                y_col,
                color=colors[i % len(colors)],
                name=f"{domain}",
            )

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis=dict(
            range=[0, max(100, df_plot[x_col].max() * 1.1)]
            if x_col != "message_length"
            else None
        ),
        yaxis=dict(range=[0, 100]),
        hovermode="closest",
        height=600,
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.02),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif",
        ),
    )

    # Custom hover template to show full message (with wrapping via <br> tags)
    fig.update_traces(
        hovertemplate="<b>Message:</b><br>%{customdata[0]}<br><br>"
        + f"<b>{x_label}:</b> %{{x:.1f}}<br>"
        + f"<b>{y_label}:</b> %{{y:.1f}}<br>"
        + "<b>Domain:</b> %{customdata[3]}<br>"
        + "<extra></extra>",
        selector=dict(mode="markers"),
    )

    return fig


def create_chain_pos_plot(df):
    """Create an interactive plot of message value vs chain position."""

    df_plot = df[df["message_value"].notna()].copy()

    # Add jitter to chain_pos for visualization
    df_plot["chain_pos_jittered"] = df_plot["chain_pos"] + np.random.uniform(
        -0.2, 0.2, len(df_plot)
    )

    fig = px.scatter(
        df_plot,
        x="chain_pos_jittered",
        y="message_value",
        color="domain",
        hover_data={
            "message_wrapped": True,
            "chain_pos": True,
            "message_value": ":.1f",
            "domain": True,
            "chain_pos_jittered": False,
        },
        opacity=0.6,
        title="Message Value by Chain Position",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Calculate and add mean with error bars for each chain position
    means = (
        df_plot.groupby("chain_pos")["message_value"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    means["se"] = means["std"] / np.sqrt(means["count"])

    fig.add_trace(
        go.Scatter(
            x=means["chain_pos"],
            y=means["mean"],
            mode="markers+lines",
            marker=dict(size=12, color="black", symbol="diamond"),
            line=dict(color="black", width=2),
            error_y=dict(
                type="data", array=means["se"] * 1.96, visible=True, color="black"
            ),
            name="Mean (95% CI)",
            hovertemplate="<b>Chain Position:</b> %{x}<br><b>Mean Value:</b> %{y:.1f}<br><extra></extra>",
        )
    )

    fig.update_layout(
        xaxis_title="Chain Position",
        yaxis_title="Message Value",
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        yaxis=dict(range=[0, 100]),
        hovermode="closest",
        height=600,
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.02),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif",
        ),
    )

    # Custom hover template for scatter points (with wrapping via <br> tags)
    fig.update_traces(
        hovertemplate="<b>Message:</b><br>%{customdata[0]}<br><br>"
        + "<b>Chain Position:</b> %{customdata[1]}<br>"
        + "<b>Message Value:</b> %{customdata[2]:.1f}<br>"
        + "<b>Domain:</b> %{customdata[3]}<br>"
        + "<extra></extra>",
        selector=dict(mode="markers"),
    )

    return fig


def main():
    st.set_page_config(page_title="Message Value Analysis", layout="wide")

    st.title("Message Value Analysis")
    st.markdown("""
    Message value as a function of different factors. 
    Click one of the variable names below to put it on the x-axis.
    Hover over a data point to see the text of the message.
    """)

    # Load data
    with st.spinner("Loading and processing data..."):
        df_messages = load_and_process_data()

    # Sidebar filters
    st.sidebar.header("Filters")

    domains = ["All"] + sorted(df_messages["domain"].unique().tolist())
    selected_domain = st.sidebar.selectbox("Select Domain", domains)

    if selected_domain != "All":
        df_filtered = df_messages[df_messages["domain"] == selected_domain]
    else:
        df_filtered = df_messages

    # Display summary statistics
    st.sidebar.markdown("---")
    st.sidebar.header("Summary Statistics")

    valid_messages = df_filtered[df_filtered["message_value"].notna()]
    st.sidebar.metric("Total Messages", len(df_filtered))
    st.sidebar.metric("Messages with computed value", len(valid_messages))
    if len(valid_messages) > 0:
        st.sidebar.metric(
            "Mean Message Value", f"{valid_messages['message_value'].mean():.1f}"
        )
        st.sidebar.metric(
            "Stdev Message Value", f"{valid_messages['message_value'].std():.1f}"
        )

    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Sender Performance",
            "Receiver Performance",
            "Message Length",
            "Chain Position",
            "Data Table",
        ]
    )

    with tab1:
        st.header("Message Value vs Sender Performance")
        st.markdown("""
        How does the performance of the message sender relate to the value of their message?
        Higher-performing senders tend to write more valuable messages.
        """)

        fig_sender = create_scatter_plot(
            df_filtered,
            x_col="sender_avg_score",
            y_col="message_value",
            x_label="Sender Average Score",
            y_label="Message Value",
            title="Message Value vs Sender Performance",
            color_by_domain=(selected_domain == "All"),
        )
        st.plotly_chart(fig_sender, use_container_width=True)

        # Correlation info
        valid_data = df_filtered[["sender_avg_score", "message_value"]].dropna()
        if len(valid_data) > 2:
            corr, p_val = stats.pearsonr(
                valid_data["sender_avg_score"], valid_data["message_value"]
            )
            st.info(
                f"**Correlation:** r = {corr:.3f}, p = {p_val:.4f} (n = {len(valid_data)})"
            )

    with tab2:
        st.header("Message Value vs Receiver Performance")
        st.markdown("""
        How does the performance of the message receiver relate to the message value?
        This shows how well the message helped the next person in the chain.
        """)

        fig_receiver = create_scatter_plot(
            df_filtered,
            x_col="receiver_avg_score",
            y_col="message_value",
            x_label="Receiver Average Score",
            y_label="Message Value",
            title="Message Value vs Receiver Performance",
            color_by_domain=(selected_domain == "All"),
        )
        st.plotly_chart(fig_receiver, use_container_width=True)

        # Correlation info
        valid_data = df_filtered[["receiver_avg_score", "message_value"]].dropna()
        if len(valid_data) > 2:
            corr, p_val = stats.pearsonr(
                valid_data["receiver_avg_score"], valid_data["message_value"]
            )
            st.info(
                f"**Correlation:** r = {corr:.3f}, p = {p_val:.4f} (n = {len(valid_data)})"
            )

    with tab3:
        st.header("Message Value vs Message Length")
        st.markdown("""
        Does message length predict message value? 
        Longer messages might contain more useful information, but brevity can also be valuable.
        """)

        fig_length = create_scatter_plot(
            df_filtered,
            x_col="message_length",
            y_col="message_value",
            x_label="Message Length (characters)",
            y_label="Message Value",
            title="Message Value vs Message Length",
            color_by_domain=(selected_domain == "All"),
        )
        st.plotly_chart(fig_length, use_container_width=True)

        # Correlation info
        valid_data = df_filtered[["message_length", "message_value"]].dropna()
        if len(valid_data) > 2:
            corr, p_val = stats.pearsonr(
                valid_data["message_length"], valid_data["message_value"]
            )
            st.info(
                f"**Correlation:** r = {corr:.3f}, p = {p_val:.4f} (n = {len(valid_data)})"
            )

    with tab4:
        st.header("Message Value by Chain Position")
        st.markdown("""
        How does message value change across positions in the transmission chain?
        Later positions may have accumulated more knowledge to share.
        """)

        fig_chain = create_chain_pos_plot(df_filtered)
        st.plotly_chart(fig_chain, use_container_width=True)

        # Show mean values by chain position
        means_by_pos = df_filtered.groupby("chain_pos")["message_value"].agg(
            ["mean", "std", "count"]
        )
        means_by_pos.columns = ["Mean Value", "Std Dev", "Count"]
        st.dataframe(means_by_pos.round(2), use_container_width=True)

    with tab5:
        st.header("Full Data Table")
        st.markdown("Browse and search all messages with their associated metrics.")

        # Select columns to display
        display_cols = [
            "message",
            "message_value",
            "domain",
            "chain_id",
            "chain_pos",
            "sender_avg_score",
            "receiver_avg_score",
            "score_change",
            "message_length",
        ]

        # Search functionality
        search_term = st.text_input("Search messages", "")

        df_display = df_filtered[display_cols].copy()

        if search_term:
            df_display = df_display[
                df_display["message"].str.contains(search_term, case=False, na=False)
            ]

        # Sort options
        sort_col = st.selectbox(
            "Sort by",
            [
                "message_value",
                "sender_avg_score",
                "receiver_avg_score",
                "message_length",
                "chain_pos",
            ],
            index=0,
        )
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

        df_display = df_display.sort_values(
            sort_col, ascending=(sort_order == "Ascending"), na_position="last"
        )

        st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            column_config={
                "message": st.column_config.TextColumn("Message", width="large"),
                "message_value": st.column_config.NumberColumn("Value", format="%.1f"),
                "sender_avg_score": st.column_config.NumberColumn(
                    "Sender Score", format="%.1f"
                ),
                "receiver_avg_score": st.column_config.NumberColumn(
                    "Receiver Score", format="%.1f"
                ),
                "score_change": st.column_config.NumberColumn(
                    "Score Change", format="%.1f"
                ),
                "message_length": st.column_config.NumberColumn("Length"),
            },
        )

        st.caption(f"Showing {len(df_display)} messages")

    # Footer with best/worst messages
    st.markdown("---")
    st.header("Best and Worst Messages")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Highest Value Messages")
        top_messages = df_filtered.nlargest(5, "message_value")[
            ["message", "message_value", "domain"]
        ]
        for _, row in top_messages.iterrows():
            if pd.notna(row["message_value"]):
                st.success(
                    f"**Value: {row['message_value']:.1f}** ({row['domain']})\n\n{row['message']}"
                )

    with col2:
        st.subheader("Lowest Value Messages")
        bottom_messages = df_filtered[df_filtered["message_value"].notna()].nsmallest(
            5, "message_value"
        )[["message", "message_value", "domain"]]
        for _, row in bottom_messages.iterrows():
            st.error(
                f"**Value: {row['message_value']:.1f}** ({row['domain']})\n\n{row['message']}"
            )


if __name__ == "__main__":
    main()
