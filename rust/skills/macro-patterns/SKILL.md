---
name: macro-patterns
description: This skill should be used when the user asks to "create a macro", "generate a macro", "use macro_rules", "procedural macro", "derive macro", "reduce boilerplate with macros", or mentions macro patterns like builder, enum iteration, or code generation.
version: 0.1.0
---

# Rust Macro Patterns

## Overview

This skill provides guidance for creating and using Rust macros to reduce code duplication and generate boilerplate, covering both declarative (`macro_rules!`) and procedural macros.

## Declarative Macros (macro_rules!)

### Basic Syntax

```rust
macro_rules! macro_name {
    (pattern) => {
        expansion
    };
}
```

### Simple Example - Print with Label

```rust
macro_rules! debug_print {
    ($val:expr) => {
        println!("{} = {:?}", stringify!($val), $val);
    };
}

// Usage
let x = 42;
debug_print!(x);  // Prints: x = 42
```

### Pattern Types

- `$name:expr` - Expression
- `$name:ident` - Identifier
- `$name:ty` - Type
- `$name:pat` - Pattern
- `$name:stmt` - Statement
- `$name:block` - Block
- `$name:item` - Item (function, struct, etc.)
- `$name:tt` - Token tree (any single token)

### Repetition

Use `$(...)*` for zero or more, `$(...)+` for one or more:

```rust
macro_rules! create_function {
    ($func_name:ident, $($arg:ident: $typ:ty),*) => {
        fn $func_name($($arg: $typ),*) {
            $(println!("{}: {:?}", stringify!($arg), $arg);)*
        }
    };
}

create_function!(print_values, x: i32, y: String);
```

## Common Macro Patterns

### Builder Pattern Generator

```rust
macro_rules! builder {
    ($name:ident { $($field:ident: $typ:ty),* }) => {
        pub struct $name {
            $($field: $typ,)*
        }

        paste::paste! {
            impl $name {
                pub fn new() -> Self {
                    Self {
                        $($field: Default::default(),)*
                    }
                }

                $(
                    pub fn $field(mut self, value: $typ) -> Self {
                        self.$field = value;
                        self
                    }
                )*
            }
        }
    };
}

// Usage
builder!(Config {
    host: String,
    port: u16
});

let config = Config::new()
    .host("localhost".to_string())
    .port(8080);
```

### Enum Iterator

```rust
macro_rules! enum_iterator {
    ($name:ident { $($variant:ident),* }) => {
        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum $name {
            $($variant,)*
        }

        impl $name {
            pub fn variants() -> &'static [$name] {
                &[$($name::$variant,)*]
            }
        }
    };
}

// Usage
enum_iterator!(Color { Red, Green, Blue });

for color in Color::variants() {
    println!("{:?}", color);
}
```

### HashMap Initialization

```rust
macro_rules! hashmap {
    ($($key:expr => $val:expr),* $(,)?) => {{
        let mut map = std::collections::HashMap::new();
        $(map.insert($key, $val);)*
        map
    }};
}

// Usage
let map = hashmap! {
    "one" => 1,
    "two" => 2,
};
```

### Test Case Generator

```rust
macro_rules! test_cases {
    ($test_name:ident: $($name:ident($($arg:expr),*) => $expected:expr),* $(,)?) => {
        $(
            #[test]
            fn $name() {
                assert_eq!($test_name($($arg),*), $expected);
            }
        )*
    };
}

// Usage
fn add(a: i32, b: i32) -> i32 {
    a + b
}

test_cases! {
    add:
    test_add_positive(1, 2) => 3,
    test_add_negative(-1, -2) => -3,
    test_add_zero(0, 0) => 0,
}
```

### Error Type Generator

```rust
macro_rules! define_error {
    ($name:ident { $($variant:ident($inner:ty)),* }) => {
        #[derive(Debug)]
        pub enum $name {
            $($variant($inner),)*
        }

        $(
            impl From<$inner> for $name {
                fn from(err: $inner) -> Self {
                    $name::$variant(err)
                }
            }
        )*

        impl std::fmt::Display for $name {
            fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                match self {
                    $($name::$variant(e) => write!(f, "{}: {}", stringify!($variant), e),)*
                }
            }
        }

        impl std::error::Error for $name {}
    };
}

// Usage
define_error!(AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError)
});
```

## Procedural Macros

### Derive Macros

Custom derive macros require separate crate with `proc-macro = true`:

```toml
# Cargo.toml
[lib]
proc-macro = true

[dependencies]
syn = "2.0"
quote = "1.0"
proc-macro2 = "1.0"
```

Basic derive macro:
```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;

    let expanded = quote! {
        impl #name {
            pub fn builder() -> Builder {
                Builder::default()
            }
        }
    };

    TokenStream::from(expanded)
}
```

### Attribute Macros

```rust
#[proc_macro_attribute]
pub fn timed(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let name = &input.sig.ident;
    let block = &input.block;

    let expanded = quote! {
        fn #name() {
            let start = std::time::Instant::now();
            #block
            println!("Took: {:?}", start.elapsed());
        }
    };

    TokenStream::from(expanded)
}
```

### Function-like Macros

```rust
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    // Parse SQL string, validate syntax, generate code
    todo!()
}

// Usage: sql!("SELECT * FROM users WHERE id = ?")
```

## Best Practices

1. **Use macros sparingly** - Prefer functions when possible
2. **Document well** - Macros are hard to understand
3. **Keep simple** - Complex macros are maintenance burden
4. **Test thoroughly** - Use `cargo expand` to see output
5. **Hygiene** - Avoid variable name conflicts
6. **Error messages** - Use `compile_error!` for clear errors

## Debugging Macros

**cargo-expand** - See macro expansions:
```bash
cargo install cargo-expand
cargo expand --lib  # Expand all macros
cargo expand module::function  # Expand specific item
```

**Manual expansion**:
```rust
println!("{}", stringify!(macro_call!()));
```

## Additional Resources

### Reference Files

For detailed macro guides:
- **`references/macro-rules-guide.md`** - Complete macro_rules! patterns and techniques
- **`references/proc-macro-guide.md`** - Procedural macro development guide

### Scripts

Utility scripts:
- **`scripts/expand-macro.sh`** - Wrapper for cargo-expand with formatting

Consult these resources for advanced macro patterns and development techniques.
