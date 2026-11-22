"""nougendesign in the NouGen mesh: own identity, no owner paths, a loadable manifest."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import nougen_mesh
import sync_from_shards

ROOT = Path(__file__).resolve().parents[1]
MESH_ENV = ("NOUGEN_ROOT", "NOUGEN_MESH_FILE", "NOUGEN_MACHINE", "NOUGEN_AGENT", "NOUGEN_FLEET_NODE",
            "NOUGEN_NODE_NAME", "NOUGEN_TENANT", "NOUGEN_FLEET_HOSTS_FILE", "NOUGEN_ENDPOINTS_FILE",
            "NOUGEN_INGRESS_URL", "NOUGEN_SHARDS_DIR", "NOUGEN_DESIGN_DIR", "NOUGEN_REPOS_DIR")


@pytest.fixture
def fresh_box(monkeypatch, tmp_path):
    for var in MESH_ENV:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("NOUGEN_ROOT", str(tmp_path / "home"))
    monkeypatch.setattr(nougen_mesh, "_git_config", lambda key: "")
    monkeypatch.setattr(nougen_mesh, "_hostname", lambda: "tester-laptop")
    return tmp_path


def test_fresh_box_is_standalone_with_its_own_name(fresh_box):
    ident = nougen_mesh.identity()
    assert ident == {"machine": "tester-laptop", "agent": "unknown-agent", "node": "standalone", "tenant": None}
    assert nougen_mesh.nodes() == {} and nougen_mesh.ingress() is None
    assert nougen_mesh.endpoint("open", at="some-node") is None   # nothing remote without an ingress


def test_shards_checkout_resolves_through_the_mesh(fresh_box, monkeypatch):
    lone = fresh_box / "solo" / "nougendesign"
    (lone / ".git").mkdir(parents=True)
    assert nougen_mesh.repo_dir("shards", near=str(lone / "tools" / "x.py")) is None
    sib = fresh_box / "solo" / "NouGenShards"
    (sib / "tools").mkdir(parents=True)
    assert nougen_mesh.repo_dir("shards", near=str(lone / "tools" / "x.py")) == sib
    other = fresh_box / "pinned"
    other.mkdir()
    monkeypatch.setenv("NOUGEN_SHARDS_DIR", str(other))
    assert nougen_mesh.repo_dir("shards", near=str(lone)) == other


def test_sync_without_a_path_uses_the_mesh(fresh_box, monkeypatch, capsys):
    monkeypatch.setattr(nougen_mesh, "repo_dir", lambda name, near=None: None)
    assert sync_from_shards.main(["--check"]) == 2
    assert "NOUGEN_SHARDS_DIR" in capsys.readouterr().out
    shards = fresh_box / "shards"
    for rel in sync_from_shards.PATHS:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, shards / rel)
        elif src.is_file():
            (shards / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, shards / rel)
    monkeypatch.setattr(nougen_mesh, "repo_dir", lambda name, near=None: shards if name == "shards" else None)
    assert sync_from_shards.main(["--check"]) == 0


_OWNER = re.compile(r"(?i)The Observatory|Watchtower|Outpost|kushboygroup|C:\\\\Users\\\\super|/Users/super"
                    r"|nougenai\.com|\bblade\b|\bphoebus\b|\bwhoart\b|aiwithdav3")
RUNTIME = ["tools/nougendesigns.py", "tools/nougendesign_discover.py", "tools/nyx_morph.py", "tools/fold_solver.py",
           "tools/sync_from_shards.py", "tools/nougen_mesh.py", "stitch/src/keymaker.ts", "stitch/src/mesh.ts",
           "stitch/src/stitch.ts", "stitch/src/cli.ts", "nougen.tools.json"]


def test_runtime_names_no_owner_paths_or_hosts():
    for rel in RUNTIME:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert not _OWNER.search(text), (rel, _OWNER.search(text))


def test_vendored_mesh_matches_canonical_when_shards_is_here():
    shards = nougen_mesh.repo_dir("shards", near=__file__)
    canon = shards / "src" / "nougen_shards" / "mesh.py" if shards else None
    if canon is None or not canon.exists():
        pytest.skip("no NouGenShards checkout with the mesh module on this box")
    assert nougen_mesh.file_digest(str(ROOT / "tools" / "nougen_mesh.py")) == nougen_mesh.file_digest(str(canon))


def test_manifest_loads_and_its_cli_tools_point_at_real_files():
    data = nougen_mesh.manifest(ROOT)
    assert data["schema"] == nougen_mesh.MANIFEST_SCHEMA and data["repo"] == "design"
    names = {t["name"] for t in data["tools"]}
    assert {"lint", "check", "compile", "nyx_morph", "stitch_projects", "stitch_export"} <= names
    for t in data["tools"]:
        assert t["transport"] == "cli" and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", t["name"])
        assert (ROOT / t["argv"][1]).is_file(), t
        slots = {m.group(1) for a in t["argv"] for m in [re.fullmatch(r"\{(\w+)\??\}", a)] if m}
        assert slots == set(t["args"]["properties"]), t["name"]


def test_lint_runs_through_the_mesh(fresh_box, monkeypatch):
    monkeypatch.setenv("NOUGEN_DESIGN_DIR", str(ROOT))
    out = nougen_mesh.call("design.lint", {"spec": "designs/nougen-core/design.json"})
    assert out["passed"] is True
