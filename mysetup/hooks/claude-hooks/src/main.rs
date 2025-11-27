//! Integrated Claude Code Hooks
//!
//! Comprehensive hook program combining features from both projects:
//! - Prompt quality evaluation
//! - Bash command logging and security validation
//! - Rust/Node.js/Python file automation (lint/format)
//! - MCP tool usage tracking
//! - Session statistics and reporting

use claude_code_hooks::prelude::*;
use std::sync::{Arc, Mutex};
use anyhow::Result;

use crate::models::SessionStats;
use crate::handlers::{BashHandler, FileHandler, McpHandler, PromptHandler};

#[macro_use]
mod utils;
mod models;
mod handlers;
mod automation;
mod security;

#[tokio::main]
async fn main() -> Result<(), HookError> {
    // Initialize global state
    let stats = Arc::new(Mutex::new(SessionStats::default()));
    let prompt_handler = Arc::new(PromptHandler::default());
    let bash_handler = Arc::new(BashHandler::default());
    let file_handler = Arc::new(FileHandler);
    let mcp_handler = Arc::new(McpHandler);

    let hook = HookRunner::new()
        // Prompt quality evaluation
        .on_user_prompt_submit_sync({
            let handler = prompt_handler.clone();
            move |event| handler.handle(&event)
        })
        // Pre-tool-use: logging and validation
        .on_pre_tool_use_sync({
            let stats = stats.clone();
            let bash_handler = bash_handler.clone();
            let file_handler = file_handler.clone();
            let mcp_handler = mcp_handler.clone();

            move |event| -> Result<(), HookError> {
                let mut session_stats = stats.lock().expect("Failed to lock session stats");

                // Initialize session if first event
                if session_stats.session_id.is_empty() {
                    *session_stats = SessionStats::new(event.common.session_id.clone());
                    println!("🚀 Starting session: {}", event.common.session_id);
                }

                let tool_name = &event.tool_name;
                let hook_event = HookEvent::PreToolUse(event.clone());

                // Handle different tool types
                match tool_name.as_str() {
                    "Bash" | "Task" => {
                        bash_handler.handle(&mut session_stats, &event)?;
                    }
                    "Write" | "Edit" | "MultiEdit" => {
                        file_handler.handle_pre(&mut session_stats, &event)?;
                    }
                    _ => {
                        // Check for MCP tools
                        if hook_event.is_mcp_tool() {
                            mcp_handler.handle_pre(&mut session_stats, &hook_event)?;
                        } else {
                            println!("🔧 [Tool] {}", tool_name);
                        }
                    }
                }

                Ok(())
            }
        })
        // Post-tool-use: automation and result recording
        .on_post_tool_use_sync({
            let stats = stats.clone();
            let file_handler = file_handler.clone();
            let mcp_handler = mcp_handler.clone();

            move |event| -> Result<(), HookError> {
                let mut session_stats = stats.lock().unwrap();

                // Handle MCP post-processing
                let hook_event = HookEvent::PostToolUse(event.clone());
                if hook_event.is_mcp_tool() {
                    mcp_handler.handle_post(&mut session_stats, &event)?;
                }

                // Handle file operations completion (format/lint)
                if matches!(event.tool_name.as_str(), "Write" | "Edit" | "MultiEdit") {
                    file_handler.handle_post(&mut session_stats, &event)?;
                }

                Ok(())
            }
        })
        // Session end: print summary and save
        .on_stop_sync({
            let stats = stats.clone();

            move |event| -> Result<(), HookError> {
                let session_stats = stats.lock().unwrap();

                println!("🛑 Session ended: {}", event.common.session_id);
                session_stats.print_summary();

                // Save session data
                if let Err(e) = session_stats.save_to_file() {
                    eprintln!("Failed to save session data: {}", e);
                }

                Ok(())
            }
        });

    println!("🎯 Integrated Claude Code Hooks activated");
    println!("   Features:");
    println!("     • Prompt quality evaluation");
    println!("     • Bash command security validation");
    println!("     • Multi-language auto-format/lint (Rust, Node.js, Python)");
    println!("     • MCP tool tracking");
    println!("     • Session statistics");
    println!("   Logs saved to: ~/.claude/hook-logs/");
    println!("");

    hook.run_from_stdin().await
}
