# jj safe-push: jj git push の直接実行を禁止し、安全な push ワークフローを強制する
# bash / zsh 両対応
#
# - jj git push (--dry-run なし) → ブロック
# - jj git push --dry-run → 許可
# - jj safe-push → fetch → conflict 確認 → dry-run → 確認 → push の安全なワークフロー

jj() {
  case "$1:$2" in
    git:push)
      case "$*" in
        *--dry-run*) ;;
        *)
          printf '\033[31mError: jj git push の直接実行は禁止されています。\033[0m\n' >&2
          printf 'jj safe-push を使用してください。\n' >&2
          return 1
          ;;
      esac
      ;;
    safe-push:*)
      shift
      _jj_safe_push "$@"
      return $?
      ;;
  esac

  command jj "$@"
}

_jj_safe_push() {
  printf '=== Step 1: リモートの最新状態を取得 ===\n'
  if ! command jj git fetch; then
    printf '\033[31mError: jj git fetch に失敗しました。\033[0m\n' >&2
    return 1
  fi

  printf '\n=== Step 2: bookmark の diverge を確認 ===\n'
  local conflicts
  conflicts=$(command jj bookmark list --conflicted 2>&1)
  if [ -n "$conflicts" ]; then
    printf '\033[33mConflicted bookmarks が検出されました:\033[0m\n' >&2
    printf '%s\n' "$conflicts" >&2
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
}
