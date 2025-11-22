---
name: speckit-skilled
descripton: 新しい機能の実装や修正、リファクタリング時に仕様を策定する際に使用する。
---

# SpecKit Skilled

仕様駆動開発ツール「Speckit」をAgent Skillとして調整したもの。
```sh
╭──────────────────────────────────────────────────────────────── Next Steps ─────────────────────────────────────────────────────────────────╮
│                                                                                                                                             │
│  1. You're already in the project directory!                                                                                                │
│  2. Start using slash commands with your AI agent:                                                                                          │
│     2.1 /speckit.constitution - Establish project principles                                                                                │
│     2.2 /speckit.specify - Create baseline specification                                                                                    │
│     2.3 /speckit.plan - Create implementation plan                                                                                          │
│     2.4 /speckit.tasks - Generate actionable tasks                                                                                          │
│     2.5 /speckit.implement - Execute implementation                                                                                         │
│                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────── Enhancement Commands ────────────────────────────────────────────────────────────╮
│                                                                                                                                             │
│  Optional commands that you can use for your specs (improve quality & confidence)                                                           │
│                                                                                                                                             │
│  ○ /speckit.clarify (optional) - Ask structured questions to de-risk ambiguous areas before planning (run before /speckit.plan if used)     │
│  ○ /speckit.analyze (optional) - Cross-artifact consistency & alignment report (after /speckit.tasks, before /speckit.implement)            │
│  ○ /speckit.checklist (optional) - Generate quality checklists to validate requirements completeness, clarity, and consistency (after       │
│  /speckit.plan)                                                                                                                             │
│                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

<<<<<<< HEAD
これらの機能をAgent Skillとして動作させる。

## Agent Skillにするにあたって実行した変更
本来は、それぞれClaude Codeのカスタムコマンドとして動作するものであり、
今回、この移植をするにあたり、以下の変更が行われている。

- `.claude/commands`にあったMarkdownファイル群はSkillのディレクトリ直下に移動。
- `.specify/scripts`にあったShellスクリプトファイル群は、Skillディレクトリの直下に`scripts`ディレクトリごと移動している
- `.specify/templates`にあったテンプレートMarkdownファイル群は、Skillディレクトリの直下に`templates`ディレクトリごと移動している
- `.specify/memory`にあった`constitution.md`ファイルは、Skillディレクトリの直下に`memory`ディレクトリごと移動している

そのため、`.specify`は`${CLAUDE_PLUGIN_ROOT}`に差し替えられている。

## Agent Skillとしての実行されるSpec Kitに要求する追加の指示

- `tasks`を実行すると、その成果物としてMarkdownを作成する。そのMarkdownの内容については、リポジトリにIssueとして必ず登録する。
    - つまり、`tasks`を実行したら、`taskstoissues`も実行する流れを固定とする
    - その際、基本的には`gh`か`GitHub MCP`を活用する。
        - `GitHub MCP`が動かなかった場合、自動的に`gh`を利用すること。
        - `gh`が導入されていない場合は、導入を行う指示を行うこと。
    
=======
これらの機能をAgent Skillとして動作させる

>>>>>>> b648004b21b690f17a48171f81b6b86fe473b310
