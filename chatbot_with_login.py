import streamlit as st
import os
import json
from langchain.chains import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# Constants
SESSION_FILE = "user_sessions.json"

# Ensure JSON session file exists
if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "w") as file:
        json.dump({}, file)


class CustomEntityStore:
    """Custom entity store for conversation memory."""
    def __init__(self):
        self.store = defaultdict(str)

    def get(self, key, default=None):
        return self.store.get(key, default)

    def set(self, key, value):
        self.store[key] = value

    def clear(self):
        self.store.clear()


def initialize_session_state():
    """Initialize Streamlit session states."""
    session_defaults = {
        "authenticated": False,
        "current_user": None,
        "generated": [],
        "past": [],
        "input": "",
        "stored_session": [],
        "entity_memory": None
    }
    for key, default in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


initialize_session_state()


# Model loading
model = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0)

if not st.session_state["entity_memory"]:
    st.session_state.entity_memory = ConversationEntityMemory(llm=model, k=12)
    st.session_state.entity_memory.entity_store = CustomEntityStore()

conversation = ConversationChain(
    llm=model,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=st.session_state.entity_memory
)



def save_user_session():
    """Save the current chat session to the JSON file."""
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append(f"User: {st.session_state['past'][i]}")
        save.append(f"Bot: {st.session_state['generated'][i]}")
    st.session_state["stored_session"].append(save)

    with open(SESSION_FILE, "r") as file:
        user_sessions = json.load(file)

    if st.session_state["current_user"] not in user_sessions:
        user_sessions[st.session_state["current_user"]] = {"password": None, "sessions": []}

    user_sessions[st.session_state["current_user"]]["sessions"].append(save)

    with open(SESSION_FILE, "w") as file:
        json.dump(user_sessions, file, indent=4)


def new_chat():
    """Start a new chat session."""
    save_user_session()
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.entity_store.clear()
    st.session_state.entity_memory.buffer.clear()


def login(username, password):
    """Authenticate user and load their sessions."""
    with open(SESSION_FILE, "r") as file:
        user_sessions = json.load(file)

    if username in user_sessions and user_sessions[username].get("password") == password:
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = username
        load_user_sessions(username)
        st.success("Login successful!")
    else:
        st.error("Invalid credentials!")


def register(username, password):
    """Register a new user."""
    with open(SESSION_FILE, "r") as file:
        user_sessions = json.load(file)

    if username in user_sessions:
        st.error("Username already exists!")
    else:
        user_sessions[username] = {"password": password, "sessions": []}
        with open(SESSION_FILE, "w") as file:
            json.dump(user_sessions, file, indent=4)
        st.success("User registered successfully! Please login.")


def load_user_sessions(username):
    """Load a user's saved chat sessions."""
    with open(SESSION_FILE, "r") as file:
        user_sessions = json.load(file)
    if username in user_sessions:
        st.session_state["stored_session"] = user_sessions[username].get("sessions", [])


# UI
def chat_interface():
    """Main chat interface for authenticated users."""
    st.sidebar.button("New Chat", on_click=new_chat, type="primary")
    st.title("🤖 Chat Bot with 🧠")
    st.subheader("Powered by 🦜 LangChain + Gemini + Streamlit")
    
    user_input = st.text_input("Ask Anything....")
    # # st.write("User INPUT:",user_input)
    st.write(f"Session State Input: {st.session_state['input']}")
    # st.write(f"Captured User Input: {user_input}")
    if user_input:
        st.session_state['input'] = user_input
    if user_input:
        try:
            st.write(user_input)
            output = conversation.run(input=user_input)
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)
            st.write(output)
        except Exception as e:
            st.error(f"Error during chat: {e}")
    else:
        st.write("Input Not given")

    with st.expander("Conversation"):
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            st.info(st.session_state["past"][i])
            st.success(st.session_state["generated"][i])

    for i, sublist in enumerate(st.session_state["stored_session"]):
        with st.sidebar.expander(label=f"Conversation-Session:{i}"):
            st.write(sublist)

    if st.sidebar.checkbox("Clear-all"):
        st.session_state["stored_session"] = []
        with open(SESSION_FILE, "r") as file:
            user_sessions = json.load(file)
        if st.session_state["current_user"] in user_sessions:
            user_sessions[st.session_state["current_user"]]["sessions"] = []
        with open(SESSION_FILE, "w") as file:
            json.dump(user_sessions, file, indent=4)
        del st.session_state.stored_session


# App starts
if not st.session_state["authenticated"]:
    st.title("Login to Chatbot")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            login(login_username, login_password)

    with register_tab:
        register_username = st.text_input("Username", key="register_username")
        register_password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            register(register_username, register_password)
else:
    chat_interface()
