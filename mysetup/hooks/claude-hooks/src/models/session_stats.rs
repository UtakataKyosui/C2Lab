use std::collections::HashMap;

use chrono::{DateTime, Utc};
use claude_code_hooks::{HookEvent, PostToolUseEvent, PreToolUseEvent, helpers};
use serde::{Deserialize, Serialize};

use crate::models::{BashCommand, InfoSession, RustOperation};

/// Global statistics and logging state
#[derive(Debug, Default, Serialize, Deserialize)]
pub struct SessionStats {
    pub session_id: String,
    pub start_time: Option<DateTime<Utc>>,
    pub bash_commands: Vec<BashCommand>,
    pub rust_operations: Vec<RustOperation>,
    pub mcp_usage: HashMap<String, u32>,
    pub info_gathering_sessions: Vec<InfoSession>,
}

impl SessionStats {
    pub fn new(session_id: String) -> Self {
        Self {
            session_id,
            start_time: Some(Utc::now()),
            bash_commands: Vec::new(),
            rust_operations: Vec::new(),
            mcp_usage: HashMap::new(),
            info_gathering_sessions: Vec::new(),
        }
    }

    pub fn record_bash_command(&mut self, event: &PreToolUseEvent) {
        use crate::security::CommandValidator;
        
        if let Some(command) = event.tool_input.get("command") {
            if let Some(cmd_str) = command.as_str() {
                let validator = CommandValidator::new();
                let validation = validator.validate(cmd_str);
                
                let bash_cmd = BashCommand {
                    timestamp: Utc::now(),
                    command: cmd_str.to_string(),
                    session_id: event.common.session_id.clone(),
                    cwd: event.common.cwd.clone(),
                    is_destructive: validation.is_destructive,
                    is_system_level: validation.is_system_level,
                };
                
                self.bash_commands.push(bash_cmd);
            }
        }
    }

    pub fn record_rust_operation(&mut self, event: &PreToolUseEvent) {
        if let Some(file_path) = event.tool_input.get("file_path") {
            if let Some(path_str) = file_path.as_str() {
                if path_str.ends_with(".rs") {
                    let rust_op = RustOperation {
                        timestamp: Utc::now(),
                        operation_type: event.tool_name.clone(),
                        file_path: path_str.to_string(),
                        session_id: event.common.session_id.clone(),
                        lint_applied: false, // Will be updated after processing
                        format_applied: false,
                    };
                    
                    self.rust_operations.push(rust_op);
                }
            }
        }
    }

    pub fn record_mcp_usage(&mut self, event: &HookEvent) {
        if let Some(info) = helpers::mcp::get_mcp_info(event) {
            *self.mcp_usage.entry(info.server_name.clone()).or_insert(0) += 1;
            
            // Record information gathering sessions
            let category = helpers::mcp::categorize_mcp_tool(event);
            if matches!(category, helpers::McpToolCategory::Documentation) {
                if let HookEvent::PreToolUse(pre_event) = event {
                    let info_session = InfoSession {
                        timestamp: Utc::now(),
                        session_id: pre_event.common.session_id.clone(),
                        tool_name: info.tool_name.clone(),
                        query_info: pre_event.tool_input.clone(),
                        result_summary: None, // Will be updated on PostToolUse
                    };
                    
                    self.info_gathering_sessions.push(info_session);
                }
            }
        }
    }

    pub fn update_info_session_result(&mut self, event: &PostToolUseEvent) {
        if let Some(info) = helpers::mcp::get_mcp_info(&HookEvent::PostToolUse(event.clone())) {
            if let Some(session) = self.info_gathering_sessions.iter_mut()
                .filter(|s| s.tool_name == info.tool_name && s.session_id == event.common.session_id)
                .last() {
                
                // Extract result summary from tool response
                let summary = if let Some(content) = event.tool_response.get("content") {
                    Some(format!("Retrieved: {}", 
                        content.as_str()
                            .unwrap_or("Data retrieved")
                            .chars()
                            .take(100)
                            .collect::<String>()
                    ))
                } else {
                    Some("Information retrieved successfully".to_string())
                };
                
                session.result_summary = summary;
            }
        }
    }


    pub fn save_to_file(&self) -> Result<(), anyhow::Error> {
        let home_dir = dirs::home_dir().ok_or_else(|| anyhow::anyhow!("Could not find home directory"))?;
        let logs_dir = home_dir.join(".claude").join("hook-logs");
        std::fs::create_dir_all(&logs_dir)?;
        
        let log_file = logs_dir.join(format!("session-{}.json", self.session_id));
        let json_data = serde_json::to_string_pretty(self)?;
        std::fs::write(log_file, json_data)?;
        
        Ok(())
    }

    pub fn print_summary(&self) {
        println!("\n📊 Session Summary ({})", self.session_id);
        
        if let Some(start) = self.start_time {
            let duration = Utc::now().signed_duration_since(start);
            println!("  ⏱️  Duration: {} minutes", duration.num_minutes());
        }
        
        if !self.bash_commands.is_empty() {
            println!("  💻 Bash Commands: {}", self.bash_commands.len());
            let destructive_count = self.bash_commands.iter().filter(|c| c.is_destructive).count();
            let system_count = self.bash_commands.iter().filter(|c| c.is_system_level).count();
            
            if destructive_count > 0 {
                println!("    ⚠️  Destructive commands: {}", destructive_count);
            }
            if system_count > 0 {
                println!("    🔧 System-level commands: {}", system_count);
            }
        }
        
        if !self.rust_operations.is_empty() {
            println!("  🦀 Rust Operations: {}", self.rust_operations.len());
            let formatted_count = self.rust_operations.iter().filter(|r| r.format_applied).count();
            let linted_count = self.rust_operations.iter().filter(|r| r.lint_applied).count();
            
            if formatted_count > 0 {
                println!("    ✨ Auto-formatted: {}", formatted_count);
            }
            if linted_count > 0 {
                println!("    🔍 Auto-linted: {}", linted_count);
            }
        }
        
        if !self.mcp_usage.is_empty() {
            println!("  🔌 MCP Usage:");
            for (server, count) in &self.mcp_usage {
                println!("    {} x{}", server, count);
            }
        }
        
        if !self.info_gathering_sessions.is_empty() {
            println!("  📚 Information Sessions: {}", self.info_gathering_sessions.len());
        }
    }
}