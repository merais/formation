Absolument. Voici une **cheatsheet sur les statistiques en Python**, formatée en Markdown pour une lisibilité optimale.

-----

## 📊 Concepts de base et mesures clés

### Mesures de tendance centrale

  * **Moyenne :** La somme des valeurs divisée par le nombre de valeurs. Elle est sensible aux valeurs extrêmes.
  * **Médiane :** La valeur qui se trouve au milieu d'un ensemble de données trié. Elle est robuste face aux valeurs extrêmes.
  * **Mode :** La valeur la plus fréquente dans un ensemble de données.

### Mesures de dispersion

  * **Étendue :** La différence entre la valeur maximale et minimale.
  * **Variance :** Mesure la dispersion des données autour de la moyenne (moyenne des écarts au carré).
  * **Écart-type :** La racine carrée de la variance. Il est dans la même unité que les données, ce qui le rend plus facile à interpréter.
  * **Écart interquartile (IQR) :** L'intervalle qui contient les 50 % des données centrales. C'est la différence entre le 3e quartile ($Q\_3$) et le 1er quartile ($Q\_1$).

-----

## 🐍 Bibliothèques et commandes Python

### NumPy (Calculs rapides)

Idéale pour les calculs sur les tableaux (`numpy.array`).

```python
import numpy as np

données = np.array([1, 2, 3, 4, 5, 10, 20])

# Tendance centrale
moyenne = np.mean(données)
médiane = np.median(données)

# Dispersion
variance = np.var(données)
écart_type = np.std(données)
étendue = np.ptp(données) # 'peak-to-peak'
```

### SciPy (Statistiques avancées)

Fournit des fonctions statistiques plus complexes, des distributions et des tests d'hypothèses.

```python
from scipy import stats
import numpy as np

données = np.array([1, 2, 3, 3, 4, 5])

# Statistiques descriptives
stat_descriptives = stats.describe(données)

# Mode
mode_val, mode_count = stats.mode(données)

# Asymétrie (skewness) et aplatissement (kurtosis)
asymétrie = stats.skew(données)
aplatissement = stats.kurtosis(données)

# Exemple de test t de Student pour deux échantillons
échantillon1 = np.array([1, 2, 3])
échantillon2 = np.array([4, 5, 6])
stat_t, p_val = stats.ttest_ind(échantillon1, échantillon2)
```

### Pandas (Manipulation de données)

La bibliothèque de choix pour la manipulation et l'analyse de données tabulaires (DataFrame).

```python
import pandas as pd

# Création d'un DataFrame
df = pd.DataFrame({
    'Âge': [25, 30, 35, 40],
    'Score': [85, 90, 78, 92]
})

# Statistiques descriptives pour tout le DataFrame
résumé_stats = df.describe()

# Statistiques pour une seule colonne
moyenne_âge = df['Âge'].mean()
médiane_score = df['Score'].median()

# Corrélation entre colonnes
matrice_corrélation = df.corr()
```