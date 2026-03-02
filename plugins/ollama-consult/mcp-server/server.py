#!/usr/bin/env python3
"""Ollama Consult MCP Server

ローカルLLM（Ollama）をClaudeの相談相手として提供するMCPサーバー。
計画・方針の壁打ちや複数アプローチの比較に使用する。

設定は .claude/settings.local.json の env セクションで行う:
  {
    "env": {
      "OLLAMA_HOST": "http://localhost:11434",
      "OLLAMA_MODEL": "llama3.2"
    }
  }
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ollama-consult")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "")
SYSTEM_PROMPT = os.environ.get(
    "OLLAMA_SYSTEM_PROMPT",
    "You are a helpful assistant for planning and decision-making. "
    "Provide concise, concrete suggestions and tradeoff analysis. "
    "Be direct and practical.",
)


def build_not_configured_error() -> str:
    return (
        "エラー: Ollama のモデルが設定されていません。\n\n"
        ".claude/settings.local.json に以下を追加してください:\n\n"
        '{\n'
        '  "env": {\n'
        '    "OLLAMA_HOST": "http://localhost:11434",\n'
        '    "OLLAMA_MODEL": "llama3.2"\n'
        '  }\n'
        "}\n\n"
        "利用可能なモデルは list_models ツールで確認できます。\n"
        "設定後は Claude Code を再起動してください。"
    )


def build_connection_error(host: str) -> str:
    return (
        f"エラー: Ollama に接続できませんでした ({host})。\n"
        "Ollama が起動しているか確認してください:\n"
        "  ollama serve"
    )


@mcp.tool()
def consult_local_llm(question: str, context: str = "") -> str:
    """ローカルLLMに計画・方針・設計について相談する。

    計画の壁打ち、複数アプローチの比較、方針の是非確認など、
    軽量な意思決定支援に使用する。セキュリティや機密情報は含めないこと。

    Args:
        question: 相談する質問や課題。具体的であるほど良い回答が得られる。
        context: 背景情報や制約条件（任意）。プロジェクトの状況や前提条件など。

    Returns:
        ローカルLLMからの回答。
    """
    if not OLLAMA_MODEL:
        return build_not_configured_error()

    user_message = question
    if context:
        user_message = f"背景情報:\n{context}\n\n質問:\n{question}"

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
    except httpx.ConnectError:
        return build_connection_error(OLLAMA_HOST)
    except httpx.HTTPStatusError as e:
        return f"エラー: Ollama API エラー ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"エラー: {e}"


@mcp.tool()
def list_models() -> str:
    """Ollama で利用可能なモデルの一覧を返す。

    接続確認やモデル選択時に使用する。

    Returns:
        モデル名とサイズの一覧。
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            data = response.json()

        models = data.get("models", [])
        if not models:
            return (
                "利用可能なモデルがありません。\n"
                "ollama pull <model-name> でモデルをインストールしてください。\n"
                "例: ollama pull llama3.2"
            )

        lines = [f"Ollama ホスト: {OLLAMA_HOST}", ""]
        lines.append("利用可能なモデル:")
        for model in models:
            size_gb = model.get("size", 0) / (1024**3)
            name = model.get("name", "unknown")
            param_size = model.get("details", {}).get("parameter_size", "")
            family = model.get("details", {}).get("family", "")
            info = f"  - {name} ({size_gb:.1f}GB)"
            if param_size:
                info += f" [{param_size}]"
            if family:
                info += f" ({family})"
            lines.append(info)

        if OLLAMA_MODEL:
            lines.append(f"\n現在の設定モデル: {OLLAMA_MODEL}")
        else:
            lines.append(
                "\n現在の設定モデル: 未設定\n"
                ".claude/settings.local.json の env.OLLAMA_MODEL で設定してください。"
            )

        return "\n".join(lines)

    except httpx.ConnectError:
        return build_connection_error(OLLAMA_HOST)
    except Exception as e:
        return f"エラー: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
