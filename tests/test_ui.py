from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


def test_success_and_clear():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    with patch('chat_service.OllamaChatService.stream_reply', return_value=iter(['测试', '回答'])):
        at.chat_input[0].set_value('你好').run()
    assert not at.exception
    assert at.session_state['messages'][-1] == {'role': 'assistant', 'content': '测试回答'}
    at.button[0].click().run()
    assert len(at.session_state['messages']) == 2


def test_failure_rolls_back_user_message():
    at = AppTest.from_file(APP).run()
    before = list(at.session_state['messages'])
    with patch('chat_service.OllamaChatService.stream_reply', side_effect=RuntimeError('offline')):
        at.chat_input[0].set_value('失败的问题').run()
    assert not at.exception
    assert len(at.error) == 1
    assert at.session_state['messages'] == before
