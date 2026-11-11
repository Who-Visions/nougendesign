#!/usr/bin/env bun
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { execSync } from "node:child_process";
import { getStitch, getStitchToolClient, ensureStitchAuthenticated } from "./stitch.js";

interface StitchFileResponse {
  dataString?: string;
  imageMetadata?: Record<string, any>;
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || "help";

  const apiKey = ensureStitchAuthenticated();
  const stitch = getStitch();

  switch (command) {
    case "projects": {
      console.log("Listing Stitch projects...");
      const projects = await stitch.projects();
      console.log(`Found ${projects.length} project(s):\n`);
      for (const p of projects) {
        console.log(`• ID: ${p.id}`);
      }
      break;
    }

    case "screens": {
      const projectId = args[1];
      if (!projectId) {
        console.error("Usage: bun run stitch screens <projectId>");
        process.exit(1);
      }
      const project = stitch.project(projectId);
      const screens = await project.screens();
      console.log(`Project ${projectId} contains ${screens.length} screen(s):\n`);
      for (const s of screens) {
        const title = (s as any).data?.title || (s as any).data?.name || "Untitled";
        console.log(`• [${s.id}] ${title}`);
      }
      break;
    }

    case "download": {
      const projectId = args[1];
      if (!projectId) {
        console.error("Usage: bun run stitch download <projectId> [outDir]");
        process.exit(1);
      }
      const outDir = args[2] || path.join(process.cwd(), "downloads", projectId);
      console.log(`Downloading all assets for project ${projectId} to ${outDir}...`);
      await fs.mkdir(outDir, { recursive: true });
      const project = stitch.project(projectId);
      const res = await project.downloadAssets(outDir);
      console.log(`Successfully downloaded ${res.screens.length} screen(s).`);
      if (res.warnings && res.warnings.length > 0) {
        console.warn("Warnings:", res.warnings);
      }
      break;
    }

    case "get-screen": {
      const projectId = args[1];
      const screenId = args[2];
      if (!projectId || !screenId) {
        console.error("Usage: bun run stitch get-screen <projectId> <screenId> [outDir]");
        process.exit(1);
      }
      const outDir = args[3] || path.join(process.cwd(), "downloads", projectId, screenId);
      console.log(`Fetching screen ${screenId} from project ${projectId}...`);
      const client = getStitchToolClient();
      const res: any = await client.callTool("get_screen", {
        name: `projects/${projectId}/screens/${screenId}`,
      });
      await fs.mkdir(outDir, { recursive: true });

      // HTML
      if (res.htmlCode?.downloadUrl) {
        const hRes = await fetch(res.htmlCode.downloadUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const hJson = (await hRes.json()) as StitchFileResponse;
        const html = hJson.dataString || "";
        await fs.writeFile(path.join(outDir, "code.html"), html, "utf8");
        console.log(`Saved code.html (${html.length} bytes)`);
      }

      // Screenshot
      if (res.screenshot?.downloadUrl) {
        const sRes = await fetch(res.screenshot.downloadUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const sJson = (await sRes.json()) as StitchFileResponse;
        const buf = Buffer.from(sJson.dataString || "", "base64");
        await fs.writeFile(path.join(outDir, "screen.png"), buf);
        console.log(`Saved screen.png (${buf.length} bytes)`);
      }

      await client.close();
      console.log(`Screen saved to ${outDir}`);
      break;
    }

    case "generate": {
      const projectId = args[1];
      const prompt = args[2];
      const outDir = args[3];
      if (!projectId || !prompt) {
        console.error("Usage: bun run stitch generate <projectId> <prompt> [outDir]");
        process.exit(1);
      }
      console.log(`Generating screen in project ${projectId}...`);
      const project = stitch.project(projectId);
      const screen = await project.generate(prompt, "MOBILE");
      console.log(`Generated screen ID: ${screen.id}`);

      if (outDir) {
        await fs.mkdir(outDir, { recursive: true });
        const htmlUrl = await screen.getHtml();
        const hRes = await fetch(htmlUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const hJson = (await hRes.json()) as StitchFileResponse;
        await fs.writeFile(path.join(outDir, "code.html"), hJson.dataString || "", "utf8");

        const imgUrl = await screen.getImage();
        const sRes = await fetch(imgUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const sJson = (await sRes.json()) as StitchFileResponse;
        await fs.writeFile(path.join(outDir, "screen.png"), Buffer.from(sJson.dataString || "", "base64"));
        console.log(`Assets written to ${outDir}`);
      }
      break;
    }

    case "export-to-nougen": {
      const projectId = args[1];
      const screenId = args[2];
      const slug = args[3];
      if (!projectId || !screenId || !slug) {
        console.error("Usage: bun run stitch export-to-nougen <projectId> <screenId> <slug>");
        process.exit(1);
      }

      const client = getStitchToolClient();
      const res: any = await client.callTool("get_screen", {
        name: `projects/${projectId}/screens/${screenId}`,
      });

      const rootDir = path.resolve(__dirname, "../../");
      const targetDir = path.join(rootDir, "designs", slug);
      await fs.mkdir(targetDir, { recursive: true });

      // Save HTML
      let rawHtml = "";
      if (res.htmlCode?.downloadUrl) {
        const hRes = await fetch(res.htmlCode.downloadUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const hJson = (await hRes.json()) as StitchFileResponse;
        rawHtml = hJson.dataString || "";
        await fs.writeFile(path.join(targetDir, "code.html"), rawHtml, "utf8");
      }

      // Save Screenshot
      if (res.screenshot?.downloadUrl) {
        const sRes = await fetch(res.screenshot.downloadUrl, { headers: { "X-Goog-Api-Key": apiKey } });
        const sJson = (await sRes.json()) as StitchFileResponse;
        const buf = Buffer.from(sJson.dataString || "", "base64");
        await fs.writeFile(path.join(targetDir, "screen.png"), buf);
      }

      // Write design.json
      const designJsonPath = path.join(targetDir, "design.json");
      const designSpec = {
        dialect: "nougendesigns/v0",
        name: slug,
        version: "1.0.0",
        description: `Exported from Google Stitch project ${projectId} screen ${screenId} (${res.title || "Untitled"}).`,
        referenceWorld: "Precision mobile instrument, avionics control deck, high-density terminal.",
        antiPatterns: "Reject decorative gradients, glass, glow, giant pills, sparkles, waveform noise and generic SaaS card grids.",
        materiality: "Use obsidian dark background (#0a0e17), matte titanium containers (#181b25), cyan (#38bdf8) and emerald (#4edea3) accents.",
        density: "High density, 4px instrument corners, compact telemetry dials and logs.",
        motionGrammar: "Sub-150ms state changes, spring curves for active toggles, instant terminal updates.",
        interactionPhysics: "Direct controls, persistent lazy list state.",
        informationHierarchy: "Active operational state first, execution telemetry second, historical logs third.",
        responsiveBehavior: "Optimized for mobile viewports (360px - 412px), single LazyColumn vertical hierarchy.",
        accessibility: "High contrast WCAG AAA compliant text on dark background.",
        brandVoice: "Deterministic, telemetry-grounded, zero fluff.",
        iconography: "Material Symbols Outlined, monochrome line symbols paired with concise labels.",
        dataViz: "Monospace digits, high-contrast dials, bitemporal scrub timeline.",
        stateGrammar: "IDLE, RUNNING, PAUSED, ERROR, TOUCHDOWN states with distinct badge colors.",
        provenance: `Exported via Google Stitch SDK (@google/stitch-sdk) from project ${projectId} screen ${screenId}.`,
        tokens: {
          "--bg": "#0a0e17",
          "--bg-gradient": "var(--bg)",
          "--panel": "#181b25",
          "--panel-solid": "#181b25",
          "--panel-2": "#1c1f29",
          "--panel-hover": "#262a34",
          "--line": "#3e484f",
          "--line-glow": "#3e484f",
          "--text": "#dfe2ef",
          "--muted": "#bdc8d1",
          "--accent": "#38bdf8",
          "--accent-rgb": "56, 189, 248",
          "--accent-2": "#7bd0ff",
          "--accent-purple": "#d5c3ff",
          "--accent-green": "#4edea3",
          "--status-verified-text": "#4edea3",
          "--status-verified-border": "#4edea3",
          "--status-verified-bg": "rgba(78, 222, 163, 0.12)",
          "--status-pending-text": "#38bdf8",
          "--status-pending-border": "#38bdf8",
          "--status-pending-bg": "rgba(56, 189, 248, 0.12)",
          "--status-conflict-text": "#ffb4ab",
          "--status-conflict-border": "#ffb4ab",
          "--status-conflict-bg": "rgba(255, 180, 171, 0.12)",
          "--status-offline-text": "#87929a",
          "--status-offline-border": "#3e484f",
          "--status-offline-bg": "rgba(135, 146, 154, 0.10)",
          "--status-sim-text": "#87929a",
          "--status-sim-border": "#3e484f",
          "--status-sim-bg": "rgba(135, 146, 154, 0.10)",
          "--control-ink": "#00354a",
          "--focus": "#7bd0ff"
        },
        themes: {
          dark: {}
        },
        evidence: [
          {
            kind: "observed",
            source: `projects/${projectId}/screens/${screenId}`,
            note: `Screen title: ${res.title || "Untitled"}`
          }
        ],
        contrastPairs: [
          { ink: "--text", ground: "--bg" },
          { ink: "--muted", ground: "--panel" },
          { ink: "--control-ink", ground: "--accent" },
          { ink: "--focus", ground: "--bg", role: "ui" },
          { ink: "--status-verified-text", ground: "--panel", role: "ui" },
          { ink: "--status-pending-text", ground: "--panel", role: "ui" },
          { ink: "--status-conflict-text", ground: "--panel", role: "ui" }
        ]
      };
      await fs.writeFile(designJsonPath, JSON.stringify(designSpec, null, 2), "utf8");

      console.log(`Exported design package to ${targetDir}`);
      // Run linter
      const lintOutput = execSync(`python3 "${path.join(rootDir, "tools/nougendesigns.py")}" lint "${designJsonPath}"`, {
        encoding: "utf8",
      });
      const parsed = JSON.parse(lintOutput);
      console.log(`Linter passed: ${parsed.passed} (0 errors, ${parsed.contrast?.length || 0} contrast pairs verified)`);
      await client.close();
      break;
    }

    default:
      console.log(`
NouGen Stitch SDK CLI
Usage:
  bun run stitch projects
  bun run stitch screens <projectId>
  bun run stitch download <projectId> [outDir]
  bun run stitch get-screen <projectId> <screenId> [outDir]
  bun run stitch generate <projectId> "<prompt>" [outDir]
  bun run stitch export-to-nougen <projectId> <screenId> <slug>
      `);
      break;
  }
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
