import time
import os
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler

import chatgpt_assistant as ai_funcs

open_ai_org = os.environ["OPENAI_ORG"]

AGENT_ID = os.environ["AGENT_ID"]

st.title("Agent AWS")


@st.cache_resource
def load_llm():
    assistant = ai_funcs.AwsSolutionsArchitectAssistant(open_ai_org)
    assistant.load_assistant(AGENT_ID)
    return assistant


assistant = load_llm()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help??"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # message_placeholder = st.empty()
        # full_response = ""

        # st_callback = StreamlitCallbackHandler(st.container())

        message_content = assistant.run_ai_message_on_thread(prompt)
        main_content, captions = assistant.parse_content_for_streamlit(message_content)

        st.markdown(main_content)
        for caption in captions:
            st.caption(caption)

    st.session_state.messages.append({"role": "assistant", "content": message_content})
