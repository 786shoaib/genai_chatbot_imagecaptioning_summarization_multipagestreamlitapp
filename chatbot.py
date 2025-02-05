# chatbot.py
import streamlit as st
import os
from langchain.chains import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from collections import defaultdict

# Load the environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# Custom Entity Store
class CustomEntityStore:
    def __init__(self):
        self.store = defaultdict(str)

    def get(self, key, default=None):
        return self.store.get(key, default)

    def set(self, key, value):
        self.store[key] = value

    def clear(self):
        self.store.clear()

# Function to initialize session state if it doesn't exist
def initialize_session_state():
    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    if "input" not in st.session_state:
        st.session_state["input"] = ""  # Initialize the input key to an empty string
    if "stored_session" not in st.session_state:
        st.session_state["stored_session"] = []

# Function to get user input from the text input box
def get_text():
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                               placeholder="Your AI assistant here! Ask me anything....",
                               label_visibility="hidden")
    return input_text

# Main chatbot page function
def chatbot_page():
    initialize_session_state()

    # Sidebar for model selection and API input
    MODELS = st.sidebar.selectbox("Select Model", ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro'])
    api = st.sidebar.text_input('API', type="password")

    # Initialize Model and ConversationChain
    if api:
        model = ChatGoogleGenerativeAI(model=MODELS, temperature=0)

        if "entity_memory" not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=model, k=12)
            st.session_state.entity_memory.entity_store = CustomEntityStore()  # Use Custom Store

        conversation = ConversationChain(llm=model,
                                        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                                        memory=st.session_state.entity_memory)
    else:
        st.sidebar.error("Enter API key")

    # Function to handle new chat and reset state
    def new_chat():
        save = []
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            save.append("User:" + st.session_state["past"][i])
            save.append("Bot:" + st.session_state["generated"][i])
        st.session_state["stored_session"].append(save)
        st.session_state["generated"] = []
        st.session_state["past"] = []
        st.session_state["input"] = ""  # Reset input after new chat
        st.session_state.entity_memory.entity_store.clear()  # Clear custom store
        st.session_state.entity_memory.buffer.clear()

    # Add button for new chat in sidebar
    st.sidebar.button("New Chat", on_click=new_chat, type='primary')

    # UI components
    st.title("LLM Chat Bot with Memory")
    st.subheader("Powered by -> LangChain + Gemini + Streamlit")

    # Get user input and process conversation
    user_input = get_text()
    if user_input:
        output = conversation.run(input=user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
        st.write(output)

    # Display previous conversations
    with st.expander("Conversation"):
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            st.info(st.session_state["past"][i])
            st.success(st.session_state["generated"][i])

    # Display stored sessions
    for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label=f"Conversation-Session:{i}"):
            st.write(sublist)

    # Option to clear all stored sessions
    if st.session_state.stored_session:
        if st.sidebar.checkbox("Clear-all"):
            del st.session_state.stored_session
