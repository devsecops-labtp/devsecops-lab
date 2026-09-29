# Revue de code manuelle (checklist OWASP Top 10)

| Zone | Fichier:ligne | Constat | OWASP | Correctif |
|------|---------------|---------|-------|-----------|
| Secrets | `vulnerable/app.py:8` | `secret_key` en clair dans le dépôt | A02 | `os.environ["SECRET_KEY"]` |
| Authentification | `:22, :39` | MD5 sans sel | A02 | `generate_password_hash` / `check_password_hash` |
| Entrées / SQL | `:41` | Requête construite avec `%` | A03 | `execute(q, (name,))` |
| Sortie / XSS | `:54` | `render_template_string("..." + term)` | A03 | `escape()` ou template avec variable |
| Contrôle d'accès | `:60` | Aucune vérification du propriétaire de la note | A01 | `login_required` + `AND owner=?` |
| Commandes | `:68` | `shell=True` avec entrée utilisateur | A03 | Liste d'arguments + validation `ipaddress` |
| Autorisation | `:75` | Droit admin lu dans la query string | A01 | Rôle stocké dans la session serveur |
| Configuration | `:81` | `debug=True`, `host=0.0.0.0` | A05 | `debug=False`, reverse proxy |
| Journalisation | global | Aucun log de sécurité | A09 | `logging` sur login ok/ko |
| Anti brute force | `:44` | Pas de limitation | A07 | Compteur / Flask-Limiter |
| En-têtes | global | Aucun header de sécurité | A05 | `after_request` |

Le **contrôle d'accès (A01)** et la **logique d'autorisation** sont les zones où la relecture apporte le plus.
