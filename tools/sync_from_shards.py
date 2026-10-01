"""One-way sync: Who-Visions/NouGenShards (source of truth) -> this repo.

NouGenShards CI and the workbench consume designs/ there, so edits land there
first and are copied here. Compares ignoring line endings.

    python tools/sync_from_shards.py <path-to-NouGenShards-checkout>          # copy
    python tools/sync_from_shards.py <path-to-NouGenShards-checkout> --check  # exit 1 on drift
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PATHS = [
    "designs", "tools/nougendesigns.py", "tools/nougendesign_discover.py",
    "tests/test_nougendesigns.py", "tests/test_design_discovery.py",
    "ui/src/styles.css", ".github/workflows/nougendesigns.yml", "DESIGN.md",
]


def files(root: Path, rel: str):
    base = root / rel
    if base.is_file():
        yield rel
    elif base.is_dir():
        for p in sorted(base.rglob("*")):
            if p.is_file():
                yield p.relative_to(root).as_posix()


def same(a: Path, b: Path) -> bool:
    return b.is_file() and a.read_bytes().replace(b"\r\n", b"\n") == b.read_bytes().replace(b"\r\n", b"\n")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    src = Path(args[0]).resolve()
    if not (src / "tools" / "nougendesigns.py").is_file():
        print(f"not a NouGenShards checkout: {src}")
        return 2
    check = "--check" in argv
    drift = []
    for rel in PATHS:
        wanted = set(files(src, rel))
        for name in sorted(wanted):
            if not same(src / name, HERE / name):
                drift.append(("update", name))
                if not check:
                    (HERE / name).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src / name, HERE / name)
        for name in files(HERE, rel):
            if name not in wanted:
                drift.append(("remove", name))
                if not check:
                    (HERE / name).unlink()
    for action, name in drift:
        print(f"{action}: {name}")
    print(f"{len(drift)} difference(s)" + (" (check only)" if check else " applied"))
    return 1 if (check and drift) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
