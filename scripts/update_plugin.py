"""Übernimmt den geprüften Stand eines Original-Repositories in plugins/<name>/.

Aufruf:  python3 scripts/update_plugin.py <name> <pfad-zum-upstream-klon>

Kopiert nur die in sources.json unter "include" genannten Pfade (relativ zu
"subdir", falls gesetzt). Optional:
  "map":      {"quelle": "ziel"} kopiert Pfade unter neuem Namen
  "manifest": {...} schreibt .claude-plugin/plugin.json, falls das Original keins hat
  "exclude":  ["glob", ...] entfernt nach dem Kopieren passende Dateien (relativ zu plugins/<name>)
  "patches":  [{"file", "old", "new"}] ersetzt Text nach dem Kopieren; {upstream_version}
              wird durch die Version aus pyproject.toml/package.json ersetzt.
              Fehlt "old", bricht das Skript ab (Upstream hat sich geändert → neu prüfen).
Setzt
reviewed_commit/reviewed_date und baut .claude-plugin/marketplace.json neu.
Führt keinen Code aus dem Upstream aus.
"""
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def build_marketplace(data):
    plugins = []
    for p in data["plugins"]:
        manifest = ROOT / "plugins" / p["name"] / ".claude-plugin" / "plugin.json"
        desc = p.get("description", "")
        if manifest.exists():
            desc = json.loads(manifest.read_text(encoding="utf-8")).get("description", desc)
        item = {
            "name": p["name"],
            "source": f"./plugins/{p['name']}",
            "description": desc,
        }
        item.update(p.get("marketplace_extra", {}))
        plugins.append(item)
    MARKETPLACE.parent.mkdir(parents=True, exist_ok=True)
    MARKETPLACE.write_text(json.dumps({
        "name": "bestoug-plugins",
        "owner": {"name": "Bestoug"},
        "metadata": {"description": "Philipps geprüfte Claude-Plugins. Updates werden vor der Übernahme auf Schadcode geprüft."},
        "plugins": plugins,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--marketplace-only":
        build_marketplace(json.loads(SOURCES.read_text(encoding="utf-8")))
        return
    name, upstream = sys.argv[1], Path(sys.argv[2]).resolve()
    data = json.loads(SOURCES.read_text(encoding="utf-8"))
    entry = next(p for p in data["plugins"] if p["name"] == name)

    target = ROOT / "plugins" / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    base = upstream / entry.get("subdir", "")
    pairs = [(rel, rel) for rel in entry.get("include", [])] + list(entry.get("map", {}).items())
    for rel, out in pairs:
        src = base / rel
        if not src.exists():
            continue
        dst = target / out
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, symlinks=False)
        else:
            shutil.copy2(src, dst)

    for pattern in entry.get("exclude", []):
        for f in sorted(target.glob(pattern), reverse=True):
            if f.is_dir():
                shutil.rmtree(f)
            elif f.exists():
                f.unlink()

    manifest = target / ".claude-plugin" / "plugin.json"
    if "manifest" in entry and not manifest.exists():
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(entry["manifest"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    version = ""
    for meta, pattern in (("pyproject.toml", r'^version\s*=\s*"([^"]+)"'), ("package.json", r'"version"\s*:\s*"([^"]+)"')):
        f = base / meta
        if f.exists():
            m = re.search(pattern, f.read_text(encoding="utf-8"), re.M)
            if m:
                version = m.group(1)
                break
    for patch in entry.get("patches", []):
        f = target / patch["file"]
        text = f.read_text(encoding="utf-8")
        if patch["old"] not in text:
            sys.exit(f"{name}: Patch passt nicht mehr in {patch['file']} – Upstream geändert, bitte neu prüfen")
        f.write_text(text.replace(patch["old"], patch["new"].replace("{upstream_version}", version)), encoding="utf-8")

    commit = subprocess.run(["git", "-C", str(upstream), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    entry["reviewed_commit"] = commit
    entry["reviewed_date"] = datetime.date.today().isoformat()
    SOURCES.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_marketplace(data)
    print(f"{name}: übernommen auf Stand {commit}")


if __name__ == "__main__":
    main()
