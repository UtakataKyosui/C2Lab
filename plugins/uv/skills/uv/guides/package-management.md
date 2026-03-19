# Package Management with uv

## プロジェクトの初期化

```bash
uv init                            # 新規プロジェクトを初期化（pyproject.toml を作成）
uv init my-project                 # ディレクトリを指定して初期化
uv init --package                  # パブリッシュ可能なパッケージとして初期化
uv init --app                      # アプリケーションとして初期化
uv init --lib                      # ライブラリとして初期化
```

## 依存関係の管理

```bash
# パッケージの追加
uv add <package>                   # 依存関係を追加
uv add <package>==<version>        # バージョン指定
uv add "<package>>=<version>"      # バージョン範囲指定（シェルのリダイレクトを避けるためクォートが必要）
uv add --dev <package>             # 開発用依存関係に追加

# パッケージの削除
uv remove <package>
uv remove --dev <package>

# 依存関係の更新
uv lock --upgrade                  # 全パッケージを最新版に更新
uv lock --upgrade-package <pkg>    # 特定パッケージのみ更新
```

## 環境の同期

```bash
uv sync                            # uv.lock と仮想環境を同期
uv sync --frozen                   # lockfile を変更せずに同期（CI 推奨）
uv sync --no-dev                   # 開発用依存関係を除く
uv sync --group <group>            # 特定グループの依存関係を追加
```

## lockfile の管理

```bash
uv lock                            # uv.lock を生成・更新
uv lock --check                    # lockfile が最新か確認（CI 向け）
uv lock --upgrade                  # 全パッケージを最新版に更新
```

## スクリプト実行

```bash
uv run python <script.py>          # 仮想環境内で Python を実行
uv run <tool>                      # pyproject.toml の scripts エントリを実行
uv run -- python -c "import sys; print(sys.version)"
```

## 仮想環境の操作

```bash
uv venv                            # .venv を作成
uv venv --python 3.12              # Python バージョンを指定
uv venv --python python3.11        # パスを指定

# 手動でアクティベート（通常は uv run で不要）
source .venv/bin/activate
```

## pip 互換インターフェース

```bash
uv pip install <package>           # pip install 相当
uv pip install -r requirements.txt
uv pip install -e .                # 編集可能インストール
uv pip uninstall <package>
uv pip list                        # インストール済みパッケージ一覧
uv pip freeze                      # pip freeze 相当
uv pip compile requirements.in     # pip-tools 相当
```

## ワークスペース管理

uv はモノレポ向けのワークスペース機能をサポートします。

```toml
# ルート pyproject.toml
[tool.uv.workspace]
members = ["packages/*", "apps/*"]
```

```bash
# ワークスペース全体の操作
uv sync                            # 全メンバーを同期
uv run --package <member> <cmd>    # 特定メンバーでコマンド実行

# メンバー間の依存
uv add --editable ./packages/utils # ローカルパッケージをリンク
```

## 依存グループ（extras / optional-dependencies）

```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.1"]
docs = ["sphinx>=7.0", "sphinx-rtd-theme"]
```

```bash
# extras を含めてインストール
uv sync --extra dev
uv sync --extra dev --extra docs
uv sync --all-extras              # 全 extras を含めてインストール

uv pip install -e ".[dev,docs]"   # pip 互換形式
```

## プレリリース対応

```bash
# プレリリースを許可して追加
uv add --prerelease allow <package>

# 全パッケージのプレリリースを許可
uv sync --prerelease allow
```

```toml
# pyproject.toml でプレリリース設定
[tool.uv]
prerelease = "allow"

# 特定パッケージのみ許可
[[tool.uv.dependency-metadata]]
name = "some-package"
prerelease = "allow"
```

## pyproject.toml の例

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```
