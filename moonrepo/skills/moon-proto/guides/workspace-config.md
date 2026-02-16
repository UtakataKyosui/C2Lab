# Workspace Configuration and CI/CD

The workspace is the heart of a Moonrepo setup, defined by the `.moon/` directory and its configuration files.

## .moon/workspace.yml

This file defines the overall structure of the workspace and global settings.

```yaml
vcs:
  manager: 'git'
  defaultBranch: 'main'

projects:
  - 'apps/*'
  - 'packages/*'
  - 'shared/configs'

runner:
  cacheLifetime: '7 days'
  inheritColorsForPipedTasks: true
```

## Project Discovery

Moon automatically discovers projects based on the `projects` glob patterns in `workspace.yml`. Projects are identified as directories containing a `moon.yml` or a supported manifest file (like `package.json`).

## Dependency Graph

Moon builds a dependency graph between projects and tasks. This allows it to:
- Run tasks in the correct order.
- Re-run only the tasks affected by a change.

## CI/CD Integration

Moon is designed to optimize CI/CD pipelines.

- **Selective Execution**: Use `moon run :build --affected` to build only what's necessary.
- **Remote Caching**: (Optional) Share task caches across CI runs and team members.
- **Setup Actions**: Use `moonrepo/setup-toolchain` in GitHub Actions for easy environment setup.

```yaml
# Example GitHub Action step
# セキュリティ: 本番環境ではタグではなくコミット SHA に固定することを推奨
# 例: moonrepo/setup-toolchain@<commit-sha>
- uses: moonrepo/setup-toolchain@v0
  with:
    auto-install: true
- run: moon run :build --affected
```
