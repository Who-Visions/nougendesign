//! Emit the shell frontend's data snapshot for a package as JSON.
//!
//! Usage: `shell-data [package_dir]`
//!
//! With no argument the package is resolved the same way the shell app
//! resolves it (see `resolve_package_dir`). The output is what the Tauri
//! commands return and what `ui/shell-data.json` bundles for the
//! standalone (no-Tauri) frontend mode.

use nougendesign_shell_core::{load_snapshot, resolve_package_dir, DEFAULT_PACKAGE};
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    let arg = std::env::args().nth(1);
    let dir = match arg {
        Some(p) => PathBuf::from(p),
        None => match resolve_package_dir(DEFAULT_PACKAGE) {
            Ok(d) => d,
            Err(e) => {
                eprintln!("shell-data: {e}");
                return ExitCode::FAILURE;
            }
        },
    };
    match load_snapshot(&dir) {
        Ok(snapshot) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&snapshot).expect("snapshot serializes")
            );
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("shell-data: {e}");
            ExitCode::FAILURE
        }
    }
}
