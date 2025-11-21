import os
from typing import Dict, List, Optional

import pandas as pd
import redis
import streamlit as st
from dotenv import load_dotenv
from utils import translate

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


@st.cache_resource
def get_redis_client():
    """Initialize Redis connection"""

    try:
        client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
        )

        client.ping()
        print("✅ Connected to Redis successfully!")
        return client
    except redis.ConnectionError as e:
        st.error(f"❌ Failed to connect to Redis: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def get_all_scores(r: redis.Redis) -> List[Dict]:
    """Get all scores sorted by score (descending)"""
    scores = r.zrevrange("highscores", 0, -1, withscores=True)
    return [
        {"rank": i + 1, "name": name, "score": int(score)}
        for i, (name, score) in enumerate(scores)
    ]


def search_player(r: redis.Redis, search_term: str) -> Optional[Dict]:
    """Search for a player by name"""
    if not search_term:
        return None

    # Get player's score
    score = r.zscore("highscores", search_term)
    if score is None:
        return None

    # Get player's rank
    rank = r.zrevrank("highscores", search_term)

    return {
        "rank": rank + 1 if rank is not None else None,
        "name": search_term,
        "score": int(score),
    }


def add_score(r: redis.Redis, name: str, score: int):
    """Add or update a player's score (only if higher)"""
    existing_score = r.zscore("highscores", name)
    if existing_score is None or score > existing_score:
        r.zadd("highscores", {name: score})


def main():
    if st.session_state.points > 0:
        if st.button(translate(
            f"Submit {round(st.session_state.points)} points",
            f"{round(st.session_state.points)} Punkte einreichen"),
            key="submit_button",
        ):
            add_score(
                get_redis_client(),
                st.session_state.username,
                round(st.session_state.points),
            )
            st.success(
                f"✅ {round(st.session_state.points)} points submitted!"
                if st.session_state.language == "English"
                else f"✅ {round(st.session_state.points)} Punkte eingereicht!"
            )

    st.divider()

    st.title("🏆 Highscores Leaderboard")

    # Initialize Redis
    r = get_redis_client()
    if r is None:
        st.stop()

    # Get all scores
    all_scores = get_all_scores(r)

    if not all_scores:
        st.info("No scores yet. Be the first to play!")
        st.stop()

    # Pagination
    items_per_page = 10
    total_items = len(all_scores)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Page selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
        )

    # Calculate slice indices
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_scores = all_scores[start_idx:end_idx]

    # Create a table
    table_data = []
    for entry in page_scores:
        rank_display = (
            f"🥇 #{entry['rank']}"
            if entry["rank"] == 1
            else f"🥈 #{entry['rank']}"
            if entry["rank"] == 2
            else f"🥉 #{entry['rank']}"
            if entry["rank"] == 3
            else f"#{entry['rank']}"
        )
        table_data.append(
            {
                "Rank": rank_display,
                "Player": entry["name"],
                "Score": f"{entry['score']:,}",
            }
        )

    df = pd.DataFrame(table_data)
    st.dataframe(df, width='stretch', hide_index=True)

    st.divider()

    # Search functionality
    st.subheader("🔍 Search Your Rank")
    search_term = st.text_input(
        "Enter your name to find your rank",
        placeholder="Type your name...",
        key="search",
    )

    if search_term:
        result = search_player(r, search_term)
        if result:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rank", f"#{result['rank']}")
            with col2:
                st.metric("Name", result["name"])
            with col3:
                st.metric("Score", f"{result['score']:,}")
        else:
            st.warning(f"Player '{search_term}' not found in highscores")


if __name__ == "__main__":
    main()
