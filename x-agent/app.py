import os

# Inject Streamlit secrets into env BEFORE other imports that might call load_dotenv
try:
    import streamlit as _st

    for _k in (
        "ANTHROPIC_API_KEY",
        "X_API_KEY",
        "X_API_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_SECRET",
        "GITHUB_TOKEN",
    ):
        if _k not in os.environ:
            _v = _st.secrets.get(_k)
            if _v:
                os.environ[_k] = _v
except Exception:
    pass

from dotenv import load_dotenv

load_dotenv()  # for local dev — does NOT overwrite existing env vars

import streamlit as st
from agent import generate_drafts
from github_context import get_recent_commits
from x_client import post_tweet

st.set_page_config(
    page_title="X Agent · @CristianVGB9",
    page_icon="\U0001f916",
    layout="wide",
)

st.title("\U0001f916 X Agent")
st.caption("Draft and post as **@CristianVGB9** — Applied AI builder")

# ── Mode ──────────────────────────────────────────────────────────────────────
mode = st.radio(
    "Content source",
    ["GitHub commits (last 7 days)", "Describe manually"],
    horizontal=True,
)

context = ""

if mode == "GitHub commits (last 7 days)":
    repos_input = st.text_area(
        "Repos (one per line)",
        value="valentin992/chat-vault-rag\nvalentin992/practice-2",
        height=80,
    )
    if st.button("\U0001f4e5 Fetch commits"):
        repo_list = [r.strip() for r in repos_input.splitlines() if r.strip()]
        with st.spinner("Fetching from GitHub…"):
            fetched = get_recent_commits(repo_list)
        if fetched:
            st.session_state["context"] = fetched
            st.code(fetched, language="text")
        else:
            st.warning(
                "No commits found in the last 7 days. "
                "Add a GITHUB_TOKEN to secrets for private repos."
            )
    context = st.session_state.get("context", "")

else:
    context = st.text_area(
        "What did you build, learn, or ship?",
        placeholder=(
            "Built demo_setup.py — auto-indexes ChromaDB on cold start using "
            "OpenAI text-embedding-3-small. Costs ~$0.002 per rebuild, runs in ~30 s. "
            "Solves the ephemeral filesystem problem on Streamlit Cloud."
        ),
        height=130,
    )
    if context:
        st.session_state["context"] = context

# ── Generate ──────────────────────────────────────────────────────────────────
st.divider()

can_generate = bool(context or st.session_state.get("context"))
if st.button("✨ Generate drafts", disabled=not can_generate, type="primary"):
    ctx = context or st.session_state.get("context", "")
    with st.spinner("Claude is drafting…"):
        try:
            drafts = generate_drafts(ctx)
            st.session_state["drafts"] = drafts
        except Exception as e:
            st.error(f"Generation failed: {e}")

# ── Drafts ────────────────────────────────────────────────────────────────────
if "drafts" in st.session_state:
    st.subheader("Drafts")

    for draft in st.session_state["drafts"]:
        with st.expander(f"#{draft['id']} · {draft['theme']}", expanded=True):
            col_es, col_en = st.columns(2)

            with col_es:
                st.caption("\U0001f1ea\U0001f1f8 Español")
                es_text = st.text_area(
                    f"es_{draft['id']}",
                    value=draft["es"],
                    key=f"es_{draft['id']}",
                    label_visibility="collapsed",
                    height=110,
                )
                char_es = len(es_text)
                st.caption(
                    f"{char_es}/280"
                    + (" ⚠️ over limit" if char_es > 280 else " ✓")
                )
                if st.button("Post \U0001f1ea\U0001f1f8", key=f"post_es_{draft['id']}"):
                    with st.spinner("Posting…"):
                        try:
                            r = post_tweet(es_text)
                            st.success(f"Posted! [View →]({r['url']})")
                        except Exception as e:
                            st.error(str(e))

            with col_en:
                st.caption("\U0001f1fa\U0001f1f8 English")
                en_text = st.text_area(
                    f"en_{draft['id']}",
                    value=draft["en"],
                    key=f"en_{draft['id']}",
                    label_visibility="collapsed",
                    height=110,
                )
                char_en = len(en_text)
                st.caption(
                    f"{char_en}/280"
                    + (" ⚠️ over limit" if char_en > 280 else " ✓")
                )
                if st.button("Post \U0001f1fa\U0001f1f8", key=f"post_en_{draft['id']}"):
                    with st.spinner("Posting…"):
                        try:
                            r = post_tweet(en_text)
                            st.success(f"Posted! [View →]({r['url']})")
                        except Exception as e:
                            st.error(str(e))
