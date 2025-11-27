use anyhow::Result;
use chrono::Utc;
use dirs::home_dir;
use std::fs;
use std::path::PathBuf;

/// Log directory path
pub fn get_log_dir() -> Result<PathBuf> {
    let home = home_dir().ok_or_else(|| anyhow::anyhow!("Could not find home directory"))?;
    let log_dir = home.join(".claude").join("hook-logs");
    fs::create_dir_all(&log_dir)?;
    Ok(log_dir)
}

/// Log an event to file
pub fn log_to_file(event_type: &str, details: &str) -> Result<()> {
    use std::fs::OpenOptions;
    use std::io::Write;

    let log_dir = get_log_dir()?;
    let log_file = log_dir.join("hook.log");
    let timestamp = Utc::now().format("%Y-%m-%d %H:%M:%S UTC");
    let log_entry = format!("[{timestamp}] {event_type}: {details}\n");

    let mut file = OpenOptions::new().create(true).append(true).open(log_file)?;
    file.write_all(log_entry.as_bytes())?;

    Ok(())
}

/// Log with error handling (doesn't propagate errors)
pub fn log_safely(event_type: &str, details: &str) {
    if let Err(e) = log_to_file(event_type, details) {
        eprintln!("Failed to log: {}", e);
    }
}

/// Create a formatted log message
#[macro_export]
macro_rules! log_event {
    ($event_type:expr, $($arg:tt)*) => {
        $crate::utils::logging::log_safely($event_type, &format!($($arg)*))
    };
}
