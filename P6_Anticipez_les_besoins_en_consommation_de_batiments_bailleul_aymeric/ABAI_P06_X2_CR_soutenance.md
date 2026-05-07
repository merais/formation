# Projet 6 — Anticipez les besoins en consommation de bâtiments

**Évaluation :** jeudi 13 novembre 2025
**Statut :** Projet validé

---

## Remarques sur l'évaluation

**Compétences évaluées**

---

**1. Entraîner un modèle d'apprentissage**

Validé

Commentaires :

Votre travail de préparation et de transformation des données est particulièrement rigoureux. Vous avez procédé à un nettoyage approfondi du jeu de données, en excluant les bâtiments résidentiels et les valeurs aberrantes à l'aide des colonnes Outlier et ComplianceStatus. Votre approche anti-leakage, fondée sur une détection par expressions régulières, atteste d'une excellente compréhension des risques de fuite d'information entre les variables explicatives et la cible. Le feature engineering est riche et pertinent : les variables telles que Âge du bâtiment, Surface par étage ou Surface x Âge sont autant d'exemples de transformations intelligemment pensées. L'encodage catégoriel, la normalisation et la vérification des corrélations ont été effectués avec soin. Votre démarche est complète, méthodique et conforme aux exigences d'un projet de modélisation supervisée de niveau professionnel.

---

**2. Évaluer le modèle d'apprentissage**

Validé

Commentaires :

Votre processus de modélisation est bien structuré. Trois modèles de natures différentes ont été comparés, ce qui démontre votre souci d'exploration et de justification des choix techniques. Le modèle final, une Random Forest Regressor, a été entraîné avec des paramètres maîtrisés (n_estimators=150, max_depth=30, etc.) et évalué selon une procédure de validation croisée. L'ensemble de la démarche est reproductible grâce à votre script de sauvegarde BentoML, qui assure la conservation du modèle et de ses métadonnées. Votre rigueur et la cohérence entre vos essais témoignent d'une compréhension solide des bonnes pratiques du machine learning appliqué.

---

**3. Exposer les résultats aux directions (via une API) en vue de leur exploitation**

Validé

Commentaires :

L'évaluation de votre modèle repose sur des métriques variées et pertinentes (R², MAE, RMSE), permettant une analyse complète de la performance prédictive. Les résultats, notamment un coefficient de détermination proche de 0,96 sur le jeu de test, traduisent un excellent niveau d'ajustement. Votre interprétation des feature importances est claire et met en évidence les variables les plus influentes, telles que la surface totale, le type de propriété ou le nombre d'étages, tout en proposant une lecture compréhensible des résultats d'un point de vue métier. Vous établissez un équilibre réussi entre précision statistique et interprétation opérationnelle, ce qui renforce la crédibilité de vos conclusions.

---

**4. Identifier ou créer une API compatible et l'intégrer pour permettre l'accès aux résultats**

Validé

Commentaires :

Votre implémentation d'une API à l'aide de BentoML et Pydantic V2 illustre une excellente maîtrise des standards modernes de serving de modèles. Le fichier service.py définit une architecture claire et robuste : chaque endpoint est typé, validé et documenté. La structure de la classe SeattleEnergyPredictor, la gestion des entrées via le modèle RestrictedPredictionInput et la validation systématique des contraintes numériques démontrent une maturité technique rare à ce niveau de formation. L'API intègre une logique anti-leakage cohérente avec celle du modèle et permet la reconstitution dynamique des features dérivées. La documentation Swagger générée automatiquement facilite la prise en main du service par un utilisateur non spécialiste. Cette compétence est pleinement acquise.

---

**5. Préparer et transformer des données afin de les adapter au modèle d'apprentissage**

Validé

Commentaires :

L'exposition de votre modèle sous forme d'API est parfaitement opérationnelle. Les fichiers README.md et bentofile.yaml détaillent avec précision les étapes de construction, de conteneurisation et de lancement du service. La compatibilité avec Docker, la présence d'un endpoint /health et la possibilité d'exécuter des requêtes de prédiction en local ou via le Cloud attestent de la maîtrise de l'intégration. La documentation technique est claire, accessible et conforme aux standards professionnels. Vous proposez une solution exploitable par des services métiers, ce qui répond pleinement à la finalité du projet.

---

**6. Présenter ses résultats**

Validé

Commentaires :

Votre présentation est d'une qualité remarquable, tant sur la forme que sur le fond. Elle met habilement en avant le contexte environnemental et stratégique du projet. La neutralité carbone à horizon 2050 pour la ville de Seattle, tout en valorisant les étapes méthodologiques et les résultats clés. Votre discours visuel est structuré et dynamique, combinant rigueur analytique et storytelling convaincant. Vous avez su rendre accessibles des concepts techniques complexes tout en conservant la précision scientifique requise. Votre aisance à relier la démarche scientifique à ses implications concrètes pour la transition énergétique renforce considérablement la portée du projet.

---

**Livrable**

Points forts :
- Démarche complète couvrant l'ensemble du cycle de vie du projet : de l'analyse exploratoire au déploiement.
- Prévention rigoureuse du data leakage et excellente qualité du feature engineering.
- Maîtrise des outils modernes de déploiement (BentoML, Docker, Swagger UI).
- Documentation technique exhaustive et structurée.
- Storytelling et communication des résultats clairs et percutants.

Axes d'amélioration :
- Ajouter un court module de suivi ou de supervision (logs ou métriques d'exploitation) pour anticiper une utilisation à grande échelle.
- Numérotez vos slides.

---

**Soutenance**

Remarques :

Votre travail reflète une réelle maîtrise des outils de la science des données et une compréhension approfondie des exigences de mise en production. Vous démontrez une capacité à transformer un projet de data science en solution exploitable, et une conscience métier affirmée.

---

*Note : première soutenance le 12 novembre 2025 — Projet à retravailler. Soutenance validée le 13 novembre 2025.*
