# Modélisation STRIDE

## DFD (niveau 1)

```
[Utilisateur / Attaquant] --HTTP--> ||frontière de confiance : Internet -> serveur|| --> (P1 Flask app)
(P1 Flask app) <--SQL--> [D1 SQLite : users, notes]
(P1 Flask app) --shell--> [P2 OS : ping]
```
Éléments : **E1** navigateur (externe), **P1** application Flask, **P2** commande système `ping`, **D1** base SQLite, flux **F1** (HTTP), **F2** (SQL), **F3** (shell).

## Tableau des menaces

| # | Élément | STRIDE | Scénario | Impact | Sév. | Mesure (fixed) | Détecté par |
|---|---------|--------|----------|--------|------|----------------|-------------|
| T1 | P1 /login | **S** | `name=admin'--` contourne le mot de passe | Usurpation admin | Crit. | Requête paramétrée | Semgrep, revue, test manuel, ZAP actif |
| T2 | P1 /admin | **S/E** | `?admin=1` donne l'accès admin | Élévation de privilèges | Crit. | Rôle en session côté serveur | **Revue + test manuel uniquement** |
| T3 | P1 /ping, F3 | **E** | `host=127.0.0.1;id` -> RCE (uid=0) | Prise de contrôle serveur | Crit. | `ipaddress` + liste d'args, sans shell, admin only | Semgrep, revue, ZAP actif |
| T4 | P1 /search | **T/I** | `<script>` réfléchi ; concaténation dans template | XSS, vol de session | Haute | `escape()` | Semgrep, revue, ZAP |
| T5 | P1 /notes/<id> | **I** | Lire la note d'un autre sans être connecté (IDOR) | Fuite de données | Haute | Auth + `owner=?` | **Revue + test manuel uniquement** |
| T6 | D1 users | **I** | Mots de passe en MD5 sans sel | Cassage rapide en cas de fuite | Haute | scrypt (werkzeug) | Semgrep, revue |
| T7 | P1 config | **I/S** | `secret_key` en dur -> forge de cookies de session | Usurpation | Haute | Variable d'environnement | Semgrep, revue |
| T8 | P1 config | **I/E** | `debug=True` -> console Werkzeug | RCE potentielle | Haute | `debug=False` | Semgrep, ZAP (erreurs) |
| T9 | P1 /login | **D** | Brute force / requêtes massives | Indisponibilité, devinette | Moy. | Limite 5 essais (Flask-Limiter en prod) | Revue |
| T10 | P1 global | **R** | Aucun log de connexion/action | Non-répudiation impossible | Moy. | `logging` login ok/ko | Revue |
| T11 | P1 réponses | **I/T** | Pas de CSP, X-Frame-Options, nosniff | Clickjacking, XSS facilité | Moy. | `after_request` | ZAP passif |

## Lecture pour la présentation
- Chaque catégorie STRIDE est couverte au moins une fois.
- **T2 et T5** (contrôle d'accès) sont invisibles aux règles Semgrep génériques : ce sont des failles de logique métier.
