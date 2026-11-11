import { getStitchApiKey } from "./keymaker.js";
import { stitch, Stitch, StitchToolClient } from "@google/stitch-sdk";

let initialized = false;

interface RetryOptions {
  maxRetries?: number;
  initialDelayMs?: number;
}

/**
 * Fetch wrapper with exponential backoff on HTTP 429 / 503 errors.
 */
export async function fetchWithRetry(
  input: string | URL | Request,
  init?: RequestInit,
  options: RetryOptions = {}
): Promise<Response> {
  const maxRetries = options.maxRetries ?? 3;
  let delay = options.initialDelayMs ?? 1000;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(input as any, init);
      if (response.status === 429 || response.status === 503) {
        if (attempt < maxRetries) {
          const retryAfter = response.headers.get("retry-after");
          const waitTime = retryAfter ? parseInt(retryAfter, 10) * 1000 : delay;
          await new Promise((resolve) => setTimeout(resolve, waitTime));
          delay *= 2;
          continue;
        }
      }
      return response;
    } catch (err: any) {
      if (attempt < maxRetries && (err?.name === "TimeoutError" || err?.code === "ECONNRESET")) {
        await new Promise((resolve) => setTimeout(resolve, delay));
        delay *= 2;
        continue;
      }
      throw err;
    }
  }

  throw new Error(`Request failed after ${maxRetries} retries.`);
}

/**
 * Ensures global fetch intercepts requests to stitch.googleapis.com
 * and dynamically injects the X-Goog-Api-Key header.
 */
export function ensureStitchAuthenticated(): string {
  const key = getStitchApiKey();

  if (!initialized) {
    const origFetch = globalThis.fetch;
    globalThis.fetch = ((input: string | URL | Request, init?: RequestInit) => {
      const urlStr =
        input instanceof URL
          ? input.toString()
          : typeof input === "string"
            ? input
            : (input as Request)?.url || String(input);

      if (urlStr.includes("stitch.googleapis.com")) {
        const incomingHeaders =
          init?.headers ||
          (input && typeof input === "object" && "headers" in input
            ? (input as Request).headers
            : undefined);

        const headers = new Headers(incomingHeaders);
        if (!headers.has("X-Goog-Api-Key")) {
          headers.set("X-Goog-Api-Key", key);
        }
        return origFetch(input as any, { ...init, headers });
      }

      return origFetch(input as any, init);
    }) as typeof fetch;

    initialized = true;
  }

  return key;
}

export function getStitch() {
  ensureStitchAuthenticated();
  return stitch;
}

export function getStitchToolClient(options?: { timeout?: number }) {
  const apiKey = ensureStitchAuthenticated();
  return new StitchToolClient({
    apiKey,
    baseUrl: "https://stitch.googleapis.com/mcp",
    timeout: options?.timeout ?? 300_000,
  });
}

export { stitch, Stitch, StitchToolClient };
