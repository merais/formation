# Seaborn

## Importation et configuration de base

Il est d'usage d'importer Seaborn sous l'alias `sns`. Souvent, il est utilisé avec Matplotlib pour les personnalisations avancées.

```python
import seaborn as sns
import matplotlib.pyplot as plt
```

  * **Définir le style de base** :

    ```python
    sns.set_style('whitegrid') # Change l'apparence des graphiques
    # Autres styles : 'darkgrid', 'white', 'dark', 'ticks'
    ```

  * **Charger un jeu de données de démonstration** :

    ```python
    tips = sns.load_dataset('tips')
    # d'autres datasets : 'iris', 'titanic', 'flights'
    ```

-----

## Types de graphiques courants

Seaborn excelle dans la création de graphiques à partir de DataFrames. La plupart des fonctions prennent en charge les arguments `x`, `y` et `data`.

### Graphiques relationnels

  * **Nuage de points (scatterplot)** :

    ```python
    sns.scatterplot(x='total_bill', y='tip', data=tips)
    ```

      * Pour ajouter une dimension (par exemple, la couleur) :
        ```python
        sns.scatterplot(x='total_bill', y='tip', hue='time', data=tips)
        ```

  * **Graphique linéaire** :

    ```python
    sns.lineplot(x='size', y='total_bill', data=tips)
    ```

### Graphiques catégoriels

  * **Diagramme à barres (bar plot)** :

    ```python
    sns.barplot(x='day', y='total_bill', data=tips)
    ```

  * **Diagramme en boîtes (box plot)** :

    ```python
    sns.boxplot(x='day', y='total_bill', data=tips)
    ```

  * **Diagramme en violon (violin plot)** :

    ```python
    sns.violinplot(x='day', y='total_bill', data=tips)
    ```

  * **Nuage de points par catégorie (swarm plot)** :

    ```python
    sns.swarmplot(x='day', y='total_bill', data=tips)
    ```

### Graphiques de distribution

  * **Histogramme (displot)** :

    ```python
    sns.displot(data=tips, x='total_bill', kde=True) # avec une estimation de la densité (kde)
    ```

  * **Matrice de corrélation (heatmap)** :

    ```python
    corr = tips.corr(numeric_only=True)
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    ```

-----

## Personnalisation et graphiques multiples

  * **Définir les titres et les étiquettes avec Matplotlib** :

    ```python
    plt.title('Titre du graphique')
    plt.xlabel('Nom de l\'axe X')
    plt.ylabel('Nom de l\'axe Y')
    ```

  * **Gérer les axes de manière explicite** :

    ```python
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x='total_bill', y='tip', data=tips, ax=ax)
    ```

  * **Graphiques multi-facettes (Facets)** :
    Ces fonctions créent une grille de graphiques basés sur une variable catégorielle.

    ```python
    sns.relplot(x='total_bill', y='tip', col='time', data=tips) # 2 graphiques, un pour chaque 'time'
    sns.catplot(x='day', y='tip', kind='box', col='sex', data=tips) # Boîtes par jour et par sexe
    ```

-----

## Sauvegarde du graphique

  * **Sauvegarder le graphique** :
    ```python
    plt.savefig('mon_graphique_seaborn.png', dpi=300)
    ```

En combinant Matplotlib et Seaborn, vous pouvez créer des visualisations à la fois esthétiques et très personnalisées.