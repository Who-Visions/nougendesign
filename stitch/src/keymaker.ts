import { execFileSync } from "node:child_process";
import * as path from "node:path";
import { repoDir, repoPython } from "./mesh.js";

let cachedKey: string | null = null;

/**
 * How to run NouGenShards' Keymaker on this box: the NouGenShards checkout
 * the mesh finds (NOUGEN_SHARDS_DIR, mesh.json repos.shards, or a sibling
 * checkout), its .venv python if it has one, else python3 on PATH. With no
 * checkout found, python3 on PATH is tried as-is (nougen_shards installed).
 */
export function keymakerCommand(): { python: string; env: NodeJS.ProcessEnv; shardsDir: string | null } {
  const shardsDir = repoDir("shards");
  const childEnv: NodeJS.ProcessEnv = { ...process.env };
  if (shardsDir) {
    const src = path.join(shardsDir, "src");
    childEnv.PYTHONPATH = [src, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter);
  }
  return { python: repoPython(shardsDir), env: childEnv, shardsDir };
}

/**
 * Dynamically resolves the Google Stitch API Key from Keymaker vault
 * without ever printing or leaking the raw token into shell arguments or transcripts.
 */
export function getStitchApiKey(): string {
  if (cachedKey) return cachedKey;
  if (process.env.STITCH_API_KEY && process.env.STITCH_API_KEY.trim().length > 0) {
    cachedKey = process.env.STITCH_API_KEY.trim();
    return cachedKey;
  }

  try {
    const { python, env } = keymakerCommand();
    const code = "from nougen_shards.keymaker import get_secret; print(get_secret('STITCH_API_KEY') or '')";
    const res = execFileSync(python, ["-c", code], {
      encoding: "utf8",
      env,
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();

    if (res && res.length > 0) {
      cachedKey = res;
      process.env.STITCH_API_KEY = res;
      return cachedKey;
    }
  } catch (err) {
    // Keymaker lookup error handled gracefully
  }

  throw new Error(
    "STITCH_API_KEY could not be resolved from Keymaker or environment. " +
      "Set STITCH_API_KEY, or point NOUGEN_SHARDS_DIR (or mesh.json repos.shards) at a NouGenShards checkout.",
  );
}
