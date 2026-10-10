# 本地大模型智聊机器人

[![CI](https://github.com/eligiblex/local-llm-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/eligiblex/local-llm-chatbot/actions/workflows/ci.yml)

基于 **Streamlit + Ollama** 的本地流式聊天应用，展示模型调用、会话状态、历史窗口和异常恢复。不是模型训练项目，也不包含 RAG 或自主 Agent 功能。

## 已实现

- Streamlit 聊天页面，逐段展示 Ollama 的生成结果。
- Session State 保存当前浏览器会话中的多轮消息，可一键清空。
- 每次请求保留 system 提示和最近 N 条消息，裁剪后移除开头孤立的 assistant 回复。
- 模型名、服务地址可配置；兼容 Ollama SDK 对象和字典格式的流式分片。
- 请求失败时撤回未完成的用户消息，不把部分回答写入后续对话历史。
- 9 项测试覆盖历史裁剪、SDK 流、异常清理，以及真实 Streamlit 页面逻辑的成功/失败/清空交互。

```text
聊天输入 → Session State → 最近 N 条消息 → Ollama /api/chat
                ↑                                  ↓
            完整回答入历史 ← Streamlit 流式展示 ← 文本增量
```

## 快速开始

建议 Python 3.11 / 3.12。先安装并启动 [Ollama](https://ollama.com/)。

```bash
ollama pull deepseek-r1:1.5b
git clone https://github.com/eligiblex/local-llm-chatbot.git
cd local-llm-chatbot
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

macOS / Linux：

```bash
source .venv/bin/activate
cp .env.example .env
```

安装并启动：

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

打开 [本地页面](http://127.0.0.1:8501)。如果 Ollama 没有运行，在另一个终端执行 ollama serve。

## 模型与会话配置

| 配置 | 默认值 | 说明 |
| --- | --- | --- |
| OLLAMA_HOST | http://127.0.0.1:11434 | 模型服务地址 |
| OLLAMA_MODEL | deepseek-r1:1.5b | 必须是已下载的模型 |
| 历史消息数 | 20 | 可在侧栏调为 4～40 条，包含本次用户消息 |

不想下载默认模型时，可在 .env 或页面侧栏改成已有模型，比如 qwen2:1.5b。

本轮真实流式调用验证使用 **qwen2:1.5b**，未下载和验证默认 DeepSeek 模型，避免将模型支持与已验证结果混为一谈。详见 [验证记录](docs/validation.md)。

## 测试

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
```

测试无需运行 Ollama。页面测试使用 Streamlit AppTest，并模拟模型输出；真实本地模型验证单独记录。

## 工程边界

- 这是按消息条数裁剪，不是 token 级预算控制；单条超长输入仍可能超过模型上下文。
- 裁剪作用于每次发给模型的请求，页面显示历史仍保留在会话内存；没有数据库、账号系统或跨设备历史。
- system 提示用于行为约束，无法保证所有事实准确。
- 120 秒网络请求超时；没有自动重试生成，避免失败重试带来重复或不一致回复。
- 默认连接本机；若改为远程 Ollama，问题和历史会发送到远端，不能再宣称数据完全留在本机。
- 请只用于个人本地演示，未实现公网鉴权、访问限流和多租户隔离。

## 文件

app.py 负责页面与会话，chat_service.py 负责历史裁剪和 Ollama 流式调用，tests/ 覆盖业务逻辑和页面交互。

当前公开展示项目，尚未指定开源许可证；所选模型的使用需遵循其对应许可和服务条款。
