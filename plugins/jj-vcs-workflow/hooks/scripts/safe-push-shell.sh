# jj safe-push: jj git push の直接実行を禁止し、安全な push ワークフローを強制する
# bash / zsh 両対応
#
# - jj git push (--dry-run なし) → ブロック
# - jj git push --dry-run → 許可
# - jj safe-push → fetch → conflict 確認 → dry-run → 確認 → push の安全なワークフロー
#
# NOTE: Claude Code のシェルスナップショットは単一アンダースコアプレフィックスの
# 関数 (_foo) をキャプチャしない。そのため、ヘルパーロジックは jj() 関数内に
# インライン化し、外部関数への依存を避ける必要がある。

jj() {
  case "$1:$2" in
    git:push)
      case "$*" in
        *--dry-run*)
          # dry-run 実行時にフラグを作成（次回の push を許可するため）
          local __sp_dir="$HOME/.cache/jj-safe-push"
          mkdir -p "$__sp_dir"
          date +%s > "$__sp_dir/dry-run-$$"
          ;;
        *)
          # dry-run フラグを確認: 5分以内に作成されたフラグがあれば許可する
          local __sp_dir="$HOME/.cache/jj-safe-push"
          local __sp_flag=""
          if [ -d "$__sp_dir" ]; then
            __sp_flag=$(find "$__sp_dir" -maxdepth 1 -type f -mmin -5 -print -quit 2>/dev/null)
          fi
          if [ -n "$__sp_flag" ]; then
            rm -f "$__sp_flag"
          else
            printf '\033[31mError: jj git push の直接実行は禁止されています。\033[0m\n' >&2
            printf 'jj safe-push を使用してください。\n' >&2
            return 1
          fi
          ;;
      esac
      ;;
    safe-push:*)
      shift
      # safe-push ワークフロー: fetch → conflict 確認 → dry-run → 確認 → push
      printf '=== Step 1: リモートの最新状態を取得 ===\n'
      if ! command jj git fetch; then
        printf '\033[31mError: jj git fetch に失敗しました。\033[0m\n' >&2
        return 1
      fi

      printf '\n=== Step 2: bookmark の diverge を確認 ===\n'
      local __sp_conflicts
      __sp_conflicts=$(command jj bookmark list --conflicted 2>&1)
      if [ -n "$__sp_conflicts" ]; then
        printf '\033[33mConflicted bookmarks が検出されました:\033[0m\n' >&2
        printf '%s\n' "$__sp_conflicts" >&2
        printf '\ndiverge を解消してから再度 jj safe-push を実行してください。\n' >&2
        return 1
      fi
      printf 'conflicted bookmark なし\n'

      printf '\n=== Step 3: dry-run で push 内容を確認 ===\n'
      if ! command jj git push --dry-run "$@"; then
        printf '\033[31mError: dry-run に失敗しました。\033[0m\n' >&2
        return 1
      fi

      printf '\nPush を実行しますか? (y/N): '
      read -r reply
      case "$reply" in
        [Yy]|[Yy]es)
          command jj git push "$@"
          ;;
        *)
          printf 'Push をキャンセルしました。\n'
          return 0
          ;;
      esac
      return $?
      ;;
  esac

  command jj "$@"
}
