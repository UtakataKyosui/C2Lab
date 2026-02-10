---
name: macro
description: Generate common Rust macro patterns
argument-hint: "<builder|error-type|test>"
allowed-tools: [Write, Read, Edit]
---

# Macro Generator Command

Generate common Rust macro patterns to reduce boilerplate code.

## Supported Patterns

### Builder Pattern (`builder`)

Generate a builder macro for struct initialization:
- Ask user for struct name and fields
- Generate `builder!` macro invocation
- Include builder pattern implementation

### Error Type (`error-type`)

Generate error type enum with From implementations:
- Ask for error name and variants
- Generate enum with derive macros
- Add From implementations for each variant
- Include Display and Error trait implementations

### Test Generator (`test`)

Generate test case macro for multiple test scenarios:
- Ask for function to test
- Generate `test_cases!` macro with examples
- Include parametrized test cases

## Execution

1. Parse argument to determine pattern type
2. Gather required information from user (struct name, fields, etc.)
3. Generate macro code using templates from macro-patterns skill
4. Write to appropriate file or display for user to copy
5. Explain usage and provide example

Refer to macro-patterns skill for detailed macro templates and patterns.
