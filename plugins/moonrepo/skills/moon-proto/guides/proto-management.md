# Toolchain Management with proto

[proto](https://moonrepo.dev/proto) is a next-generation multi-language toolchain manager that ensures consistent tool versions across your local environment and CI.

## .prototools

The primary configuration file for `proto` is `.prototools`. It defines the required versions for various languages and tools.

```toml
# Example .prototools
node = "20.11.0"
npm = "10.2.4"
rust = "1.75.0"
go = "1.22.0"
```

## Basic Commands

- `proto use`: Install all tools defined in `.prototools`.
- `proto install <tool> <version>`: Manually install a specific tool/version.
- `proto list <tool>`: List installed versions of a tool.
- `proto run <tool> -- <args>`: Run a tool through proto.

## Benefits

- **Consistency**: Guarantees that everyone on the team uses the exact same versions.
- **Speed**: Fast installation and execution.
- **Portability**: Works across Windows, macOS, and Linux without external dependencies.
- **Ecosystem**: Supports a wide range of languages including Node.js, Rust, Go, Python, and more.

## Moonrepo Integration

Moonrepo leverages `proto` to manage its internal toolchain. When `.moon/toolchain.yml` is configured, Moon will automatically use the versions specified in `.prototools`.
