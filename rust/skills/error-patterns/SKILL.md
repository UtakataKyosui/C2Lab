---
name: error-patterns
description: This skill should be used when the user encounters "compilation error", "borrow checker error", "lifetime error", "trait bound error", "type mismatch", asks to "fix this error", "debug this issue", or mentions specific Rust error codes like E0277, E0597, E0382.
version: 0.1.0
---

# Common Rust Error Patterns and Fixes

## Overview

This skill provides guidance for diagnosing and fixing common Rust compilation errors, with focus on ownership, borrowing, lifetimes, and type system errors.

## Ownership and Borrowing Errors

### E0382: Use of Moved Value

**Error:**
```rust
let s = String::from("hello");
let s2 = s;  // s moved here
println!("{}", s);  // Error: value borrowed here after move
```

**Fix:** Clone if you need both, or use references:
```rust
// Option 1: Clone
let s = String::from("hello");
let s2 = s.clone();
println!("{} {}", s, s2);

// Option 2: Use reference
let s = String::from("hello");
let s2 = &s;
println!("{} {}", s, s2);
```

### E0502: Cannot Borrow as Mutable Because Also Borrowed as Immutable

**Error:**
```rust
let mut vec = vec![1, 2, 3];
let first = &vec[0];  // Immutable borrow
vec.push(4);  // Error: mutable borrow occurs here
println!("{}", first);
```

**Fix:** End immutable borrow before mutable borrow:
```rust
let mut vec = vec![1, 2, 3];
let first_val = vec[0];  // Copy the value
vec.push(4);  // OK: no active borrow
println!("{}", first_val);

// Or: Limit scope
{
    let first = &vec[0];
    println!("{}", first);
}  // Borrow ends here
vec.push(4);  // OK
```

### E0499: Cannot Borrow as Mutable More Than Once

**Error:**
```rust
let mut s = String::from("hello");
let r1 = &mut s;
let r2 = &mut s;  // Error: second mutable borrow
println!("{}, {}", r1, r2);
```

**Fix:** Use one mutable reference at a time or split into separate scopes:
```rust
let mut s = String::from("hello");
{
    let r1 = &mut s;
    r1.push_str(" world");
}  // r1 goes out of scope
let r2 = &mut s;
r2.push_str("!");
```

## Lifetime Errors

### E0597: Borrowed Value Does Not Live Long Enough

**Error:**
```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    let result = String::from("hello");
    &result  // Error: returns reference to local variable
}
```

**Fix:** Return owned value instead:
```rust
fn longest(x: &str, y: &str) -> String {
    String::from("hello")  // Return owned String
}

// Or if you need to return a reference, ensure it outlives function:
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

### E0106: Missing Lifetime Specifier

**Error:**
```rust
fn first_word(s: &str) -> &str {  // Which lifetime?
    &s[..1]
}

struct Wrapper {
    data: &str,  // Error: missing lifetime
}
```

**Fix:** Add explicit lifetime annotations:
```rust
fn first_word<'a>(s: &'a str) -> &'a str {
    &s[..1]
}

struct Wrapper<'a> {
    data: &'a str,
}
```

## Type System Errors

### E0277: Trait Bound Not Satisfied

**Error:**
```rust
fn print_vec<T>(vec: Vec<T>) {
    println!("{:?}", vec);  // Error: T doesn't implement Debug
}
```

**Fix:** Add trait bound:
```rust
use std::fmt::Debug;

fn print_vec<T: Debug>(vec: Vec<T>) {
    println!("{:?}", vec);
}

// Or use where clause:
fn print_vec<T>(vec: Vec<T>)
where
    T: Debug,
{
    println!("{:?}", vec);
}
```

### E0308: Mismatched Types

**Error:**
```rust
fn get_number() -> i32 {
    "42"  // Error: expected i32, found &str
}
```

**Fix:** Convert to correct type:
```rust
fn get_number() -> i32 {
    42
}

// Or parse string:
fn parse_number(s: &str) -> Result<i32, std::num::ParseIntError> {
    s.parse()
}
```

### E0425: Cannot Find Value in This Scope

**Error:**
```rust
fn main() {
    println!("{}", undefined_var);  // Error: not found
}
```

**Fix:** Define the variable or import the item:
```rust
fn main() {
    let undefined_var = 42;
    println!("{}", undefined_var);
}

// Or import:
use std::collections::HashMap;
```

## Pattern Matching Errors

### E0004: Non-Exhaustive Patterns

**Error:**
```rust
enum Color {
    Red,
    Green,
    Blue,
}

fn describe(color: Color) -> &'static str {
    match color {
        Color::Red => "red",
        Color::Green => "green",
        // Error: missing Blue
    }
}
```

**Fix:** Handle all cases or use wildcard:
```rust
fn describe(color: Color) -> &'static str {
    match color {
        Color::Red => "red",
        Color::Green => "green",
        Color::Blue => "blue",
    }
}

// Or use wildcard:
fn describe(color: Color) -> &'static str {
    match color {
        Color::Red => "red",
        _ => "other",
    }
}
```

## Async/Await Errors

### E0728: `await` Only Allowed Inside `async` Function

**Error:**
```rust
fn get_data() {
    let data = fetch().await;  // Error: not in async context
}
```

**Fix:** Make function async:
```rust
async fn get_data() {
    let data = fetch().await;
}
```

### Blocking in Async Context

**Error:**
```rust
async fn process() {
    std::thread::sleep(Duration::from_secs(1));  // Blocks executor
}
```

**Fix:** Use async sleep:
```rust
async fn process() {
    tokio::time::sleep(Duration::from_secs(1)).await;
}
```

## Macro Errors

### Macro Hygiene Issues

**Error:**
```rust
macro_rules! create_var {
    () => {
        let x = 42;
    };
}

fn main() {
    create_var!();
    println!("{}", x);  // Error: cannot find value
}
```

**Fix:** Return value from macro or use explicit variable:
```rust
macro_rules! create_var {
    ($name:ident) => {
        let $name = 42;
    };
}

fn main() {
    create_var!(x);
    println!("{}", x);  // OK
}
```

## Common Clippy Warnings

### Needless Borrow

**Warning:**
```rust
fn takes_ref(s: &String) {
    // ...
}

let s = String::from("hello");
takes_ref(&s);  // OK but could be improved
```

**Fix:** Use `&str` for more flexibility:
```rust
fn takes_ref(s: &str) {  // More flexible
    // ...
}

let s = String::from("hello");
takes_ref(&s);  // Works with String
takes_ref("literal");  // Also works with &str
```

### Unnecessary `mut`

**Warning:**
```rust
let mut x = 5;  // Warning: variable does not need to be mutable
println!("{}", x);
```

**Fix:** Remove `mut` if not mutating:
```rust
let x = 5;
println!("{}", x);
```

## Error Recovery Patterns

### Using Result Instead of Panic

**Bad:**
```rust
fn divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        panic!("Division by zero");
    }
    a / b
}
```

**Good:**
```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

### Error Propagation with `?`

**Bad:**
```rust
fn read_file() -> Result<String, std::io::Error> {
    match std::fs::read_to_string("file.txt") {
        Ok(content) => Ok(content),
        Err(e) => Err(e),
    }
}
```

**Good:**
```rust
fn read_file() -> Result<String, std::io::Error> {
    Ok(std::fs::read_to_string("file.txt")?)
}
```

## Debugging Strategies

1. **Read the error message carefully** - Rust errors are detailed
2. **Check the error code** - Look up E#### codes in Rust error index
3. **Use `cargo check`** - Faster than full build for error checking
4. **Add type annotations** - Help compiler and yourself understand types
5. **Use `dbg!()` macro** - Print values and take ownership temporarily
6. **Run `cargo clippy`** - Catch common mistakes before they become errors
7. **Simplify the code** - Remove complexity to isolate the issue

## Additional Resources

### Reference Files

For comprehensive error guides:
- **`references/error-index.md`** - Complete Rust error code reference
- **`references/clippy-lints.md`** - Common clippy lints and fixes

## Quick Reference Table

| Error Code | Issue | Quick Fix |
|------------|-------|-----------|
| E0382 | Use after move | Clone or use reference |
| E0502 | Immutable + mutable borrow | Limit borrow scope |
| E0499 | Multiple mutable borrows | Use one at a time |
| E0597 | Reference outlives value | Return owned value |
| E0277 | Missing trait bound | Add trait constraint |
| E0308 | Type mismatch | Convert types |
| E0425 | Undefined variable | Define or import |
| E0004 | Non-exhaustive match | Add missing arms |

Consult references for detailed explanations and advanced error patterns.
