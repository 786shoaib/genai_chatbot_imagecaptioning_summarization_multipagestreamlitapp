import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
from PIL import Image
from io import BytesIO
import google.generativeai as genai

def image_captioning_page():
    st.title("Gemini Vision")
    st.write("""
    **Gemini Vision** is a multimodal model designed to handle both text and image data.
    
    - **Primary Focus**: Processing and generating both text and visual content.
    - **Use Cases**: Used for tasks such as image captioning, visual question answering, and understanding images.
    """)
    MODELS = st.sidebar.selectbox("Select Model", ['gemini-1.5-flash', 'gemini-1.5-flash-8b'])
    api = st.sidebar.text_input('API', type="password")

    # Initialize Model and ConversationChain
    if api:
        genai.configure(api_key=api)
        model = genai.GenerativeModel(MODELS)
        
    image_url = st.text_input("Image URL", "")
    uploaded_file = st.file_uploader("Or Upload an Image...", type=["jpg", "jpeg", "png"])
    # image_url = st.text_input("Image URL", "https://s3.ap-south-1.amazonaws.com/awsimages.imagesbazaar.com/1200x1800-new/758/SM20788.jpg")
    # if st.button("Display Image"):
    img = ''
    if image_url:
        img = fetch_image(image_url)
        if img:
            st.image(img, caption="Fetched Image", use_column_width=True)
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img,caption = 'Uploaded Image',use_column_width=True)
    
    if img != '':
        if st.button("Generate Caption!"):
            response_img = model.generate_content(["Please describe the image",img])
            st.write({response_img.text})
        

    # Optional: Display the original image URL for reference
    st.write("Original URL:", image_url)
    
def fetch_image(url):
    # try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return Image.open(BytesIO(response.content))