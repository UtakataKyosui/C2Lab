use anyhow::Result;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Project type detector
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProjectType {
    Rust,
    NodeJs,
    Python,
    Unknown,
}

impl ProjectType {
    pub fn detect() -> Self {
        if Path::new("Cargo.toml").exists() {
            ProjectType::Rust
        } else if Path::new("package.json").exists() {
            ProjectType::NodeJs
        } else if Path::new("requirements.txt").exists() || Path::new("pyproject.toml").exists() {
            ProjectType::Python
        } else {
            ProjectType::Unknown
        }
    }
}

/// Formatter for various project types
pub struct Formatter;

impl Formatter {
    /// Run format for all detected project types
    pub fn run_all() -> Vec<FormatResult> {
        let mut results = Vec::new();

        let project_type = ProjectType::detect();
        match project_type {
            ProjectType::Rust => {
                results.extend(Self::format_rust());
            }
            ProjectType::NodeJs => {
                results.extend(Self::format_nodejs());
            }
            ProjectType::Python => {
                results.extend(Self::format_python());
            }
            ProjectType::Unknown => {
                results.push(FormatResult::skipped("No recognized project type found"));
            }
        }

        results
    }

    /// Format specific file
    pub fn format_file(file_path: &Path) -> Vec<FormatResult> {
        let extension = file_path.extension().and_then(|s| s.to_str());

        match extension {
            Some("rs") => Self::format_rust_file(file_path),
            Some("js") | Some("jsx") | Some("ts") | Some("tsx") => Self::format_js_file(file_path),
            Some("py") => Self::format_python_file(file_path),
            _ => vec![FormatResult::skipped(&format!(
                "Unsupported file type: {:?}",
                file_path
            ))],
        }
    }

    fn format_rust() -> Vec<FormatResult> {
        vec![Self::run_cargo_fmt()]
    }

    fn format_rust_file(file_path: &Path) -> Vec<FormatResult> {
        match find_cargo_project_root(file_path) {
            Ok(root) => vec![Self::run_cargo_fmt_file(file_path, &root)],
            Err(_) => vec![Self::run_rustfmt(file_path)],
        }
    }

    fn run_cargo_fmt() -> FormatResult {
        match Command::new("cargo").args(["fmt"]).output() {
            Ok(output) if output.status.success() => {
                FormatResult::success("cargo fmt", "Rust project formatted")
            }
            Ok(output) => FormatResult::error(
                "cargo fmt",
                &String::from_utf8_lossy(&output.stderr),
            ),
            Err(e) => FormatResult::error("cargo fmt", &e.to_string()),
        }
    }

    fn run_cargo_fmt_file(file_path: &Path, project_root: &Path) -> FormatResult {
        let file_path_str = match file_path.to_str() {
            Some(s) => s,
            None => return FormatResult::error("cargo fmt", "File path is not valid UTF-8"),
        };
        match Command::new("cargo")
            .current_dir(project_root)
            .args(["fmt", "--"])
            .arg(file_path)
            .output()
        {
            Ok(output) if output.status.success() => {
                FormatResult::success("cargo fmt", &format!("Formatted: {:?}", file_path))
            }
            Ok(output) => FormatResult::error(
                "cargo fmt",
                &String::from_utf8_lossy(&output.stderr),
            ),
            Err(e) => FormatResult::error("cargo fmt", &e.to_string()),
        }
    }

    fn run_rustfmt(file_path: &Path) -> FormatResult {
        match Command::new("rustfmt")
            .arg(file_path)
            .output()
        {
            Ok(output) if output.status.success() => {
                FormatResult::success("rustfmt", &format!("Formatted: {:?}", file_path))
            }
            Ok(output) => FormatResult::error(
                "rustfmt",
                &String::from_utf8_lossy(&output.stderr),
            ),
            Err(_) => FormatResult::not_available("rustfmt"),
        }
    }

    fn format_nodejs() -> Vec<FormatResult> {
        let mut results = Vec::new();

        // Try prettier
        match Command::new("npx")
            .args(["prettier", "--write", "."])
            .output()
        {
            Ok(output) if output.status.success() => {
                results.push(FormatResult::success("prettier", "Formatted with prettier"));
            }
            Ok(output) => {
                results.push(FormatResult::error(
                    "prettier",
                    &String::from_utf8_lossy(&output.stderr),
                ));
            }
            Err(_) => {
                // Try npm run format
                match Command::new("npm").args(["run", "format"]).output() {
                    Ok(output) if output.status.success() => {
                        results.push(FormatResult::success("npm run format", "Formatted"));
                    }
                    _ => results.push(FormatResult::not_available("prettier or npm run format")),
                }
            }
        }

        results
    }

    fn format_js_file(file_path: &Path) -> Vec<FormatResult> {
        // Try prettier on the specific file
        match Command::new("npx")
            .args(["prettier", "--write"])
            .arg(file_path)
            .output()
        {
            Ok(output) if output.status.success() => {
                vec![FormatResult::success("prettier", &format!("Formatted with prettier: {:?}", file_path))]
            }
            Ok(output) => {
                vec![FormatResult::error(
                    "prettier",
                    &String::from_utf8_lossy(&output.stderr),
                )]
            }
            Err(_) => {
                vec![FormatResult::not_available("prettier")]
            }
        }
    }

    fn format_python() -> Vec<FormatResult> {
        match Command::new("black").args(["."]).output() {
            Ok(output) if output.status.success() => {
                vec![FormatResult::success("black", "Python project formatted")]
            }
            Ok(output) => {
                vec![FormatResult::error(
                    "black",
                    &String::from_utf8_lossy(&output.stderr),
                )]
            }
            Err(_) => vec![FormatResult::not_available("black")],
        }
    }

    fn format_python_file(file_path: &Path) -> Vec<FormatResult> {
        match Command::new("black").arg(file_path).output() {
            Ok(output) if output.status.success() => {
                vec![FormatResult::success(
                    "black",
                    &format!("Formatted: {:?}", file_path),
                )]
            }
            Ok(output) => {
                vec![FormatResult::error(
                    "black",
                    &String::from_utf8_lossy(&output.stderr),
                )]
            }
            Err(_) => vec![FormatResult::not_available("black")],
        }
    }
}

/// Format result
#[derive(Debug, Clone)]
pub struct FormatResult {
    pub tool: String,
    pub status: FormatStatus,
    pub message: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FormatStatus {
    Success,
    Error,
    NotAvailable,
    Skipped,
}

impl FormatResult {
    pub fn success(tool: &str, message: &str) -> Self {
        Self {
            tool: tool.to_string(),
            status: FormatStatus::Success,
            message: message.to_string(),
        }
    }

    pub fn error(tool: &str, message: &str) -> Self {
        Self {
            tool: tool.to_string(),
            status: FormatStatus::Error,
            message: message.to_string(),
        }
    }

    pub fn not_available(tool: &str) -> Self {
        Self {
            tool: tool.to_string(),
            status: FormatStatus::NotAvailable,
            message: format!("{} is not available", tool),
        }
    }

    pub fn skipped(message: &str) -> Self {
        Self {
            tool: "".to_string(),
            status: FormatStatus::Skipped,
            message: message.to_string(),
        }
    }

    pub fn emoji(&self) -> &'static str {
        match self.status {
            FormatStatus::Success => "✅",
            FormatStatus::Error => "❌",
            FormatStatus::NotAvailable => "⚠️",
            FormatStatus::Skipped => "ℹ️",
        }
    }

    pub fn print(&self) {
        println!("  {} {}: {}", self.emoji(), self.tool, self.message);
    }
}

/// Find Cargo project root
fn find_cargo_project_root(file_path: &Path) -> Result<PathBuf> {
    let mut current_dir = file_path.parent().unwrap_or(file_path);

    loop {
        let cargo_toml = current_dir.join("Cargo.toml");
        if cargo_toml.exists() {
            return Ok(current_dir.to_path_buf());
        }

        match current_dir.parent() {
            Some(parent) => current_dir = parent,
            None => return Err(anyhow::anyhow!("No Cargo.toml found in parent directories")),
        }
    }
}
