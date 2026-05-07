# TODO

## Priorite haute
- Factoriser le parsing commun entre `profile.py` et `trajectory.py`.
  Aujourd'hui, les regex, les conversions de dates, les conversions latitude/longitude, l'encodage et une partie de la logique SQLite sont dupliques. Cela augmente le risque de divergence et rend les corrections plus couteuses.
- Separer plus clairement lecture, transformation et ecriture.
  Les methodes `process()` enchainent actuellement chargement, parsing, alimentation de la base SQLite, construction des tableaux et generation des sorties. Une separation en etapes plus explicites rendrait les tests et le debogage plus simples.
- Remplacer progressivement les `print()` de progression par du `logging`.
  Les modules `ascii.py`, `odv.py` et `netcdf.py` melangent actuellement logique metier et sorties console.

## Priorite moyenne
- Ajouter des tests de non-regression sur les fichiers de sortie generes.
  En complement des tests en memoire, verifier des fichiers `NetCDF`, `ODV` et `ASCII` minimaux permettrait de mieux proteger les formats produits.
- Durcir les acces aux metadonnees optionnelles dans les writers.
  Certaines sorties supposent encore des cles presentes dans les fichiers TOML sans toujours verifier leur existence.
- Ajouter une validation de configuration TOML au demarrage.
  Un controle simple des sections et des cles minimales requises permet de remonter les erreurs plus tot.
- Renommer certains identifiants ambigus.
  Des noms comme `hash`, `type` ou `file` masquent des builtins et compliquent la lecture du code.

## Priorite faible mais utile
- Moderniser le packaging et l'outillage.
  Par exemple `pyproject.toml`, un linter moderne et une CI plus actuelle que `.travis.yml`.
- Ajouter une tache `lint` dans `Taskfile.yml`.
- Documenter les variantes de configuration dans `README.md`.
  Exemple : `config.toml` vs `FR33-config.toml`, et la difference entre `casino` et `casino-fr33`.
