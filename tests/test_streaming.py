from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from chat_service import OllamaChatService, trim_history


def test_orphan_assistant_removed_and_input_not_mutated():
    messages = [{'role': 'system', 'content': '规则'}, {'role': 'user', 'content': '一'}, {'role': 'assistant', 'content': '二'}, {'role': 'user', 'content': '三'}]
    result = trim_history(messages, 2)
    assert [m['role'] for m in result] == ['system', 'user']
    result[0]['content'] = 'changed'
    assert messages[0]['content'] == '规则'
    assert len(messages) == 4


@pytest.mark.parametrize('limit', [0, -1])
def test_bad_limit(limit):
    with pytest.raises(ValueError):
        trim_history([], limit)


def test_empty_history():
    assert trim_history([]) == []


def test_dictionary_and_sdk_chunks():
    client = Mock()
    client.chat.return_value = iter([{'message': {'content': '你'}}, SimpleNamespace(message=SimpleNamespace(content='好')), {'done': True}])
    service = OllamaChatService(client=client)
    messages = [{'role': 'user', 'content': 'hello'}]
    assert ''.join(service.stream_reply(messages)) == '你好'
    client.chat.assert_called_once_with(model=service.model, messages=messages, stream=True)


def test_stream_closes_on_failure():
    closed = []
    def chunks():
        try:
            yield {'message': {'content': '半段'}}
            raise RuntimeError('connection lost')
        finally:
            closed.append(True)
    client = Mock()
    client.chat.return_value = chunks()
    service = OllamaChatService(client=client)
    iterator = service.stream_reply([])
    assert next(iterator) == '半段'
    with pytest.raises(RuntimeError):
        next(iterator)
    assert closed == [True]
