//! Integration tests for the shell core.
//!
//! Two layers: a fixture package built in a temp dir (deterministic,
//! covers the tweaks manifest contract), and the repo's real compiled
//! `nougenai-brand` package (the data the scaffold actually ships against).

use nougendesign_shell_core::{list_variants, load_package, load_snapshot, load_tweaks};
use std::fs;
use std::path::PathBuf;

fn real_package_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("designs")
        .join("nougenai-brand")
}

#[test]
fn real_package_loads() {
    let dir = real_package_dir();
    let info = load_package(&dir).expect("real package loads");
    assert_eq!(info.name, "nougenai-brand");
    assert_eq!(info.dialect, "nougendesigns/v0");
    assert!(!info.description.is_empty());
    assert!(info.token_count > 0, "package declares tokens");
    assert!(
        info.themes.contains(&"dark".to_string()) && info.themes.contains(&"light".to_string()),
        "package declares dark+light themes, got {:?}",
        info.themes
    );
}

#[test]
fn real_variants_are_inert_candidates() {
    let dir = real_package_dir();
    let plans = list_variants(&dir).expect("variants list");
    // Four plans landed with PR #16; the tweaks slice (PR #17) settles
    // exploration into additional candidate plans, so assert the floor.
    assert!(plans.len() >= 4, "at least the four PR #16 plans, got {}", plans.len());
    for plan in &plans {
        assert_eq!(plan.status, "candidate", "{} stays a candidate", plan.id);
        assert!(plan.mutation_count > 0);
        assert!(!plan.lock_effect.is_empty(), "{} states its lock effect", plan.id);
    }
    let ids: Vec<&str> = plans.iter().map(|p| p.id.as_str()).collect();
    assert!(ids.contains(&"boards-stale-quiet"));
}

#[test]
fn fixture_package_with_tweaks_loads_five_dimensions() {
    let root = std::env::temp_dir().join(format!(
        "nougendesign-shell-core-test-{}",
        std::process::id()
    ));
    let pkg = root.join("designs").join("fixture-brand");
    fs::create_dir_all(pkg.join("tweaks")).unwrap();
    fs::create_dir_all(pkg.join("variants")).unwrap();
    fs::write(
        pkg.join("design.json"),
        r##"{"name":"fixture-brand","dialect":"nougendesigns/v0","version":"0",
            "description":"fixture","themes":{"dark":{},"light":{}},
            "tokens":{"--brand":"#73fd7c","--accent":"#d4af37"}}"##,
    )
    .unwrap();
    fs::write(
        pkg.join("manifest.json"),
        r#"{"name":"fixture-brand","description":"fixture package"}"#,
    )
    .unwrap();
    fs::write(
        pkg.join("tweaks").join("manifest.json"),
        r#"{"dialect":"tweaks/v1","manifest":"boards-exploration",
            "package":"fixture-brand","surface":"fleet-boards","status":"candidate",
            "summary":"bounded exploration",
            "dimensions":[
              {"id":"theme","label":"Colour theme","kind":"theme","default":"base","values":["base","light"]},
              {"id":"density","label":"Board density","kind":"token-step","default":"--cluster-gap","steps":["--space-4","--cluster-gap","--space-6"]}
            ]}"#,
    )
    .unwrap();
    fs::write(
        pkg.join("variants").join("boards-stale-quiet.json"),
        r#"{"variant":"boards-stale-quiet","package":"fixture-brand","surface":"fleet-boards",
            "status":"candidate","summary":"quiet stale rows","lock_effect":"red means blocked",
            "mutations":[{"selector":".board-row.is-stale"}]}"#,
    )
    .unwrap();

    let snapshot = load_snapshot(&pkg).expect("fixture snapshot loads");
    assert_eq!(snapshot.package.token_count, 2);
    let tweaks = snapshot.tweaks.expect("tweaks manifest present");
    assert_eq!(tweaks.dimensions.len(), 2);
    assert_eq!(tweaks.dimensions[0].id, "theme");
    assert_eq!(tweaks.dimensions[0].option_count, 2);
    assert_eq!(tweaks.dimensions[1].option_count, 3, "steps count as options");
    assert_eq!(snapshot.variants.len(), 1);
    assert!(snapshot.verify.gate_of_record.contains("visual_verify"));

    fs::remove_dir_all(&root).ok();
}

#[test]
fn package_without_tweaks_or_variants_still_loads() {
    let root = std::env::temp_dir().join(format!(
        "nougendesign-shell-core-bare-{}",
        std::process::id()
    ));
    fs::create_dir_all(&root).unwrap();
    fs::write(
        root.join("design.json"),
        r#"{"name":"bare","dialect":"nougendesigns/v0","themes":{},"tokens":{}}"#,
    )
    .unwrap();
    fs::write(root.join("manifest.json"), r#"{"description":"bare"}"#).unwrap();

    let tweaks = load_tweaks(&root).expect("missing tweaks is not an error");
    assert!(tweaks.is_none());
    let plans = list_variants(&root).expect("missing variants is not an error");
    assert!(plans.is_empty());

    fs::remove_dir_all(&root).ok();
}

#[test]
fn missing_package_is_an_error_not_a_panic() {
    let dir = PathBuf::from("/nonexistent/designs/nougenai-brand");
    let err = load_package(&dir).expect_err("missing package errors");
    assert!(err.to_string().contains("missing"), "got: {err}");
}
