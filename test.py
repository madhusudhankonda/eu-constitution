import streamlit as st
# CSS to fix the input box and buttons at the bottom

st.markdown("""
    <style>
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        border-top: 1px solid #ddd;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .text-input {
        flex: 1;
        padding: 10px;
        margin-right: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .btn {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .btn-icon {
        background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABTUlEQVQ4T9WTTUoDQRSGn5mYhmDoo4QXgiIo7+BgsiBoeAI8gCH8Av4Cc4gIIZIggJJ4EUtLA+4QvYBxeYi5cmzPvEGJs7A/N2ds7s7DvdnHg7hKp3uDgWGbAot9awNQH4l04aGM2vQBtRNmGEPLQbGFynKsZgmS5cAql4lPjDCTocTXQCTPxOXQDbAkcCJoDqx5ukEu4BlwnfNN3YoUeIlG1cZK3wqCpQrsQRsoxfQZPIvZ8qP2HIn5RbmCB99CAUyIxSAI1J/A5Mj3A9rO4hncPFTMLBqkD35DCPFEYgj+ndlfPQyAizIg6C1AqsFlMxxQ4VAV8Hs1qvDJW+dQtR1pnbYUyN5kQddcfWSu+g3O0mWoBD+Of4EFZyTSvhq8uZPtYFiv/L4isQtmcivgH6Sfhs4wKxDHYNe95QTmSAAAAAElFTkSuQmCC') no-repeat center center;
        background-size: contain;
        width: 24px;
        height 24px;
        border: none;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

input_container = st.container()
with input_container:
    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
    if "prompt" not in st.session_state:
        st.session_state.prompt = ""
    col1,  col3 = st.columns([9, 1])#col2,
    with col1:
        prompt = st.chat_input("Enter your message", key="text_input")
    # with col2:
    #     send_button = st.button("➤", key="send_button", use_container_width=True)
    with col3:
        mic_button = st.button("🎤", key="voice_button", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# if mic_button:
#     st.session_state.is_speaking = True

# if st.session_state.is_speaking:
#     speech_text = recognize_speech()
#     st.session_state.is_speaking = False
#     if speech_text:
#         st.session_state.prompt = speech_text
#         send_message(speech_text)
#         st.session_state.prompt = ""

# if send_button:
#     send_message(st.session_state.prompt)
#     st.session_state.prompt = ""


if prompt:
    st.write("dddd")