import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { repoDir, repoPython, meshFile, nougenHome } from "../src/mesh.js";
import { keymakerCommand } from "../src/keymaker.js";

const VARS = ["NOUGEN_ROOT", "NOUGEN_MESH_FILE", "NOUGEN_SHARDS_DIR", "NOUGEN_REPOS_DIR", "PYTHONPATH"];
let saved: Record<string, string | undefined> = {};
let tmp = "";

beforeEach(() => {
  saved = Object.fromEntries(VARS.map((v) => [v, process.env[v]]));
  for (const v of VARS) delete process.env[v];
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "nougen-mesh-"));
  process.env.NOUGEN_ROOT = path.join(tmp, "home");
});

afterEach(() => {
  for (const v of VARS) {
    if (saved[v] === undefined) delete process.env[v];
    else process.env[v] = saved[v];
  }
  fs.rmSync(tmp, { recursive: true, force: true });
});

function fakeRepo(root: string, name: string, venv = false): string {
  const d = path.join(root, name);
  fs.mkdirSync(path.join(d, ".git"), { recursive: true });
  fs.mkdirSync(path.join(d, "src"), { recursive: true });
  if (venv) {
    fs.mkdirSync(path.join(d, ".venv", "bin"), { recursive: true });
    fs.writeFileSync(path.join(d, ".venv", "bin", "python3"), "");
  }
  return d;
}

describe("mesh: NouGenShards checkout resolves at runtime", () => {
  it("home and mesh file follow NOUGEN_ROOT and NOUGEN_MESH_FILE", () => {
    expect(nougenHome()).toBe(path.join(tmp, "home"));
    expect(meshFile()).toBe(path.join(tmp, "home", "mesh.json"));
    process.env.NOUGEN_MESH_FILE = path.join(tmp, "other.json");
    expect(meshFile()).toBe(path.join(tmp, "other.json"));
  });

  it("NOUGEN_SHARDS_DIR wins", () => {
    const shards = fakeRepo(tmp, "anywhere", true);
    process.env.NOUGEN_SHARDS_DIR = shards;
    expect(repoDir("shards", path.join(tmp, "nowhere"))).toBe(shards);
    expect(repoPython(shards)).toBe(path.join(shards, ".venv", "bin", "python3"));
  });

  it("then mesh.json repos.shards, as a path or {path}", () => {
    const shards = fakeRepo(tmp, "elsewhere");
    fs.mkdirSync(path.join(tmp, "home"), { recursive: true });
    fs.writeFileSync(meshFile(), JSON.stringify({ repos: { shards } }));
    expect(repoDir("shards", path.join(tmp, "nowhere"))).toBe(shards);
    fs.writeFileSync(meshFile(), JSON.stringify({ repos: { shards: { path: shards } } }));
    expect(repoDir("shards", path.join(tmp, "nowhere"))).toBe(shards);
  });

  it("then a sibling checkout, matched case-insensitively", () => {
    const root = path.join(tmp, "repos");
    const design = fakeRepo(root, "nougendesign");
    fs.mkdirSync(path.join(design, "stitch", "src"), { recursive: true });
    const shards = fakeRepo(root, "nougenshards");
    expect(repoDir("shards", path.join(design, "stitch", "src", "keymaker.ts"))).toBe(shards);
  });

  it("a fresh box finds nothing and falls back to python3 on PATH", () => {
    const lone = fakeRepo(path.join(tmp, "solo"), "nougendesign");
    expect(repoDir("shards", path.join(lone, "stitch"))).toBeNull();
    expect(repoPython(null)).toMatch(/^python3?$/);
    expect(repoDir("not-a-repo", lone)).toBeNull();
  });

  it("keymaker runs the found checkout's interpreter with its src importable", () => {
    const shards = fakeRepo(tmp, "NouGenShards", true);
    process.env.NOUGEN_SHARDS_DIR = shards;
    const cmd = keymakerCommand();
    expect(cmd.shardsDir).toBe(shards);
    expect(cmd.python).toBe(path.join(shards, ".venv", "bin", "python3"));
    expect(String(cmd.env.PYTHONPATH).split(path.delimiter)[0]).toBe(path.join(shards, "src"));
  });
});

describe("no owner paths in the Stitch runtime", () => {
  const owner = /The Observatory|Watchtower|Outpost|kushboygroup|C:\\\\Users\\\\super|nougenai\.com|\bblade\b|\bphoebus\b|\bwhoart\b/i;
  for (const f of ["keymaker.ts", "mesh.ts", "stitch.ts", "cli.ts"]) {
    it(f, () => {
      const text = fs.readFileSync(path.join(__dirname, "..", "src", f), "utf8");
      expect(owner.test(text)).toBe(false);
    });
  }
});
