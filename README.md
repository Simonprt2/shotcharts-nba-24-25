# NBA Shot Charts 2024-2025

Application interactive de visualisation des tirs NBA pour la saison 2024-2025. Créez des shot charts détaillés pour n'importe quel joueur avec analyse par zone et statistiques avancées.

## Fonctionnalités

- **Shot Chart interactif** : Visualisation de tous les tirs d'un joueur sur un terrain de basket
  - Tirs réussis en bleu
  - Tirs manqués en rouge
  - Terrain professionnel avec lignes réglementaires (raquette, ligne des 3 points, cercle central)

- **Analyse par zone** : Découpage du terrain en 9 zones stratégiques
  - Raquette
  - Corners 3 points (gauche/droit)
  - Zones à 3 points (côté gauche, côté droit, centre)
  - Zones de mid-range (gauche, droit, ailes, centre)

- **Statistiques joueur** :
  - Pourcentage global de réussite
  - Détail par zone (minimum 5 tentatives pour fiabilité)
  - Photo du joueur et logo de l'équipe
  - Taille, poids et position (via NBA API)


## Pour Lancer
  pip install streamlit pandas plotly numpy nba-api
  streamlit run shotcharts.py