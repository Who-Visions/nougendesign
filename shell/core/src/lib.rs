//! Read-only loading of compiled nougendesign packages for the shell.
//!
//! The shell's ruled contract (ADR 0001): load package -> render surface ->
//! explore tweaks -> lock variants -> run verify. This crate implements the
//! *reading* half of that contract. It never writes to a package directory:
//! packages are compiled outputs whose sources live in the shards, and the
//! shell holds no design state of its own.
//!
//! Everything here is plain filesystem + JSON so the logic is testable
//! without a webview, a display, or Tauri itself.

use serde::Serialize;
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

/// The one package the scaffold is wired to. The shell reads compiled
/// packages from the repo's `designs/` tree; it never edits them.
pub const DEFAULT_PACKAGE: &str = "nougenai-brand";

#[derive(Debug)]
pub enum ShellError {
    /// A file the package contract requires is not there.
    Missing(PathBuf),
    Io {
        path: PathBuf,
        source: std::io::Error,
    },
    Json {
        path: PathBuf,
        source: serde_json::Error,
    },
}

impl fmt::Display for ShellError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ShellError::Missing(p) => write!(f, "required package file missing: {}", p.display()),
            ShellError::Io { path, source } => {
                write!(f, "cannot read {}: {source}", path.display())
            }
            ShellError::Json { path, source } => {
                write!(f, "invalid JSON in {}: {source}", path.display())
            }
        }
    }
}

impl std::error::Error for ShellError {}

pub type Result<T> = std::result::Result<T, ShellError>;

fn read_json(path: &Path) -> Result<serde_json::Value> {
    if !path.exists() {
        return Err(ShellError::Missing(path.to_path_buf()));
    }
    let text = fs::read_to_string(path).map_err(|source| ShellError::Io {
        path: path.to_path_buf(),
        source,
    })?;
    serde_json::from_str(&text).map_err(|source| ShellError::Json {
        path: path.to_path_buf(),
        source,
    })
}

fn str_field(value: &serde_json::Value, key: &str) -> String {
    value
        .get(key)
        .and_then(|v| v.as_str())
        .unwrap_or_default()
        .to_string()
}

/// Summary of a compiled design package (`design.json` + `manifest.json`).
#[derive(Debug, Clone, Serialize)]
pub struct PackageInfo {
    pub name: String,
    pub description: String,
    pub dialect: String,
    pub version: String,
    /// Theme names declared by the package (e.g. `dark`, `light`).
    pub themes: Vec<String>,
    /// Number of design tokens the package declares.
    pub token_count: usize,
    /// Package directory the data was read from (display only).
    pub source_dir: String,
}

/// One dimension of a tweaks manifest (`tweaks/manifest.json`, dialect
/// `tweaks/v1`): a bounded exploration axis. Exploring a dimension changes
/// nothing on disk; settling produces a candidate variant plan.
#[derive(Debug, Clone, Serialize)]
pub struct TweakDimension {
    pub id: String,
    pub label: String,
    pub kind: String,
    /// The dimension's default, rendered as text (defaults may be strings
    /// or token names in the manifest).
    pub default: String,
    /// How many values/steps the dimension is bounded to.
    pub option_count: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct TweaksInfo {
    pub manifest: String,
    pub dialect: String,
    pub surface: String,
    pub status: String,
    pub summary: String,
    pub dimensions: Vec<TweakDimension>,
}

/// A stored variant plan (`variants/<id>.json`). Plans are inert
/// candidates: the shell lists them; only Dave's lock applies one, and
/// applying happens through the reviewed-spec flow, never from the shell.
#[derive(Debug, Clone, Serialize)]
pub struct VariantPlan {
    pub id: String,
    pub surface: String,
    pub status: String,
    pub summary: String,
    pub lock_effect: String,
    pub mutation_count: usize,
}

/// Everything the shell's frontend needs for one package, in one snapshot.
#[derive(Debug, Clone, Serialize)]
pub struct Snapshot {
    pub package: PackageInfo,
    /// `None` when the package carries no tweaks manifest yet.
    pub tweaks: Option<TweaksInfo>,
    pub variants: Vec<VariantPlan>,
    pub verify: VerifyInfo,
}

/// The verify panel's content. Per ADR 0001 the gate of record is the
/// headless reference renderer (`tools/visual_verify.py`), never the
/// shell's own webview render.
#[derive(Debug, Clone, Serialize)]
pub struct VerifyInfo {
    pub gate_of_record: String,
    pub command: String,
    pub note: String,
}

impl VerifyInfo {
    pub fn standard() -> Self {
        VerifyInfo {
            gate_of_record: "headless reference renderer (tools/visual_verify.py)".to_string(),
            command: "python3 tools/visual_verify.py --package designs/nougenai-brand \
                      --html <surface.html> --out <findings-dir> \
                      --screenshot-cmd \"weasyprint {html} {png}\""
                .to_string(),
            note: "The shell's webview render is advisory (OS webviews differ per platform). \
                   A variant is locked against the package and judged by the reference gate, \
                   so webview variance can never change what passes."
                .to_string(),
        }
    }
}

/// Load the compiled package summary from a package directory.
pub fn load_package(package_dir: &Path) -> Result<PackageInfo> {
    let design = read_json(&package_dir.join("design.json"))?;
    let manifest = read_json(&package_dir.join("manifest.json"))?;

    let mut themes: Vec<String> = design
        .get("themes")
        .and_then(|t| t.as_object())
        .map(|obj| obj.keys().cloned().collect())
        .unwrap_or_default();
    themes.sort();

    let token_count = design
        .get("tokens")
        .and_then(|t| t.as_object())
        .map(|obj| obj.len())
        .unwrap_or(0);

    Ok(PackageInfo {
        name: str_field(&design, "name"),
        description: {
            let d = str_field(&manifest, "description");
            if d.is_empty() {
                str_field(&design, "description")
            } else {
                d
            }
        },
        dialect: str_field(&design, "dialect"),
        version: str_field(&design, "version"),
        themes,
        token_count,
        source_dir: package_dir.display().to_string(),
    })
}

/// Load the tweaks manifest, if the package carries one.
pub fn load_tweaks(package_dir: &Path) -> Result<Option<TweaksInfo>> {
    let path = package_dir.join("tweaks").join("manifest.json");
    if !path.exists() {
        return Ok(None);
    }
    let value = read_json(&path)?;

    let dimensions = value
        .get("dimensions")
        .and_then(|d| d.as_array())
        .map(|dims| {
            dims.iter()
                .map(|dim| {
                    let default = match dim.get("default") {
                        Some(serde_json::Value::String(s)) => s.clone(),
                        Some(other) => other.to_string(),
                        None => String::new(),
                    };
                    let option_count = ["values", "steps"]
                        .iter()
                        .filter_map(|k| dim.get(k).and_then(|v| v.as_array()).map(|a| a.len()))
                        .next()
                        .unwrap_or(0);
                    TweakDimension {
                        id: str_field(dim, "id"),
                        label: str_field(dim, "label"),
                        kind: str_field(dim, "kind"),
                        default,
                        option_count,
                    }
                })
                .collect()
        })
        .unwrap_or_default();

    Ok(Some(TweaksInfo {
        manifest: str_field(&value, "manifest"),
        dialect: str_field(&value, "dialect"),
        surface: str_field(&value, "surface"),
        status: str_field(&value, "status"),
        summary: str_field(&value, "summary"),
        dimensions,
    }))
}

/// List the stored variant plans in a package, sorted by id.
pub fn list_variants(package_dir: &Path) -> Result<Vec<VariantPlan>> {
    let dir = package_dir.join("variants");
    if !dir.exists() {
        return Ok(Vec::new());
    }
    let mut plans = Vec::new();
    let entries = fs::read_dir(&dir).map_err(|source| ShellError::Io {
        path: dir.clone(),
        source,
    })?;
    for entry in entries {
        let entry = entry.map_err(|source| ShellError::Io {
            path: dir.clone(),
            source,
        })?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("json") {
            continue;
        }
        let value = read_json(&path)?;
        plans.push(VariantPlan {
            id: str_field(&value, "variant"),
            surface: str_field(&value, "surface"),
            status: str_field(&value, "status"),
            summary: str_field(&value, "summary"),
            lock_effect: str_field(&value, "lock_effect"),
            mutation_count: value
                .get("mutations")
                .and_then(|m| m.as_array())
                .map(|a| a.len())
                .unwrap_or(0),
        });
    }
    plans.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(plans)
}

/// Load everything the shell shows for one package.
pub fn load_snapshot(package_dir: &Path) -> Result<Snapshot> {
    Ok(Snapshot {
        package: load_package(package_dir)?,
        tweaks: load_tweaks(package_dir)?,
        variants: list_variants(package_dir)?,
        verify: VerifyInfo::standard(),
    })
}

/// Resolve the package directory: explicit override first
/// (`NOUGENDESIGN_PACKAGE_DIR`), then walk up from the current directory
/// and from the executable looking for `designs/<package>`.
pub fn resolve_package_dir(package: &str) -> Result<PathBuf> {
    if let Ok(dir) = std::env::var("NOUGENDESIGN_PACKAGE_DIR") {
        let path = PathBuf::from(dir);
        if path.join("design.json").exists() {
            return Ok(path);
        }
    }
    let mut starts: Vec<PathBuf> = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        starts.push(cwd);
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            starts.push(parent.to_path_buf());
        }
    }
    for start in &starts {
        let mut dir: Option<&Path> = Some(start.as_path());
        while let Some(d) = dir {
            let candidate = d.join("designs").join(package);
            if candidate.join("design.json").exists() {
                return Ok(candidate);
            }
            // Also allow running from inside shell/ or a package-adjacent dir.
            let direct = d.join(package);
            if direct.join("design.json").exists() && d.ends_with("designs") {
                return Ok(direct);
            }
            dir = d.parent();
        }
    }
    Err(ShellError::Missing(
        PathBuf::from(format!("designs/{package}"))
            .join("design.json"),
    ))
}
