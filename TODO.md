# TODO

## Realise
- Ajout d'un `Taskfile.yml` avec les taches principales du projet, une tache `default`, une tache `all` et une separation explicite entre les workflows `casino` et `casino-fr33`.
- Correction de plusieurs regressions de parsing et ajout de tests de non-regression pour `COLCOR`, `CASINO`, `LADCP` et `MVP`.
- Renforcement progressif de la couverture de tests avec des cas reels pour `Profile`, `Trajectory`, `NetCDF`, la validation de configuration et les utilitaires de parsing.
- Documentation du workflow `task` dans le wiki local, de maniere generique et non liee a une campagne particuliere.
- Extraction de helpers de parsing partages dans `parsing_utils.py` pour les coordonnees et certaines conversions de dates.
- Ajout d'une validation simple de configuration au demarrage via `config_validation.py`.
- Durcissement des writers `odv.py` et `ascii.py` pour mieux tolerer des metadonnees optionnelles.
- Clarification progressive de l'orchestration avec `prepare_processing()` et `write_outputs()` dans `profile.py` et `trajectory.py`.
- Remplacement de quelques noms ambigus a fort impact, par exemple `type` par `data_type` et `hash` par `split_map` ou `metadata`.

## Priorite haute
- Factoriser le parsing commun entre `profile.py` et `trajectory.py`.
  Aujourd'hui, les regex, les conversions de dates, les conversions latitude/longitude, l'encodage et une partie de la logique SQLite sont dupliques. Cela augmente le risque de divergence et rend les corrections plus couteuses.
- Separer plus clairement lecture, transformation et ecriture.
  Les methodes `process()` ont deja ete clarifiees avec `prepare_processing()` et `write_outputs()`, mais la frontiere entre parsing, transformation et persistance reste encore tres melangee dans les classes.
- Remplacer progressivement les `print()` de progression par du `logging`.
  Les modules `ascii.py`, `odv.py` et `netcdf.py` melangent actuellement logique metier et sorties console.
- Continuer le nettoyage des noms ambigus restants et des acces fragiles a la configuration.
  Le travail a commence sur `type` et `hash`, mais il reste encore des variables et conventions locales a rendre plus explicites.
- Separer plus profondement le parsing des en-tetes et le parsing des donnees.
  Aujourd'hui, ces deux etapes restent encore fortement imbriquees dans les grandes boucles de lecture de `profile.py` et `trajectory.py`.

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
