# Résultats

## Semgrep (règles maison, exécuté localement, Semgrep 1.178)
| Version | Alertes |
|---------|---------|
| vulnerable | **8** (SQLi x2, MD5 x2, SSTI/XSS, cmd injection, secret en dur, debug) |
| fixed | **0** |

Rapports : `semgrep-vulnerable.json`, `semgrep-fixed.json`. Les alertes doublonnées (2 SQLi, 2 MD5) sont des occurrences distinctes dans le code, pas des faux positifs.

## Tests dynamiques manuels (`manual-dynamic-proof.txt`)
| Test | vulnerable | fixed |
|------|-----------|-------|
| SQLi `admin'--` | connecté en admin | 401 |
| XSS `<script>` | reflété tel quel | `&lt;script&gt;` |
| IDOR `/notes/1` sans login | contenu affiché | 401 |
| Injection de commande | `uid=0(root)` | 401 (et entrée validée) |
| `/admin?admin=1` | accès admin | 401 |
| En-têtes de sécurité | absents | présents |

## Comparaison des méthodes
| | Semgrep (SAST) | ZAP (DAST) | Revue manuelle |
|---|---|---|---|
| Injections / patterns dangereux | Excellent | Bon (actif) | Bon |
| Secrets, crypto faible, config | Excellent | Non | Bon |
| En-têtes, cookies, config runtime | Non | Excellent (passif) | Moyen |
| IDOR / logique d'autorisation | **Raté** | Difficile sans auth | **Excellent** |
| Faux positifs | Possibles | Possibles | Faibles |
| Vitesse / automatisation | Très rapide | Moyenne | Lente |

Aucun outil ne suffit seul : ils sont complémentaires.

## Limites
Le scan ZAP n'a pas pu être exécuté dans l'environnement de préparation (pas de Docker) : il s'exécute dans GitHub Actions. Ajouter ensuite SCA (Dependabot / pip-audit), scan de secrets (gitleaks) et DAST authentifié.
