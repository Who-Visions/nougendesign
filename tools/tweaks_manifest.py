#!/usr/bin/env python3
"""tweaks_manifest.py — bounded exploration spaces for design packages
(Claude Design reversal #2, Module 2: the tweaks panel, fleet-safe).

Claude Design's tweak panel lets you flip palette, accent, density
and card style at zero prompt cost — but turning tweaks off APPLIES
the result, with no undo (first course, Module 10: the challenge).
Slice 4 answered with stored candidate variant plans: discrete,
locked by Dave's word, never applied on close. This tool is the
other half: the *exploration space* itself, declared in the package.

A tweaks manifest states which dimensions a surface MAY vary, and
every dimension is bound to package material only — token names,
theme names, declared token ladders, or enumerated choices written
into the manifest. An off-brand value is inexpressible, not merely
discouraged: validation resolves every bound against the package's
design.json and goes red on anything that does not resolve. That is
why exploration is free: the space is pre-locked, so no point in it
can leave the brand.

Settling on values produces a Slice-4 candidate variant plan
(tools/variant_plans.py shape, status "candidate") via the `plan`
command. Nothing in this tool applies anything; there is
deliberately no apply command. A plan takes effect only when Dave
locks it, through the normal reviewed-spec flow.

Manifest file shape (JSON, dialect "tweaks/v1"):

  {
    "manifest": "boards-exploration",   // kebab-case id
    "dialect": "tweaks/v1",
    "status": "candidate",              // always "candidate"
    "package": "nougenai-brand",        // package it explores
    "surface": "fleet-boards",          // surface the space serves
    "summary": "One line: what this space is for.",
    "evidence": [{"kind": "observed|inferred|invented",
                  "note": "...", "source": "..."}],
    "dimensions": [ <dimension>, ... ]
  }

Dimension kinds (each carries id, label, default, and an effect
{selector, change}; change may use {value}, {token}, {resolved}):

  theme       values are theme names from the package ("base" or a
              key of design.json "themes"); {value} = theme name.
  token-enum  values are [{value, token}]; every token must exist
              in the package; {resolved} = the token's base value.
  token-step  a ladder over one token: "token" plus "steps", token
              names in the package whose values form a strictly
              monotonic ladder; the default step's value must equal
              the token's current value (the ladder passes through
              the locked default); {value} = step token name,
              {resolved} = its value.
  choice      values are [{value, change}]; each value carries its
              own mutation prose (card styles, treatments — the
              dimensions whose options are not tokens).

Commands:

  python3 tools/tweaks_manifest.py validate designs/nougenai-brand/tweaks
  python3 tools/tweaks_manifest.py index designs/nougenai-brand/tweaks
  python3 tools/tweaks_manifest.py plan designs/nougenai-brand/tweaks \
      --settings settings.json --variant boards-explored-quiet \
      --out designs/nougenai-brand/variants/boards-explored-quiet.json

`validate` takes a manifest file or the directory holding one
(manifest.json). `index` (re)writes INDEX.md beside the manifest —
generated, never hand-edited. `plan` writes a candidate variant
plan; settings is a JSON object {dimension_id: value}. Exit code 1
on any validation error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DIALECT = "tweaks/v1"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NUMERIC = re.compile(r"^(-?[0-9]*\.?[0-9]+)([a-z%]*)$")
KINDS = ("theme", "token-enum", "token-step", "choice")
EVIDENCE_KINDS = ("observed", "inferred", "invented")


# ---------------------------------------------------------------- loading

def load_json(path):
    return json.loads(Path(path).read_text())


def manifest_path(target):
    target = Path(target)
    if target.is_dir():
        return target / "manifest.json"
    return target


def package_spec(manifest_file, data):
    """design.json of the package the manifest names: a sibling of the
    manifest's directory (manifest lives in <package>/tweaks/)."""
    pkg_dir = Path(manifest_file).resolve().parent.parent
    spec_path = pkg_dir / "design.json"
    if not spec_path.exists():
        return None, f"{manifest_file}: no design.json found at {spec_path}"
    spec = load_json(spec_path)
    if spec.get("name") != data.get("package"):
        return None, (f"{manifest_file}: package '{data.get('package')}' does not "
                      f"match design.json name '{spec.get('name')}'")
    return spec, None


def all_tokens(spec):
    """Base tokens overlaid with every theme's overrides — a token
    named by a dimension may live in either."""
    tokens = dict(spec.get("tokens", {}))
    for overrides in spec.get("themes", {}).values():
        tokens.update(overrides)
    return tokens


def _num(value):
    m = NUMERIC.match(str(value).strip())
    if not m:
        return None
    return float(m.group(1)), m.group(2)


# ---------------------------------------------------------------- validate

def _check_effect(dim, where, errors):
    eff = dim.get("effect")
    if not isinstance(eff, dict) or not str(eff.get("selector", "")).strip() \
            or not str(eff.get("change", "")).strip():
        errors.append(f"{where}: dimension needs an effect with non-empty selector and change")
        return
    if "{value}" not in eff["change"] and "{resolved}" not in eff["change"] \
            and dim.get("kind") != "choice":
        errors.append(f"{where}: effect.change must reference {{value}} or {{resolved}} "
                      "so a setting can be rendered into a mutation")


def validate_dimension(dim, spec, where):
    errors = []
    if not isinstance(dim, dict):
        return [f"{where}: a dimension must be a JSON object"]
    did = dim.get("id", "?")
    where = f"{where} dimension '{did}'"
    if not KEBAB.match(str(dim.get("id", ""))):
        errors.append(f"{where}: id is not kebab-case")
    if not str(dim.get("label", "")).strip():
        errors.append(f"{where}: label must be non-empty")
    kind = dim.get("kind")
    if kind not in KINDS:
        errors.append(f"{where}: kind '{kind}' is not one of {', '.join(KINDS)}")
        return errors
    _check_effect(dim, where, errors)
    base = spec.get("tokens", {})
    tokens = all_tokens(spec)
    default = dim.get("default")

    if kind == "theme":
        allowed = {"base"} | set(spec.get("themes", {}))
        values = dim.get("values")
        if not isinstance(values, list) or not values:
            errors.append(f"{where}: theme dimension needs a non-empty values list")
        else:
            for v in values:
                if v not in allowed:
                    errors.append(f"{where}: theme '{v}' is not in the package "
                                  f"(allowed: {', '.join(sorted(allowed))})")
            if default not in values:
                errors.append(f"{where}: default '{default}' is not one of its values")

    elif kind == "token-enum":
        values = dim.get("values")
        if not isinstance(values, list) or not values:
            errors.append(f"{where}: token-enum dimension needs a non-empty values list")
        else:
            names = []
            for v in values:
                if not isinstance(v, dict) or not str(v.get("value", "")).strip() \
                        or not str(v.get("token", "")).strip():
                    errors.append(f"{where}: each value needs a non-empty value and token")
                    continue
                names.append(v["value"])
                if v["token"] not in tokens:
                    errors.append(f"{where}: token '{v['token']}' does not exist in the package")
            if default not in names:
                errors.append(f"{where}: default '{default}' is not one of its values")

    elif kind == "token-step":
        token = dim.get("token")
        steps = dim.get("steps")
        if token not in base:
            errors.append(f"{where}: token '{token}' does not exist in the package's base tokens")
        if not isinstance(steps, list) or len(steps) < 2:
            errors.append(f"{where}: token-step needs at least two steps")
            steps = []
        nums = []
        for s in steps:
            if s not in base:
                errors.append(f"{where}: step token '{s}' does not exist in the package")
                continue
            n = _num(base[s])
            if n is None:
                errors.append(f"{where}: step token '{s}' value '{base[s]}' is not numeric")
            else:
                nums.append((s, n))
        if len(nums) == len(steps) and len(nums) >= 2:
            units = {u for _, (_, u) in nums}
            vals = [v for _, (v, _) in nums]
            if len(units) > 1:
                errors.append(f"{where}: step values mix units ({', '.join(sorted(units))})")
            elif not (all(a < b for a, b in zip(vals, vals[1:]))
                      or all(a > b for a, b in zip(vals, vals[1:]))):
                errors.append(f"{where}: step values are not a strictly monotonic ladder")
        if default not in steps:
            errors.append(f"{where}: default '{default}' is not one of its steps")
        elif token in base and default in base and base[token] != base[default]:
            errors.append(f"{where}: default step '{default}' has value '{base[default]}' but "
                          f"the locked value of '{token}' is '{base[token]}' — the ladder "
                          "must pass through the package's current value")

    elif kind == "choice":
        values = dim.get("values")
        if not isinstance(values, list) or not values:
            errors.append(f"{where}: choice dimension needs a non-empty values list")
        else:
            names = []
            for v in values:
                if not isinstance(v, dict) or not str(v.get("value", "")).strip() \
                        or not str(v.get("change", "")).strip():
                    errors.append(f"{where}: each choice value needs a non-empty value and change")
                    continue
                names.append(v["value"])
            if default not in names:
                errors.append(f"{where}: default '{default}' is not one of its values")
    return errors


def validate_manifest(path):
    path = Path(path)
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        return [f"{path}: unreadable ({exc})"]
    if not isinstance(data, dict):
        return [f"{path}: a tweaks manifest must be a JSON object"]
    errors = []
    if not KEBAB.match(str(data.get("manifest", ""))):
        errors.append(f"{path}: manifest id '{data.get('manifest')}' is not kebab-case")
    if data.get("dialect") != DIALECT:
        errors.append(f"{path}: dialect must be '{DIALECT}'")
    if data.get("status") != "candidate":
        errors.append(f"{path}: status must be 'candidate' — a manifest declares an "
                      "exploration space; it never claims to be locked or applied")
    for key in ("package", "surface", "summary"):
        if not str(data.get(key, "")).strip():
            errors.append(f"{path}: missing or empty required key '{key}'")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{path}: evidence must be a non-empty list (repo rule: choices "
                      "are labeled observed / inferred / invented)")
    else:
        for i, e in enumerate(evidence):
            if not isinstance(e, dict) or e.get("kind") not in EVIDENCE_KINDS \
                    or not str(e.get("note", "")).strip():
                errors.append(f"{path}: evidence {i} needs a kind in "
                              f"{', '.join(EVIDENCE_KINDS)} and a non-empty note")
    spec, spec_err = package_spec(path, data)
    if spec_err:
        errors.append(spec_err)
        return errors
    dims = data.get("dimensions")
    if not isinstance(dims, list) or not dims:
        errors.append(f"{path}: dimensions must be a non-empty list")
        return errors
    seen = set()
    for dim in dims:
        if isinstance(dim, dict):
            if dim.get("id") in seen:
                errors.append(f"{path}: duplicate dimension id '{dim.get('id')}'")
            seen.add(dim.get("id"))
        errors += validate_dimension(dim, spec, str(path))
    return errors


# ---------------------------------------------------------------- plan

def allowed_values(dim, spec):
    kind = dim["kind"]
    if kind == "theme":
        return list(dim["values"])
    if kind == "token-step":
        return list(dim["steps"])
    return [v["value"] for v in dim["values"]]


def render_mutation(dim, value, spec):
    kind = dim["kind"]
    base = spec.get("tokens", {})
    if kind == "choice":
        change = next(v["change"] for v in dim["values"] if v["value"] == value)
        return {"selector": dim["effect"]["selector"], "change": change}
    if kind == "theme":
        token, resolved = "", value
    elif kind == "token-enum":
        entry = next(v for v in dim["values"] if v["value"] == value)
        token, resolved = entry["token"], all_tokens(spec)[entry["token"]]
    elif kind == "token-step":
        token, resolved = dim["token"], base[value]
        value_name = value
    change = dim["effect"]["change"]
    change = change.replace("{resolved}", str(resolved))
    change = change.replace("{token}", str(token))
    change = change.replace("{value}", str(value if kind != "token-step" else value_name))
    return {"selector": dim["effect"]["selector"], "change": change}


def build_plan(data, spec, settings, variant_id):
    """Settings {dimension_id: value} → a Slice-4 candidate variant plan.
    Raises ValueError on any setting outside the declared space."""
    dims = {d["id"]: d for d in data["dimensions"]}
    mutations = []
    chosen = []
    for dim_id, value in settings.items():
        if dim_id not in dims:
            raise ValueError(f"unknown dimension '{dim_id}' — the manifest declares: "
                             f"{', '.join(sorted(dims))}")
        dim = dims[dim_id]
        allowed = allowed_values(dim, spec)
        if value not in allowed:
            raise ValueError(f"dimension '{dim_id}': value '{value}' is outside the "
                             f"declared space (allowed: {', '.join(map(str, allowed))})")
        mutations.append(render_mutation(dim, value, spec))
        chosen.append(f"{dim_id} = {value}")
    if not mutations:
        raise ValueError("settings are empty — a plan needs at least one explored setting")
    return {
        "variant": variant_id,
        "status": "candidate",
        "package": data["package"],
        "surface": data["surface"],
        "summary": (f"Explored via tweaks manifest '{data['manifest']}': "
                    + "; ".join(chosen) + "."),
        "lock_effect": ("Locking makes the explored settings permanent on "
                        f"{data['surface']}: " + "; ".join(chosen) + ". Until then "
                        "nothing has changed — exploration never applies."),
        "mutations": mutations,
    }


# ---------------------------------------------------------------- index

def _bound_description(dim, spec):
    kind = dim["kind"]
    base = spec.get("tokens", {})
    if kind == "theme":
        return "package themes: " + ", ".join(dim["values"])
    if kind == "token-enum":
        return "package tokens: " + ", ".join(
            f"{v['value']} → {v['token']}" for v in dim["values"])
    if kind == "token-step":
        return (f"ladder over {dim['token']}: "
                + ", ".join(f"{s} ({base.get(s, '?')})" for s in dim["steps"]))
    return "enumerated choices: " + ", ".join(v["value"] for v in dim["values"])


def render_index(data, spec):
    lines = [
        f"# Tweaks manifest — {data['manifest']}",
        "",
        "Generated by `tools/tweaks_manifest.py index`. Do not hand-edit.",
        "",
        f"Package: `{data['package']}` · Surface: `{data['surface']}` "
        f"· Dialect: `{data['dialect']}` · Status: **candidate**",
        "",
        data["summary"],
        "",
        "This manifest declares the dimensions this surface MAY vary. "
        "Every bound resolves against the package's own tokens and "
        "themes — a value outside the brand is inexpressible here, "
        "which is what makes exploration free. Exploring changes "
        "nothing. Settling on values produces a candidate variant "
        "plan (see `tools/variant_plans.py`); a plan takes effect "
        "only when Dave locks it. Nothing applies on view, on "
        "close, or on refresh.",
        "",
        "| Dimension | Kind | Default | Bounds |",
        "|---|---|---|---|",
    ]
    for dim in data["dimensions"]:
        lines.append(f"| `{dim['id']}` — {dim['label']} | {dim['kind']} "
                     f"| `{dim['default']}` | {_bound_description(dim, spec)} |")
    lines += ["", "## Evidence", ""]
    for e in data.get("evidence", []):
        lines.append(f"- **{e['kind']}** — {e['note']}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate"); p.add_argument("target")
    p = sub.add_parser("index"); p.add_argument("target")
    p = sub.add_parser("plan"); p.add_argument("target")
    p.add_argument("--settings", required=True)
    p.add_argument("--variant", required=True)
    p.add_argument("--out")
    args = parser.parse_args()

    path = manifest_path(args.target)

    if args.command == "validate":
        errors = validate_manifest(path)
        for err in errors:
            print(err, file=sys.stderr)
        print(f"validate: {path}, {len(errors)} error(s)")
        return 1 if errors else 0

    errors = validate_manifest(path)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    data = load_json(path)
    spec, _ = package_spec(path, data)

    if args.command == "index":
        out = path.parent / "INDEX.md"
        out.write_text(render_index(data, spec))
        print(f"index: {len(data['dimensions'])} dimension(s) → {out}")
        return 0

    if args.command == "plan":
        if not KEBAB.match(args.variant):
            print(f"plan: variant id '{args.variant}' is not kebab-case", file=sys.stderr)
            return 1
        try:
            settings = load_json(args.settings)
            plan = build_plan(data, spec, settings, args.variant)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            print(f"plan: {exc}", file=sys.stderr)
            return 1
        text = json.dumps(plan, indent=2, sort_keys=True) + "\n"
        if args.out:
            Path(args.out).write_text(text)
            print(f"plan: {args.variant} → {args.out}")
        else:
            print(text, end="")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
