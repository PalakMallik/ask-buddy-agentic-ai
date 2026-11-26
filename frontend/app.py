
import requests
import streamlit as st

# ==========================================
# CONFIGURATION
# ==========================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Ask Buddy | AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS - DARK PURPLE THEME
# ==========================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background: linear-gradient(
        135deg,
        #100B1D 0%,
        #171027 50%,
        #100B1D 100%
    );
    color: #F5EEFF;
}

/* Header */
[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1B1230,
        #120D20
    );
    border-right: 1px solid #392653;
}

[data-testid="stSidebar"] * {
    color: #EDE3FF;
}

/* Main headings */
h1, h2, h3 {
    color: #F5EEFF !important;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -1px;
}

/* Captions */
.stCaption, small {
    color: #B9A6D6 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        135deg,
        #A855F7,
        #EC4899
    );
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 9px 16px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        135deg,
        #C084FC,
        #F472B6
    );
    box-shadow: 0 0 18px #A855F755;
    transform: translateY(-2px);
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #211833;
    border: 1px solid #3D2A56;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #211833;
    border: 1px solid #A855F7;
    border-radius: 16px;
}

[data-testid="stChatInput"] textarea {
    color: #F5EEFF !important;
}

/* Input focus */
[data-testid="stChatInput"]:focus-within {
    border-color: #EC4899;
    box-shadow: 0 0 12px #A855F744;
}

/* Dividers */
hr {
    border-color: #392653;
}

/* Conversation buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
}

/* Welcome card */
.welcome-card {
    background: linear-gradient(
        135deg,
        #28183E,
        #38204B
    );
    border: 1px solid #75469A;
    border-radius: 22px;
    padding: 35px;
    text-align: center;
    margin: 35px 0;
    box-shadow: 0 10px 40px #00000040;
}

.gradient-text {
    background: linear-gradient(
        90deg,
        #C084FC,
        #F472B6
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.feature-card {
    background: #211833;
    border: 1px solid #49315F;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    min-height: 115px;
}

.feature-card h4 {
    color: #E9C8FF;
    margin-bottom: 8px;
}

.feature-card p {
    color: #B9A6D6;
    font-size: 13px;
}

/* Remove excess top spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-thumb {
    background: #75469A;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# API FUNCTIONS
# ==========================================

def create_conversation():

    response = requests.post(
        f"{API_URL}/conversations/",
        json={"title": "Ask Buddy Chat"},
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    st.session_state.conversation_id = data["id"]
    st.session_state.messages = []

    st.query_params["cid"] = str(data["id"])


def get_conversations():

    response = requests.get(
        f"{API_URL}/conversations/",
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def load_conversation(conversation_id):

    response = requests.get(
        f"{API_URL}/conversations/{conversation_id}",
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    st.session_state.conversation_id = data["id"]

    st.session_state.messages = [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in data["messages"]
    ]

    st.query_params["cid"] = str(data["id"])


def delete_conversation(conversation_id):

    response = requests.delete(
        f"{API_URL}/conversations/{conversation_id}",
        timeout=15
    )

    response.raise_for_status()

    if st.session_state.conversation_id == conversation_id:

        st.session_state.conversation_id = None
        st.session_state.messages = []

        st.query_params.clear()


# ==========================================
# RESTORE CONVERSATION
# ==========================================

if (
    st.session_state.conversation_id is None
    and "cid" in st.query_params
):

    try:
        load_conversation(int(st.query_params["cid"]))

    except (ValueError, requests.RequestException):
        st.query_params.clear()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        """
        <h2>
            🤖 <span class="gradient-text">Ask Buddy</span>
        </h2>
        <p style="color:#B9A6D6;">
            Your intelligent AI companion
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("＋  New Conversation", use_container_width=True):

        try:
            create_conversation()
            st.rerun()

        except requests.RequestException as e:
            st.error(f"Could not create conversation: {e}")

    st.divider()

    st.markdown("### 💬 Conversation History")

    try:

        conversations = get_conversations()

        if conversations:

            for conversation in conversations:

                conversation_id = conversation["id"]

                title = conversation["title"] or "New Chat"

                if conversation_id == st.session_state.conversation_id:
                    button_label = f"🟣 {title}"
                else:
                    button_label = f"💬 {title}"

                col1, col2 = st.columns([5, 1])

                with col1:

                    if st.button(
                        button_label,
                        key=f"conversation_{conversation_id}",
                        use_container_width=True
                    ):

                        try:
                            load_conversation(conversation_id)
                            st.rerun()

                        except requests.RequestException as e:
                            st.error(f"Could not load conversation: {e}")

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_{conversation_id}",
                        help="Delete conversation"
                    ):

                        try:
                            delete_conversation(conversation_id)
                            st.rerun()

                        except requests.RequestException as e:
                            st.error(f"Could not delete conversation: {e}")

        else:
            st.caption("No conversations yet.")

    except requests.RequestException:
        st.warning("Backend is currently unavailable.")

    st.divider()

    st.markdown(
        """
        <p style="color:#A78BBA; font-size:12px;">
            ✨ Powered by Google Gemini<br>
            🔎 Real-time search by Serper
        </p>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    """
    <h1>
        🤖 <span class="gradient-text">Ask Buddy</span>
    </h1>
    """,
    unsafe_allow_html=True
)

st.caption("Your AI-powered conversational assistant")

st.divider()


# ==========================================
# WELCOME SCREEN
# ==========================================

if st.session_state.conversation_id is None:

    st.markdown(
        """
        <div class="welcome-card">
            <h1 class="gradient-text">
                Hello! Welcome to Ask Buddy 👋
            </h1>

            <p style="color:#D8C7EC; font-size:17px;">
                Your personal AI assistant is ready.
            </p>

            <p style="color:#B9A6D6;">
                Ask questions, explore ideas, learn new things
                and discover information from the web.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h4>🧠 AI Powered</h4>
                <p>Intelligent answers with Gemini</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h4>🔎 Live Search</h4>
                <p>Access current web information</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h4>💬 Chat History</h4>
                <p>Continue your saved conversations</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    if st.button(
        "✨  Start a New Conversation",
        type="primary",
        use_container_width=True
    ):

        try:
            create_conversation()
            st.rerun()

        except requests.RequestException as e:
            st.error(f"Could not create conversation: {e}")


# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# ==========================================
# CHAT INPUT AND STREAMING AI RESPONSE
# ==========================================

if st.session_state.conversation_id is not None:

    query = st.chat_input("Message Ask Buddy... ✨")

    if query:

        # Display user message
        st.session_state.messages.append({
            "role": "user",
            "content": query
        })

        with st.chat_message("user"):
            st.markdown(query)

        # Generate streaming AI response
        with st.chat_message("assistant"):

            placeholder = st.empty()

            ai_response = ""

            try:

                response = requests.post(
                    f"{API_URL}/chat/",
                    json={
                        "conversation_id": st.session_state.conversation_id,
                        "message": query
                    },
                    stream=True,
                    timeout=(15, 180)
                )

                response.raise_for_status()

                with st.spinner("Ask Buddy is thinking... ✨"):

                    for chunk in response.iter_content(
                        chunk_size=1,
                        decode_unicode=True
                    ):

                        if chunk:

                            ai_response += chunk

                            placeholder.markdown(
                                ai_response + "▌"
                            )

                response.close()

                placeholder.markdown(ai_response)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })

                # Refresh conversation sidebar
                if len(st.session_state.messages) == 2:
                    st.rerun()

            except requests.RequestException as e:

                placeholder.error(
                    f"Connection error: {e}"
                )

            except Exception as e:

                placeholder.error(
                    f"Something went wrong: {e}"
                )
