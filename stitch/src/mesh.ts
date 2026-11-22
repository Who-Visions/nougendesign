/**
 * Tiny NouGen mesh reader for the Stitch CLI.
 *
 * Same precedence as the Python mesh module (tools/nougen_mesh.py):
 * environment, then the mesh file (NOUGEN_MESH_FILE or <NOUGEN_ROOT>/mesh.json,
 * NOUGEN_ROOT defaulting to ~/.nougen), then what the box itself has (a
 * sibling checkout), then nothing. Nothing here names an operator, a machine
 * or a home path.
 */
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

function env(name: string): string {
  return (process.env[name] || "").trim();
}

function expand(p: string): string {
  return p.startsWith("~") ? path.join(os.homedir(), p.slice(1)) : p;
}

function isDir(p: string | null | undefined): p is string {
  if (!p) return false;
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function isFile(p: string): boolean {
  try {
    return fs.statSync(p).isFile();
  } catch {
    return false;
  }
}

/** Runtime home: $NOUGEN_ROOT, else ~/.nougen. */
export function nougenHome(): string {
  const raw = env("NOUGEN_ROOT");
  return raw ? expand(raw) : path.join(os.homedir(), ".nougen");
}

export function meshFile(): string {
  const raw = env("NOUGEN_MESH_FILE");
  return raw ? expand(raw) : path.join(nougenHome(), "mesh.json");
}

/** The mesh file as an object; {} when absent or unreadable. */
export function loadMesh(): Record<string, any> {
  try {
    const data = JSON.parse(fs.readFileSync(meshFile(), "utf8"));
    return data && typeof data === "object" && !Array.isArray(data) ? data : {};
  } catch {
    return {};
  }
}

/** GitHub repo names of the package, keyed by mesh short name. */
const REPOS: Record<string, string> = {
  shards: "NouGenShards",
  relay: "NouGenRelay",
  msg: "NouGenMsg",
  code: "NouGenCode",
  design: "nougendesign",
  tracker: "NouGenTracker",
  open: "NouGenOpen",
  "fleet-mcp": "nougen-fleet-mcp",
  claude: "NouGenClaude",
  portable: "NouGenPortable",
};

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

function repoTop(start: string): string | null {
  let cur = path.resolve(start);
  if (!isDir(cur)) cur = path.dirname(cur);
  for (;;) {
    if (fs.existsSync(path.join(cur, ".git")) || fs.existsSync(path.join(cur, "nougen.tools.json"))) return cur;
    const up = path.dirname(cur);
    if (up === cur) return null;
    cur = up;
  }
}

/**
 * Where repo `name` is checked out on this box, or null:
 * NOUGEN_<NAME>_DIR, then mesh "repos"[name] (a path or {path}), then a
 * sibling of the repo holding `near` whose name matches case-insensitively,
 * then a child of $NOUGEN_REPOS_DIR.
 */
export function repoDir(name: string, near: string = __dirname): string | null {
  const repo = REPOS[name];
  if (!repo) return null;
  const fromEnv = env(`NOUGEN_${name.toUpperCase().replace(/-/g, "_")}_DIR`);
  if (isDir(expand(fromEnv))) return expand(fromEnv);
  const repos = loadMesh().repos;
  let v: any = repos && typeof repos === "object" ? repos[name] : null;
  if (v && typeof v === "object") v = v.path;
  if (typeof v === "string" && isDir(expand(v))) return expand(v);
  const want = norm(repo);
  const roots: string[] = [];
  const top = repoTop(near);
  if (top) {
    if (norm(path.basename(top)) === want) return top;
    roots.push(path.dirname(top));
  }
  if (env("NOUGEN_REPOS_DIR")) roots.push(expand(env("NOUGEN_REPOS_DIR")));
  for (const root of roots) {
    let kids: string[] = [];
    try {
      kids = fs.readdirSync(root);
    } catch {
      continue;
    }
    for (const kid of kids) {
      const full = path.join(root, kid);
      if (norm(kid) === want && isDir(full)) return full;
    }
  }
  return null;
}

/** A repo's own interpreter (.venv) if it has one, else python3 on PATH. */
export function repoPython(dir: string | null): string {
  if (dir) {
    for (const rel of [".venv/bin/python3", ".venv/bin/python", ".venv/Scripts/python.exe", "venv/bin/python"]) {
      const p = path.join(dir, rel);
      if (isFile(p)) return p;
    }
  }
  return process.platform === "win32" ? "python" : "python3";
}
