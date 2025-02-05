import streamlit as st 
import os
from langchain.chains import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_google_genai import ChatGoogleGenerativeAI
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY


if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
    
def get_text():
    input_text = st.text_input("You: ",st.session_state["input"],key = "input",
                               placeholder="Your AI assistant here! Ask me anything....",
                               label_visibility="hidden")
    return input_text


model = ChatGoogleGenerativeAI(model='gemini-1.0-pro',temperature=0)

if "entity_memory" not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(llm=model,k=12)
    st.session_state.entity_memory.entity_store = defaultdict(str)
    
conversation = ConversationChain(llm = model,
                                 prompt = ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                                 memory = st.session_state.entity_memory)

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.entity_store = {}
    st.session_state.entity_memory.buffer.clear()

st.sidebar.button("New Chat", on_click = new_chat, type='primary')

st.title("🤖 Chat Bot with 🧠")
st.subheader(" Powered by 🦜 LangChain + OpenAI + Streamlit")


user_input = get_text()

if user_input:
    output = conversation.run(input = user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)
    st.write(output)
    
with st.expander("Conversation"):
    for i in range(len(st.session_state['generated'])-1,-1,-1):
        st.info(st.session_state["past"][i])
        st.success(st.session_state["generated"][i])
        
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label= f"Conversation-Session:{i}"):
        st.write(sublist)
        
if st.session_state.stored_session:   
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session

