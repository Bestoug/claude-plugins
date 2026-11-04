# claude-plugins

Philipps eigener, geprüfter Plugin-Marktplatz für Claude.

Hier liegen Kopien fremder Claude-Plugins. Neue Versionen der Originale werden jede Woche automatisch von Claude auf Schadcode, Datenabfluss und Prompt-Injection geprüft und nur übernommen, wenn sie unbedenklich sind. claude.ai synchronisiert diesen Marktplatz automatisch.

## Enthaltene Plugins
| Plugin | Original | Lizenz |
|---|---|---|
| andrej-karpathy-skills | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | MIT |
| marketing-skills | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | MIT |
| superpowers | [obra/superpowers](https://github.com/obra/superpowers) | MIT |
| ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT |
| graphify (nur Skill, angepasst: nur auf Zuruf, feste Paketversion) | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Apache-2.0 |
| anatomy (ohne Galerie-Upload, nur auf Zuruf) | [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | MIT |
| feature-dev, code-review, security-guidance, claude-md-management, swift-lsp | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (Unterordner `plugins/`) | siehe LICENSE |

Die geprüften Stände stehen in `sources.json`. Alle Rechte an den Plugins liegen bei den jeweiligen Autoren; die Lizenzdateien liegen in den Plugin-Ordnern.

## Aufbau
- `.claude-plugin/marketplace.json`: Katalog für claude.ai
- `plugins/<name>/`: geprüfte Kopie des Plugins
- `sources.json`: Herkunft und geprüfter Stand je Plugin
- `scripts/update_plugin.py`: übernimmt einen geprüften Stand

## In claude.ai einbinden
Customize → Plugins → Hinzufügen → Marketplace hinzufügen → Aus einem Repository hinzufügen → `Bestoug/claude-plugins`
