use anyhow::Result;
use claude_code_hooks::{HookError, UserPromptSubmitEvent};

use crate::models::{HookSpecificOutput, PromptEvaluator, UserPromptSubmitResponse};
use crate::utils::{log_safely, send_notification_safely};

/// Handler for user prompt submission events
pub struct PromptHandler {
    evaluator: PromptEvaluator,
}

impl Default for PromptHandler {
    fn default() -> Self {
        Self::new(60)
    }
}

impl PromptHandler {
    pub fn new(threshold: i32) -> Self {
        Self {
            evaluator: PromptEvaluator::new(threshold),
        }
    }

    pub fn handle(&self, event: &UserPromptSubmitEvent) -> Result<(), HookError> {
        let score = self.evaluator.evaluate(&event.prompt);
        let notification_message = format!("プロンプト評価スコア: {score}/100");

        log_safely(
            "PROMPT_SUBMIT",
            &format!("スコア: {}, プロンプト: {}", score, &event.prompt[..50.min(event.prompt.len())])
        );

        if !self.evaluator.passes_threshold(&event.prompt) {
            send_notification_safely(
                "Claude Code - プロンプト品質警告",
                "品質スコアが低すぎます",
                &notification_message
            );

            let response = UserPromptSubmitResponse {
                decision: Some("block".to_string()),
                reason: Some(format!("プロンプト評価スコアが低すぎます ({score})")),
                hook_specific_output: Some(HookSpecificOutput {
                    hook_event_name: "UserPromptSubmit".to_string(),
                    additional_context: notification_message,
                }),
                continue_: false,
                stop_reason: Some("プロンプトの品質が基準を満たしていません".to_string()),
                suppress_output: Some(true),
            };

            if let Ok(json_response) = serde_json::to_string_pretty(&response) {
                println!("{}", json_response);
            } else {
                eprintln!("Error serializing response");
            }
        } else {
            send_notification_safely(
                "Claude Code - プロンプト受信",
                "品質チェック完了",
                &notification_message
            );

            let response = UserPromptSubmitResponse {
                decision: None,
                reason: None,
                hook_specific_output: Some(HookSpecificOutput {
                    hook_event_name: "UserPromptSubmit".to_string(),
                    additional_context: notification_message,
                }),
                continue_: true,
                stop_reason: None,
                suppress_output: Some(false),
            };

            println!("{}", serde_json::to_string_pretty(&response).unwrap());
        }

        Ok(())
    }
}
