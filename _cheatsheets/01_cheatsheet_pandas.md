# Pandas

## Importation et création de base

Pour commencer, il faut toujours importer la librairie, généralement sous l'abréviation `pd`.

```python
import pandas as pd
import numpy as np # Souvent utilisé avec pandas
```

  * **Créer une Series** (une colonne) :
    ```python
    s = pd.Series([1, 3, 5, np.nan, 6, 8])
    ```
  * **Créer un DataFrame** (un tableau) à partir d'un dictionnaire :
    ```python
    data = {'A': [1, 2, 3], 'B': ['foo', 'bar', 'baz']}
    df = pd.DataFrame(data)
    ```
  * **Créer un DataFrame** à partir d'un tableau NumPy :
    ```python
    df2 = pd.DataFrame(np.random.randn(6, 4), columns=list('ABCD'))
    ```
  * **Lire un fichier CSV** :
    ```python
    df = pd.read_csv('chemin/vers/votre/fichier.csv')
    ```

-----

## Aperçu des données

Ces commandes sont utiles pour explorer vos données après les avoir chargées.

  * **Afficher les premières lignes** :
    ```python
    df.head() # Les 5 premières
    df.head(10) # Les 10 premières
    ```
  * **Afficher les dernières lignes** :
    ```python
    df.tail()
    ```
  * **Obtenir des informations sur le DataFrame** (colonnes, types, etc.) :
    ```python
    df.info()
    ```
  * **Statistiques descriptives** :
    ```python
    df.describe() # Donne la moyenne, l'écart-type, etc.
    ```
  * **Noms des colonnes** :
    ```python
    df.columns
    ```
  * **Forme du DataFrame** (lignes, colonnes) :
    ```python
    df.shape
    ```

-----

## Sélection de données

  * **Sélectionner une colonne** :
    ```python
    df['nom_colonne']
    df.nom_colonne # Attention, ne fonctionne pas si le nom a des espaces
    ```
  * **Sélectionner plusieurs colonnes** :
    ```python
    df[['colonne1', 'colonne2']]
    ```
  * **Sélectionner par position** (`iloc`) :
    ```python
    df.iloc[0] # La première ligne
    df.iloc[0, 1] # La valeur à la ligne 0, colonne 1
    df.iloc[0:3] # Les 3 premières lignes
    ```
  * **Sélectionner par étiquette** (`loc`) :
    ```python
    df.loc[0] # La ligne avec l'index 0
    df.loc[0, 'colonne'] # La valeur à la ligne 0 et à la colonne 'colonne'
    ```
  * **Filtrage conditionnel** :
    ```python
    df[df['age'] > 30] # Lignes où la colonne 'age' est > 30
    df[(df['age'] > 30) & (df['ville'] == 'Paris')] # Filtrage avec plusieurs conditions
    ```

-----

## Manipulation des données

  * **Ajouter une nouvelle colonne** :
    ```python
    df['nouvelle_col'] = df['col1'] + df['col2']
    ```
  * **Supprimer une colonne** :
    ```python
    df.drop('colonne_a_supprimer', axis=1, inplace=True)
    ```
  * **Renommer des colonnes** :
    ```python
    df.rename(columns={'vieux_nom': 'nouveau_nom'}, inplace=True)
    ```
  * **Gérer les valeurs manquantes** (`NaN`) :
    ```python
    df.dropna() # Supprime les lignes avec au moins une valeur NaN
    df.fillna(0) # Remplace les NaN par 0
    ```
  * **Appliquer une fonction** :
    ```python
    df['colonne'].apply(lambda x: x * 2)
    ```

-----

## Groupement et agrégation

  * **Grouper des données** (`groupby`) :
    ```python
    grouped = df.groupby('colonne_de_groupement')
    ```
  * **Calculer la moyenne par groupe** :
    ```python
    grouped['colonne_numerique'].mean()
    ```
  * **Compter le nombre d'occurrences** :
    ```python
    df['colonne'].value_counts()
    ```

-----

## Opérations de fusion et de jointure

  * **Concaténer** des DataFrames (ajouter des lignes) :
    ```python
    df_concat = pd.concat([df1, df2])
    ```
  * **Fusionner** des DataFrames (jointure) :
    ```python
    df_merged = pd.merge(df1, df2, on='clé_commune')
    ```

-----

## Sauvegarde

  * **Sauvegarder en fichier CSV** :
    ```python
    df.to_csv('resultats.csv', index=False)
    ```