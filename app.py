from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from chat_service import DEFAULT_SYSTEM_PROMPT, OllamaChatService, trim_history


load_dotenv(Path(__file__).with_name('.env'))
st.set_page_config(page_title="Local LLM Chatbot", page_icon="🤖")
st.title("本地大模型智聊机器人")
st.caption("默认使用本机 Ollama；若改用远程服务，对话将发送到你配置的地址。")

with st.sidebar:
    st.subheader("会话设置")
    model = st.text_input("模型", value=os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b"))
    host = st.text_input("Ollama 地址", value=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))
    max_messages = st.slider("保留的历史消息数", 4, 40, 20, 2)
    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "assistant", "content": "你好，我是本地智聊机器人。有什么可以帮你？"},
        ]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "assistant", "content": "你好，我是本地智聊机器人。有什么可以帮你？"},
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("请输入问题")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    request_messages = trim_history(st.session_state.messages, max_messages=max_messages)
    try:
        service = OllamaChatService(host=host, model=model)
        with st.chat_message("assistant"):
            answer = st.write_stream(service.stream_reply(request_messages))
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError('模型未返回有效答案')
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception:
        # Failed/incomplete generations must not pollute the next model request.
        st.session_state.messages.pop()
        st.error("本次回答未完成。请确认 Ollama 已启动、模型已下载，再重新发送问题。")
