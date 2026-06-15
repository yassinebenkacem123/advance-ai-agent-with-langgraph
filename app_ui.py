
import streamlit as st
from langchain_core.messages import HumanMessage


st.set_page_config(
    page_title="Research Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Root ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0E0E11;
        min-height: 100vh;
        color: #E6E6EB;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #141418;
        border-right: 1px solid #23232A;
    }
    [data-testid="stSidebar"] * {
        color: #E6E6EB !important;
    }

    /* ── Hero ── */
    .hero-header {
        padding: 4rem 0 3rem;
        border-bottom: 1px solid #23232A;
        margin-bottom: 3rem;
    }
    .hero-title {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 400;
        color: #FDFDFD;
        letter-spacing: 0.01em;
        margin: 0 0 0.6rem 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        color: #8A8A93;
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 0.02em;
        margin: 0;
        line-height: 1.6;
    }

    /* ── Chat messages ── */
    .chat-turn {
        margin-bottom: 2.5rem;
        display: flex;
        flex-direction: column;
    }
    .chat-turn-label {
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #63636B;
        margin-bottom: 0.6rem;
    }
    
    /* User Bubble */
    .turn-user {
        align-items: flex-end;
    }
    .chat-bubble-user {
        background-color: #2A2A35;
        color: #FDFDFD;
        padding: 1rem 1.4rem;
        border-radius: 18px 18px 4px 18px;
        font-size: 0.98rem;
        line-height: 1.6;
        max-width: 75%;
        font-weight: 400;
    }
    
    /* Assistant Bubble */
    .turn-assistant {
        align-items: flex-start;
    }
    .chat-bubble-assistant {
        background-color: transparent;
        color: #E6E6EB;
        padding: 0.5rem 0 1rem 0;
        font-size: 1rem;
        line-height: 1.75;
        max-width: 85%;
        font-weight: 300;
    }

    /* ── Status ledger ── */
    .ledger {
        background: #141418;
        border: 1px solid #23232A;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .ledger-title {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #8A8A93;
        margin-bottom: 1rem;
    }
    .ledger-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.35rem 0;
        font-size: 0.88rem;
        color: #B5B5BE;
    }
    .ledger-bar {
        width: 24px;
        height: 2px;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .bar-waiting  { background: #2A2A35; }
    .bar-running  { background: #8C8C96; animation: shimmer 1.5s ease-in-out infinite; }
    .bar-done     { background: #4A4A55; }
    .bar-error    { background: #7A3B3B; }
    .ledger-step  { flex: 1; font-weight: 300; }
    .ledger-state {
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .state-waiting  { color: #4A4A55; }
    .state-running  { color: #E6E6EB; }
    .state-done     { color: #8A8A93; }
    .state-error    { color: #D67A7A; }

    @keyframes shimmer {
        0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(140,140,150,0.2); }
        50%      { opacity: 0.4; box-shadow: none; }
    }

    /* ── Source cards ── */
    .source-card {
        background: #1A1A20;
        border: 1px solid #2A2A35;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        line-height: 1.6;
        transition: border-color 0.2s ease;
    }
    .source-card:hover {
        border-color: #4A4A55;
    }
    .source-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #63636B;
        margin-bottom: 0.4rem;
    }

    /* ── Input ── */
    .stTextInput > div > div > input {
        background: #141418 !important;
        border: 1px solid #2A2A35 !important;
        border-radius: 12px !important;
        color: #FDFDFD !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.85rem 1.2rem !important;
        font-size: 1rem !important;
        font-weight: 300 !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #63636B !important;
        background: #1A1A20 !important;
    }
    .stTextInput > label {
        color: #8A8A93 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #FDFDFD !important;
        color: #0E0E11 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        padding: 0.75rem 1.5rem !important;
    }
    .stButton > button:hover {
        background: #E6E6EB !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar clear button inverted */
    [data-testid="stSidebar"] .stButton > button {
        background: #2A2A35 !important;
        color: #E6E6EB !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #3A3A45 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #141418 !important;
        border-radius: 8px !important;
        color: #B5B5BE !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        border: 1px solid #23232A !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #141418;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #23232A;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8A8A93;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: #2A2A35 !important;
        color: #FDFDFD !important;
    }

    /* ── Divider ── */
    hr { border-color: #23232A !important; margin: 2rem 0 !important; }

    /* ── Sidebar nav items ── */
    .nav-item {
        padding: 0.4rem 0;
        font-size: 0.85rem;
        color: #8A8A93;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-weight: 300;
    }
    .nav-step-num {
        font-size: 0.7rem;
        font-weight: 500;
        color: #4A4A55;
        width: 16px;
        text-align: right;
        flex-shrink: 0;
    }

    /* ── Hide default streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)



@st.cache_resource(show_spinner=False)
def load_agent():
    from main import app, AgentState  # noqa: PLC0415
    return app, AgentState


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False


def render_ledger(statuses: dict[str, str]):
    state_labels = {
        "waiting": ("bar-waiting", "state-waiting", "waiting"),
        "running": ("bar-running", "state-running",  "in progress"),
        "done":    ("bar-done",    "state-done",     "done"),
        "error":   ("bar-error",   "state-error",    "error"),
    }
    rows = ""
    for step, state in statuses.items():
        bar_cls, label_cls, label_text = state_labels.get(state, state_labels["waiting"])
        rows += (
            f'<div class="ledger-row">'
            f'<div class="ledger-bar {bar_cls}"></div>'
            f'<span class="ledger-step">{step}</span>'
            f'<span class="ledger-state {label_cls}">{label_text}</span>'
            f'</div>'
        )
    st.markdown(
        f'<div class="ledger">'
        f'<div class="ledger-title">Research Progress</div>'
        f'{rows}'
        f'</div>',
        unsafe_allow_html=True,
    )


def run_agent(query: str):
    agent_app, AgentState = load_agent()

    initial_state = AgentState(
        messages=[HumanMessage(content=query)],
        google_results=None,
        bing_results=None,
        reddit_results=None,
        selected_reddit_urls=[],
        reddit_post_data=None,
        google_analysis=None,
        bing_analysis=None,
        reddit_analysis=None,
        final_result=None,
    )

    statuses: dict[str, str] = {
        "Google Search":        "running",
        "Bing Search":          "running",
        "Reddit Search":        "running",
        "Selecting Reddit URLs": "waiting",
        "Fetching Reddit Posts": "waiting",
        "Analysing Google":     "waiting",
        "Analysing Bing":       "waiting",
        "Analysing Reddit":     "waiting",
        "Synthesising":         "waiting",
    }

    status_placeholder = st.empty()
    with status_placeholder.container():
        render_ledger(statuses)

    def update_status(**kwargs):
        statuses.update(kwargs)
        with status_placeholder.container():
            render_ledger(statuses)

    final_state = None
    try:
        for chunk in agent_app.stream(initial_state, stream_mode="updates"):
            for node_name, node_state in chunk.items():
                if node_name == "google-search":
                    update_status(**{"Google Search": "done"})
                elif node_name == "bing-search":
                    update_status(**{"Bing Search": "done"})
                elif node_name == "reddit-search":
                    update_status(**{"Reddit Search": "done"})
                elif node_name == "analyze-reddit-post":
                    update_status(**{"Selecting Reddit URLs": "done", "Fetching Reddit Posts": "running"})
                elif node_name == "retreive-reddit-post-data":
                    update_status(**{
                        "Fetching Reddit Posts": "done",
                        "Analysing Google": "running",
                        "Analysing Bing": "running",
                        "Analysing Reddit": "running",
                    })
                elif node_name == "analyze-google-result":
                    update_status(**{"Analysing Google": "done"})
                elif node_name == "analyze-bing-result":
                    update_status(**{"Analysing Bing": "done"})
                elif node_name == "analyze-reddit-result":
                    update_status(**{"Analysing Reddit": "done"})
                elif node_name == "synthesize-node":
                    update_status(**{"Synthesising": "running"})
                    final_state = node_state

        update_status(**{"Synthesising": "done"})

    except Exception as exc:
        update_status(**{k: "error" for k, v in statuses.items() if v == "running"})
        st.error(f"Interruption: {exc}")
        return None

    if final_state is None:
        try:
            final_state = agent_app.invoke(initial_state)
        except Exception as exc:
            st.error(f"Could not complete the process: {exc}")
            return None

    return final_state


with st.sidebar:
    st.markdown(
        "<p style='font-family:DM Serif Display,Georgia,serif;font-size:1.4rem;"
        "color:#FDFDFD;font-weight:400;margin:0.5rem 0 0.2rem'>Research Assistant</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:0.8rem;color:#8A8A93;margin-bottom:1.5rem;font-weight:300;'>"
        "Google · Bing · Reddit, synthesised</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(
        "<p style='font-size:0.7rem;font-weight:600;letter-spacing:0.12em;"
        "text-transform:uppercase;color:#63636B;margin-bottom:0.8rem'>Process</p>",
        unsafe_allow_html=True,
    )
    pipeline_steps = [
        "Search primary networks",
        "Filter relevant threads",
        "Retrieve full context",
        "Analyse independently",
        "Synthesise response",
    ]
    for i, step in enumerate(pipeline_steps, 1):
        st.markdown(
            f"<div class='nav-item'>"
            f"<span class='nav-step-num'>{i}</span>"
            f"<span>{step}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()



st.markdown(
    """
    <div class="hero-header">
        <h1 class="hero-title">What would you like to explore?</h1>
        <p class="hero-subtitle">
            Submit an inquiry. The assistant will independently scan the web, filter the noise, 
            and synthesize a clear, considered response.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

for entry in st.session_state.chat_history:
    role = entry["role"]
    content = entry["content"]

    if role == "user":
        st.markdown(
            f'<div class="chat-turn turn-user">'
            f'<div class="chat-turn-label">You</div>'
            f'<div class="chat-bubble-user">{content}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chat-turn turn-assistant">'
            f'<div class="chat-turn-label">Assistant</div>'
            f'<div class="chat-bubble-assistant">{content}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if entry.get("details"):
            details = entry["details"]
            with st.expander("Review source analysis", expanded=False):
                tab_labels, tab_contents = [], []
                if details.get("google_analysis"):
                    tab_labels.append("Google")
                    tab_contents.append(details["google_analysis"])
                if details.get("bing_analysis"):
                    tab_labels.append("Bing")
                    tab_contents.append(details["bing_analysis"])
                if details.get("reddit_analysis"):
                    tab_labels.append("Reddit")
                    tab_contents.append(details["reddit_analysis"])

                reddit_posts = []
                if details.get("reddit_results") and isinstance(details["reddit_results"], dict):
                    reddit_posts = details["reddit_results"].get("parsed_data", [])

                if tab_labels:
                    tabs = st.tabs(tab_labels)
                    for tab, text in zip(tabs, tab_contents):
                        with tab:
                            st.markdown(
                                f"<div style='color:#B5B5BE;font-size:0.9rem;line-height:1.7;font-weight:300;'>{text}</div>",
                                unsafe_allow_html=True,
                            )

                if reddit_posts:
                    st.markdown(
                        "<p style='font-size:0.75rem;font-weight:600;letter-spacing:0.1em;"
                        "text-transform:uppercase;color:#63636B;margin-top:1.5rem;margin-bottom:0.8rem;'>Thread Context</p>",
                        unsafe_allow_html=True,
                    )
                    for post in reddit_posts[:10]:
                        title = post.get("title", "Untitled Document")
                        url = post.get("url", "#")
                        st.markdown(
                            f"<div class='source-card'>"
                            f"<div class='source-label'>Reddit Origin</div>"
                            f"<a href='{url}' target='_blank' "
                            f"style='color:#E6E6EB;text-decoration:none;font-weight:400'>{title}</a>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

st.divider()
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_query = st.text_input(
        "Inquiry",
        placeholder="e.g. What are the current patterns for microservice resilience?",
        label_visibility="collapsed",
        key="query_input",
        disabled=st.session_state.is_thinking,
    )
with col_btn:
    send_clicked = st.button(
        "Send",
        use_container_width=True,
        disabled=st.session_state.is_thinking,
    )


if send_clicked and user_query.strip():
    query = user_query.strip()
    st.session_state.chat_history.append({"role": "user", "content": query, "details": {}})
    st.session_state.is_thinking = True
    st.rerun()

if st.session_state.is_thinking:
    last_entry = st.session_state.chat_history[-1] if st.session_state.chat_history else None
    if last_entry and last_entry["role"] == "user":
        query = last_entry["content"]

        st.markdown(
            "<p style='color:#8A8A93;font-size:0.9rem;font-weight:300;margin-bottom:1rem'>"
            "Compiling synthesis. This requires a brief moment.</p>",
            unsafe_allow_html=True,
        )

        with st.spinner(""):
            final_state = run_agent(query)

        if final_state:
            answer = final_state.get("final_result") or "The query resolved without generating a definitive synthesis. Please refine the parameters."
            details = {
                "google_analysis": final_state.get("google_analysis"),
                "bing_analysis":   final_state.get("bing_analysis"),
                "reddit_analysis": final_state.get("reddit_analysis"),
                "reddit_results":  final_state.get("reddit_results"),
            }
        else:
            answer = "An interruption occurred during the synthesis process. Please resubmit the query."
            details = {}

        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": answer,
            "details": details,
        })
        st.session_state.is_thinking = False
        st.rerun()