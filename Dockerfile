# uv + Python 3.12 + ruff がプリインストールされた lint/format 検証用イメージ
# 使い方:
#   docker build -t claude-plugins-lint .
#   docker run --rm -v "$(pwd):/workspace" -w /workspace claude-plugins-lint \
#     bash -c "ruff check . && ruff format --check ."
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /workspace

# ruff をグローバルインストール（uvx での毎回ダウンロードを省略）
RUN uv tool install ruff

ENV PATH="/root/.local/bin:$PATH"

ENTRYPOINT ["bash"]
