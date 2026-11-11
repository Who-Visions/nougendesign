import { describe, expect, it } from "bun:test";
import { getStitch, getStitchToolClient, ensureStitchAuthenticated } from "../src/stitch.js";
import { getStitchApiKey } from "../src/keymaker.js";

describe("NouGen Stitch SDK Integration", () => {
  it("resolves the Stitch API key from Keymaker vault", () => {
    const key = getStitchApiKey();
    expect(key).toBeDefined();
    expect(key.length).toBeGreaterThan(20);
    expect(key.startsWith("AQ.")).toBe(true);
  });

  it("authenticates and configures the Stitch SDK singleton", () => {
    const key = ensureStitchAuthenticated();
    expect(key).toBeDefined();
    const stitch = getStitch();
    expect(stitch).toBeDefined();
    expect(stitch.toolMap).toBeDefined();
  });

  it("exposes pre-parsed MCP tool schemas via stitch.toolMap", () => {
    const stitch = getStitch();
    const generateTool = stitch.toolMap.get("generate_screen_from_text");
    expect(generateTool).toBeDefined();
    expect(generateTool?.params.some((p) => p.name === "projectId")).toBe(true);
    expect(generateTool?.params.some((p) => p.name === "prompt")).toBe(true);

    const getScreenTool = stitch.toolMap.get("get_screen");
    expect(getScreenTool).toBeDefined();
    expect(getScreenTool?.params.some((p) => p.name === "name")).toBe(true);
  });

  it("connects and lists projects via StitchToolClient", async () => {
    const client = getStitchToolClient();
    const { tools } = await client.listTools();
    expect(tools.length).toBeGreaterThan(0);
    expect(tools.some((t) => t.name === "list_projects")).toBe(true);
    expect(tools.some((t) => t.name === "get_screen")).toBe(true);
    await client.close();
  });
});
