# DevSecOps Lab : STRIDE + revue de code + SAST + DAST

Appli Flask volontairement vulnérable (`vulnerable/`), sa version corrigée (`fixed/`), et un pipeline GitHub Actions.
**Ne jamais déployer `vulnerable/` en dehors d'un environnement de test.**

## Démarrage
```bash
git init && git add . && git commit -m "init" && git branch -M main
git remote add origin <URL> && git push -u origin main   # déclenche le workflow
```
Local :
```bash
pip install semgrep && semgrep --config .semgrep/rules.yml vulnerable/
docker build -t vuln vulnerable && docker run -p 5000:5000 vuln
docker run --network host -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://localhost:5000 -r zap.html
```

## Contenu
- `docs/01-STRIDE.md` : DFD + tableau des menaces
- `docs/02-revue-de-code.md` : revue manuelle
- `docs/03-resultats-et-comparaison.md` : résultats, SAST vs DAST vs revue
- `.github/workflows/security.yml` : Semgrep + ZAP (matrice vulnerable/fixed), SARIF
- `.semgrep/rules.yml` : règles personnalisées taguées CWE / OWASP / STRIDE

## Plan de présentation (15-20 min)
1. Contexte, shift-left (2 min) 2. DFD + STRIDE (3) 3. Pipeline (2) 4. Résultats : 3 failles en détail (5) 5. Démo : push -> Actions -> onglet Security (3) 6. SAST vs DAST vs revue, limites (3) 7. Conclusion.
