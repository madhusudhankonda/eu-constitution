import streamlit as st
import os
import logging
from client_util import get_azure_openai_client
from client_util import AZURE_OPENAI_ASSISTANT_ID
from dotenv import load_dotenv
from common_settings import set_page_container_style, hide_streamlit_header_footer
import base64
load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="EU Constitution", 
    page_icon=":flag-eu:",
    layout="wide",
    initial_sidebar_state="expanded")

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Encode the background image
bg_img = get_img_as_base64("src/images/eu-bg.png")  # Replace with your local background image file

# Load the CSS file and insert the background image
with open("styles.css") as f:
    css = f.read().replace("{bg_img}", bg_img)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

set_page_container_style(
        max_width = 1100, max_width_100_percent = True,
        padding_top = 0, padding_right = 10, padding_left = 5, padding_bottom = 5
)

st.markdown(hide_streamlit_header_footer(), unsafe_allow_html=True)

col1, col2 = st.columns([90, 10])

with col2:
    reset_button = st.button("Reset chat", key="reset_button", help="Click to reset the chat")

# Reset the chat if the reset button is clicked
if reset_button:
    st.session_state.messages = []

with col1:
    st.markdown(
        f'''
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{get_img_as_base64('src/images/eu-logo.png')}" style="width: 70px; height: 70px; margin-right: 10px;">
            <p style="color:#0A2081;font-size:30px;font-weight:bold;margin-top:0px;margin-bottom:0px;">European Union Constitution AI Chatbot</p>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(f'<p style="color:grey;font-size:18px;text-align:center;text-centre:center">{"An AI assistant for querying the EU Constitution and Treaties"}', unsafe_allow_html=True)

def about():
    st.sidebar.markdown('---')
    st.sidebar.info('''
    ### EU Constitution 
    #### by https://chocolateminds.com

    Updated: 09 October 2024''')

col1, col2 = st.columns([4, 1])

LANGUAGE = "English"

# ---- SIDEBAR START -------

st.sidebar.image("src/images/eu.jpg", width=250)
st.sidebar.markdown("<h3 style='color: #0A2081;'>Choose the output language:</h3>", unsafe_allow_html=True)
with st.sidebar:
    LANGUAGE = st.selectbox("options", ["English", "French", "German", "Italian", "Spanish", "Dutch", "Polish", "Portuguese"],label_visibility = "collapsed")

constitution_faq = [
    "What are the fundamental rights guaranteed by the EU Charter of Fundamental Rights?",
    "What is the purpose and structure of the European Union?",
    "How does the EU Constitution define EU citizenship?",
    "What are the main EU institutions and their roles?",
    "What are the key principles of EU law?",
    "How are EU treaties amended?",
    "How is the President of the European Commission selected?",
    "What are the emergency provisions in EU treaties?",
    "How does the EU make decisions?",
    "How can new member states join the European Union?"
]

treaty_faq = [
    "What were the key changes introduced by the Treaty of Lisbon?",
    "How did the Maastricht Treaty establish the European Union?",
    "What was the significance of the Treaty of Rome?",
    "How did the Treaty on the Functioning of the EU (TFEU) change EU operations?",
    "What were the main provisions of the Single European Act?",
    "How did the Treaty of Amsterdam enhance EU cooperation?",
    "What changes were brought by the Treaty of Nice?",
    "What is the significance of the Schengen Agreement?",
    "How does the Treaty on European Union (TEU) define EU values?",
    "What are the key provisions of the Charter of Fundamental Rights?"
]

def display_faq(faq_list, prefix):
    for question in faq_list:
        if st.button(question, key=f"{prefix}_{question}"):
            st.session_state.faq_question = question

st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on EU Constitution</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.expander("FAQ on EU Constitution", expanded=False):
        display_faq(constitution_faq, "const")

st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on EU Treaties</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.expander("FAQ on EU Treaties", expanded=False):
        display_faq(treaty_faq, "treaty")

st.sidebar.markdown("<h3 style='color: #0A2081;'>How to use?</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.container(border=1):
        st.markdown(
            """
            Input the question in the chat box in the main page, towards the bottom of the page. 
            
            After writing the query, click the send button and await for reply from the virtual assistant.
            """
        )

st.sidebar.markdown("<h3 style='color: #0A2081;'>About</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.container(border=1):
        st.markdown(
            "Welcome to EU Constitution ChatBot, an AI-powered Virtual Assistant designed to help you understand and query EU Constitution and Treaties."
        )
        st.markdown("Created by [Chocolateminds](https://www.chocolateminds.com/).")

# ---- SIDEBAR END -------

try:
    client = get_azure_openai_client()
    logging.debug("Client successfully initialized!")
except Exception as e:
    st.error(f"Error initializing client: {str(e)}")

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "faq_question" not in st.session_state:
    st.session_state.faq_question = None

def process_citations(message):
    """Process citations from the message and append footnotes with citations."""
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []

    logging.debug(f"Processing message: {message_content.value}")

    for index, annotation in enumerate(annotations):
        logging.debug(f"Annotation: {annotation}")
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            quote_text = getattr(file_citation, 'quote', None) or \
                            getattr(file_citation, 'text', None) or\
                            'Citation'
            citations.append(f'[{index + 1}] "{quote_text}" from {cited_file.filename}')
            logging.debug(f"Citation added: {quote_text} from {cited_file.filename}")

    return message_content.value

def generate_response(prompt):
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, 
        role="user", 
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=AZURE_OPENAI_ASSISTANT_ID,
        instructions=f"""
        Please answer the questions in {LANGUAGE} using only the knowledge provided in the uploaded EU Constitution and Treaties PDF files.

        - There is a file for each language in the vector store - you must consult the respective file. 
        For example, if the LANGUAGE is French, you must retrieve answers from eu-french.pdf file
        - Include direct quotes from the relevant sections of the document in your answer.
        - Ensure that the 'quote' field in the file_citation includes the exact text from the document.
        - Provide detailed answers in {LANGUAGE}, with citations at the end.
        - The citations should reference specific articles or sections, including the quoted text.
        """,
    )

    with st.spinner("Thinking.."):
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )

        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)

        assistant_messages_for_run = [
            message for message in messages if message.run_id == run.id and message.role == "assistant"
        ]

        for message in assistant_messages_for_run:
            logging.debug(f"Processing assistant message: {message}")
            full_response = process_citations(message=message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant", avatar="src/images/eu-logo.png"):
                st.markdown(full_response, unsafe_allow_html=True)

with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="src/images/eu-logo.png" if message["role"] == "assistant" else "src/images/chat_avatar.png"):
            st.markdown(message["content"])

if st.session_state.faq_question:
    st.session_state.messages.append({"role": "user", "content": st.session_state.faq_question})
    with st.chat_message("user", avatar="src/images/chat_avatar.png"):
        st.markdown(f"<p style='color: #0A2081;'>{st.session_state.faq_question}</p>", unsafe_allow_html=True)
    generate_response(st.session_state.faq_question)
    st.session_state.faq_question = None

if prompt := st.chat_input("What do you want to ask me?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="src/images/chat_avatar.png"):
        st.markdown(prompt)
    generate_response(prompt)

if __name__ == '__main__':
    about()