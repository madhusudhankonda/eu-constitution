import streamlit as st
import logging
from src.client_util import get_azure_openai_client
from src.client_util import AZURE_OPENAI_ASSISTANT_ID
from dotenv import load_dotenv

load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="Indian Constitution", 
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown(
    "<div style='background-color:#1cb3e0;padding:0px;text-align:center;'>"
    "<h1 style='color:white;'>Indian Constitution Assistant</h1>"
    "</div>",
    unsafe_allow_html=True
)

st.sidebar.image("src\images\indian-constitution-logo.png", width=300)

# Create a two-column layout: 70% for the chat and 30% for model tweaking
col1, col2, col3 = st.columns([1, 2, 1])

st.sidebar.header("Frequently Asked Questions")

with st.sidebar:

    st.header("Menu")
    menu_options = ["Chat", "Model Settings", "FAQs"]
    selection = st.radio("Navigate to:", menu_options)
    
    if selection == "Chat":
        st.write("You're in the Chat section.")
    elif selection == "Model Settings":
        st.write("You're in the Model Settings section.")
    elif selection == "FAQs":
        st.write("You're in the FAQs section.")
    


    st.markdown(
        """
    1. What are the fundamental rights provided by the Indian Constitution?

    2. What is the Preamble to the Indian Constitution, and what does it signify?

    3. How does the Indian Constitution define the territories of India?

    4. What provisions does the Indian Constitution make regarding citizenship?

    5. What are the Directive Principles of State Policy in the Indian Constitution?

    6. What is the amendment process in the Indian Constitution?

    7. How is the President of India elected, and what are the President's powers and duties?

    8. What are the emergency provisions stated in the Indian Constitution?

    9. What is the significance of the Ninth Schedule in the Indian Constitution?

    10. How are the states formed or reorganized under the Indian Constitution?
    """
    )
    st.sidebar.markdown("""---""")

st.sidebar.header("How to use?")

with st.sidebar:
    st.markdown(
        """
        Below is an example application description that you can use to test Indian Constitution Virtual Assistant.
        Input the question in the chat box in the main page, towards the bottom of the page. 
        
        After writing the query, click the send button and await for reply from the virtual assistant.
        """

    )
    
    st.markdown("""---""")

st.sidebar.header("About")

with st.sidebar:
    st.markdown(
        "Welcome to Indian Constitution ChatBot, an AI-powered Virtual Assistant designed to help you understand, quiz, query Indian Constitution."
    )
    st.markdown("Created by [Chocolateminds](https://www.chocolateminds.com/).")
    
    st.markdown("""---""")
# OpenAI client initialization with error handling

try:
    client = get_azure_openai_client()
    logging.debug("Client successfully initialized!")
except Exception as e:
    st.error(f"Error initializing client: {str(e)}")

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4o"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
for message in st.session_state.messages:
    with st.chat_message(message["role"],avatar="src\images\question.png"):
        st.markdown(message["content"])






def process_citations(message, language):
    """Process citations from the message and append footnotes with citations."""
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []

    logging.debug(f"Processing message: {message_content.value}")

    # Iterate over annotations and add citations
    for index, annotation in enumerate(annotations):
        logging.debug(f"Annotation: {annotation}")

        # Replace the citation marker with footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citation details
        if (file_citation := getattr(annotation, 'file_citation', None)):
            if language == "English":
                cited_file = client.files.retrieve('assistant-p3uJKhxDn1iAEAmHk8xXlfEU')
            elif language == "Telugu":
                cited_file = client.files.retrieve('assistant-OgN1ZQeGPqdxtPs90x8pzAsy')
            else:
                cited_file = client.files.retrieve('assistant-JGbnns9fgvw5ndWzZ8AuLXet')
            print("file citation",cited_file)
            quote_text = getattr(file_citation, 'quote', None) or \
                            getattr(file_citation, 'text', None) or\
                            'Citation'
            citations.append(f'[{index + 1}] "{quote_text}" from {cited_file.filename}')
            logging.debug(f"Citation added: {quote_text} from {cited_file.filename}")

    # Add citations at the end of the message
    # message_content.value += '\n\n**Citations:**\n' + '\n'.join(citations)
    return message_content.value


# Model tweaking parameters and language selection in the 30% column

with col2:

    language = st.selectbox("Choose the output language:", ["English", "Hindi", "Telugu","Tamil"])


with col3:
    st.header("Model Settings")
    response_length = st.slider("Response Length:", min_value=50, max_value=500, value=150)
    temperature = st.selectbox("Model Temperature:", [0.1, 0.3, 0.5, 0.7, 0.9], index=2)
    use_advanced_mode = st.checkbox("Use Advanced Mode")
    max_tokens = st.number_input("Max Tokens:", min_value=10, max_value=2048, value=1024)

# col1, col2, col3 = st.columns([1, 2, 1])




if prompt := st.chat_input("Ask me!"):
            params = {
                    "prompt": prompt,
                    "max_tokens": max_tokens if use_advanced_mode else response_length,
                    "temperature": temperature,
                    "stop": None,
                }
            # no use right now
            if language == "Hindi":
                params["language"] = "es"
            elif language == "Telugu":
                params["language"] = "te" 
            elif language == "Tamil":
                params["language"] = "ta"
            else: 
                 params["language"] = "es"
            # Create a new chat thread for the conversation
            chat_thread = client.beta.threads.create()
            st.session_state.thread_id = chat_thread.id

            # Add the user's message to the state and display it on the screen
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="src\images\question.png"):
                st.markdown(prompt)

            # Send the user's message to the thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id, 
                role="user", 
                content=prompt
            )

            # Create a run with specific instructions to provide detailed answers with citations
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=AZURE_OPENAI_ASSISTANT_ID,
                temperature=temperature,
                instructions=f"""
Please answer the questions in {language} using only the knowledge provided in the uploaded ic-hindi PDF file.

- Include direct quotes from the relevant sections of the document in your answer.
- Ensure that the 'quote' field in the file_citation includes the exact text from the document.
- Provide detailed answers in {language}, with citations at the end.
- Please answer the questions using the provided document. Include specific citations in APA format with page numbers and paragraph numbers.
  - Format in-text citations like this: (Author, Year, p. X, para. Y)
  - Example: (Indian Constitution, 2020, p. 15, para. 4)
  
- Provide a full reference at the end, formatted like this:
  - Author(s). (Year). *Title of Document*. Publisher. Page number and paragraph number.
  - Example: Government of India. (2020). *The Constitution of India*. Ministry of Law and Justice, p. 15, para. 4.

Please use the page and paragraph numbers from the document when quoting.
                """,
            )
            print(run)
            # Show a spinner while the assistant is generating the response
            with st.spinner("Generating response..."):
                while run.status != "completed":
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id, run_id=run.id
                    )

                # Retrieve the messages added by the assistant
                messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)

                # Process and display assistant messages
                assistant_messages_for_run = [
                    message for message in messages if message.run_id == run.id and message.role == "assistant"
                ]

                for message in assistant_messages_for_run:
                    logging.debug(f"Processing assistant message: {message}")
                    full_response = process_citations(message=message, language=language)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    with st.chat_message("assistant", avatar="src/images/answer.png"):
                        st.markdown(full_response, unsafe_allow_html=True)



# Chat interface in the 70% column

def chat_content():
    st.session_state['contents'].append(st.session_state.content)

# with st.container():
#     with st.container():
#         st.chat_input(key='content', on_submit=chat_content) 
#         button_b_pos = "0rem"
#         # button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
#         # float_parent(css=button_css)
#     if content:=st.session_state.content:
#         with st.chat_message(name='robot'):
#             for c in st.session_state.contents:
#                 st.write(c)

    st.header("Chat with the Indian Constitution Assistant")
    st.write("This is where the conversation will take place.")

# Chat input for the user
