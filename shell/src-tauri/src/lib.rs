//! The nougendesign shell — Tauri (Rust), per ADR 0001.
//!
//! The shell stays a shell: it loads a compiled package through
//! `nougendesign-shell-core`, shows one rendered surface, lists the
//! tweaks manifest's dimensions and the stored variant plans, and points
//! verify at the headless reference gate. It has no apply command, no
//! package writes, and no design state of its own.

use nougendesign_shell_core::{
    load_snapshot, resolve_package_dir, Snapshot, DEFAULT_PACKAGE,
};

/// Load the full snapshot for the wired package. Read-only.
#[tauri::command]
fn load_package() -> Result<Snapshot, String> {
    let dir = resolve_package_dir(DEFAULT_PACKAGE).map_err(|e| e.to_string())?;
    load_snapshot(&dir).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![load_package])
        .run(tauri::generate_context!())
        .expect("error while running the nougendesign shell");
}
