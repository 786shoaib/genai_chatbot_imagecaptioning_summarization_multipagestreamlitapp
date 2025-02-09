import streamlit as st
from chatbot import chatbot_page  # Import the chatbot page function
from image_captioning import image_captioning_page

# Set the page configuration (optional)
st.set_page_config(page_title="GenAI Project", page_icon=":robot:", layout="wide")

# Function to display the welcome page
def display_welcome_page():
    # Add a custom title
    st.title("🤖 Welcome to GenAI Project")
    
    # Add a bot-like image
    st.image(
        "https://cdn-icons-png.flaticon.com/512/4712/4712027.png",  # High-quality bot image
        caption="Your Friendly AI Assistant",
        width=300
    )

    # Add a header and description
    st.header("Empowering the Future with AI!")
    st.markdown("""
    GenAI Project is a powerful suite of tools powered by **LangChain**, **Gemini**, and **Streamlit**. 
    Our project offers a rich experience including chatbot capabilities, image captioning, and translation, all in one place.

    Explore the exciting world of AI with our simple interface and robust backend. 
    The chatbot will help you explore the capabilities of language models, while other features are coming soon!
    """)

    # Optional: Add a decorative section image
    st.image(
        "https://cdn.pixabay.com/photo/2021/05/15/18/54/artificial-intelligence-6253287_960_720.jpg",
        caption="Unlock the Power of AI",
        use_container_width=True  # Updated parameter
    )

    # Add some custom styling
    st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
        }
        .stTextInput>div>div>input {
            background-color: #f7f7f7;
            border-radius: 10px;
            padding: 12px;
            font-size: 16px;
        }
        .stButton>button {
            background-color: #0073e6;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
    """, unsafe_allow_html=True)

    # Button to start the chatbot or explore more
    st.markdown("### Ready to explore AI? Start chatting now!")
    # if st.button("Go to Chatbot"):
    #     st.experimental_set_query_params(page="Chatbot")




# Sidebar for navigation
PAGES = {
    "Welcome": display_welcome_page,  # Display welcome page
    "Chatbot": chatbot_page,  # Chatbot page function
    "Image Captioning": image_captioning_page,  # image captioning function
    "Summarizer (TODO)": lambda: st.write("Summarizer (TODO)")  # Placeholder for translation
}

# Page navigation
selected_page = st.sidebar.selectbox("Select a Page", options=list(PAGES.keys()))

# Display the selected page
PAGES[selected_page]()  # Call the function for the selected page
