# Matplotlib

## Importation et création de base

Il est d'usage d'importer Matplotlib sous l'alias `plt` et de l'utiliser en conjonction avec NumPy ou Pandas.

```python
import matplotlib.pyplot as plt
import numpy as np
```

  * **Créer une figure et des axes** :

    ```python
    fig, ax = plt.subplots() # La méthode recommandée
    ```

      * `fig` est la figure entière (la fenêtre).
      * `ax` est l'espace où l'on va tracer le graphique.

  * **Afficher le graphique** :

    ```python
    plt.show() # Affiche la fenêtre avec le graphique
    ```

-----

## Types de graphiques courants

  * **Graphique linéaire (line plot)** :

    ```python
    x = np.linspace(0, 10, 100) # Crée 100 points entre 0 et 10
    y = np.sin(x)
    ax.plot(x, y, label='sin(x)')
    ```

  * **Nuage de points (scatter plot)** :

    ```python
    ax.scatter(np.random.rand(50), np.random.rand(50))
    ```

  * **Histogramme** :

    ```python
    data = np.random.randn(1000)
    ax.hist(data, bins=30)
    ```

  * **Diagramme à barres (bar chart)** :

    ```python
    noms = ['A', 'B', 'C']
    valeurs = [10, 25, 15]
    ax.bar(noms, valeurs)
    ```

  * **Diagramme circulaire (pie chart)** :

    ```python
    etiquettes = ['A', 'B', 'C']
    tailles = [15, 30, 45]
    ax.pie(tailles, labels=etiquettes, autopct='%1.1f%%')
    ```

-----

## Personnalisation du graphique

  * **Ajouter des titres et des étiquettes** :

    ```python
    ax.set_title('Titre du graphique')
    ax.set_xlabel('Étiquette de l\'axe des X')
    ax.set_ylabel('Étiquette de l\'axe des Y')
    ```

  * **Ajouter une légende** :

    ```python
    ax.legend() # Nécessite que les lignes aient un `label`
    ```

  * **Modifier les limites des axes** :

    ```python
    ax.set_xlim(0, 5) # Limites de l'axe des X
    ax.set_ylim(0, 1) # Limites de l'axe des Y
    ```

  * **Changer les couleurs et styles** :

    ```python
    ax.plot(x, y, color='red', linestyle='--', marker='o')
    ```

      * Les options de couleur peuvent être des noms (ex: `'red'`) ou des codes hexadécimaux (ex: `'#FF5733'`).

-----

## Graphiques multiples

  * **Graphiques multiples sur la même figure** :
    ```python
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4)) # 1 ligne, 2 colonnes
    ax1.plot(x, y)
    ax2.scatter(x, y)
    plt.tight_layout() # Ajuste l'espacement pour éviter les chevauchements
    ```

-----

## Sauvegarde du graphique

  * **Sauvegarder en fichier image** :
    ```python
    plt.savefig('mon_graphique.png', dpi=300) # En PNG avec 300 dpi
    ```
    Les formats courants sont PNG, JPG, PDF et SVG.