import os
from typing import Any
from uuid import UUID 
import streamlit as st

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage

from dotenv import load_dotenv

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="") -> None:
        self.container = container
        self.text = initial_text
        
    def on_llm_new_token(self, token: str, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> None:
        self.text += token
        self.container.markdown(self.text)

def init_page():
    st.set_page_config(page_title="Langchain PoC", layout="wide") 
    st.title("💬 Chatbot")
    
def init_key():
    if 'chatbot_api_key' not in st.session_state:
        st.session_state["chatbot_api_key"] = os.environ["OPENAI_API_KEY"]
    
def init_sidebar():
    with st.sidebar:
        st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    
def init_chat():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [ChatMessage(role="assistant", content="How can I help you?")]

    for msg in st.session_state.messages:
        st.chat_message(msg.role).write(msg.content)

    if prompt := st.chat_input():
        if "chatbot_api_key" not in st.session_state:  
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        # openai.api_key = st.session_state["chatbot_api_key"]
        st.session_state.messages.append(ChatMessage(role="user", content=prompt)) 
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            container = st.empty()
            stream_handler = StreamHandler(container)
            with st.sidebar:
                llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=st.session_state["chatbot_api_key"], streaming=True, callbacks=[stream_handler])
                response = llm(st.session_state.messages) 
                
            st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
            container.markdown(response.content)
    
def main():
    load_dotenv()
    init_page()
    init_key()
    init_sidebar()
    init_chat()
     
if __name__ == '__main__':
    main()