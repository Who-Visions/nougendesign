import { execSync } from "node:child_process";

let cachedKey: string | null = null;

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
    const pythonBin = "/Users/kushboygroup/The Observatory/NouGen/nougenshards/.venv/bin/python3";
    const code = "from nougen_shards.keymaker import get_secret; print(get_secret('STITCH_API_KEY') or '')";
    const res = execSync(`"${pythonBin}" -c "${code}"`, {
      encoding: "utf8",
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

  throw new Error("STITCH_API_KEY could not be resolved from Keymaker or environment.");
}
