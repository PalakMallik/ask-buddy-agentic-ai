from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st


st.set_page_config(
    page_title="Ask Buddy",
    page_icon="🤖",
    layout="wide"
)


llm = ChatGoogleGenerativeAI(model = "gemini-3.5-flash-lite")


st.title("🤖💬 Ask Buddy - AI QnA Bot")
st.markdown("QnA Bot with LangChain and Google Gemini !")


# Initialize only once
if "messages" not in st.session_state:
    st.session_state.messages = []



# Display previous messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)


# Get new message
query = st.chat_input("Ask anything")


if query:
    # User message
    st.session_state.messages.append({"role" : "user", "content" : query})
    st.chat_message("user").markdown(query)

    # AI response
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.content[0]["text"])
    st.session_state.messages.append({"role" : "ai", "content" : res.content[0]["text"]})


