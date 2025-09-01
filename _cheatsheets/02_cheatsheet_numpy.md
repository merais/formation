# Numpy

## Importation et création de base

Pour commencer, il est d'usage d'importer la librairie sous l'abréviation `np`.

```python
import numpy as np
```

  * **Créer un tableau (array) 1D** :
    ```python
    a = np.array([1, 2, 3, 4])
    ```
  * **Créer un tableau 2D** :
    ```python
    b = np.array([[1, 2, 3], [4, 5, 6]])
    ```
  * **Créer un tableau avec des zéros** :
    ```python
    np.zeros((3, 4)) # Crée un tableau de 3x4 rempli de zéros
    ```
  * **Créer un tableau avec des uns** :
    ```python
    np.ones((2, 3)) # Crée un tableau de 2x3 rempli de uns
    ```
  * **Créer une séquence numérique** :
    ```python
    np.arange(10) # Crée un tableau de 0 à 9
    np.arange(2, 10, 2) # De 2 à 9, avec un pas de 2
    ```
  * **Créer des nombres aléatoires** :
    ```python
    np.random.rand(2, 3) # Nombres aléatoires entre 0 et 1 dans un tableau de 2x3
    np.random.randint(0, 10, size=(2, 3)) # Entiers aléatoires entre 0 et 10
    ```

-----

## Aperçu des tableaux

  * **Forme du tableau** :
    ```python
    a.shape
    ```
  * **Dimension du tableau** :
    ```python
    a.ndim
    ```
  * **Type de données** :
    ```python
    a.dtype
    ```
  * **Taille totale (nombre d'éléments)** :
    ```python
    a.size
    ```

-----

## Sélection et indexation

  * **Sélection d'un élément** :
    ```python
    a[0] # Premier élément d'un tableau 1D
    b[0, 1] # Élément à la ligne 0, colonne 1 d'un tableau 2D
    ```
  * **Slicing (tranches)** :
    ```python
    a[1:3] # Éléments de l'index 1 à 2
    b[0:2, 1] # Lignes 0 et 1, colonne 1
    ```
  * **Indexation booléenne** :
    ```python
    a[a > 2] # Sélectionne les éléments plus grands que 2
    ```

-----

## Manipulation des formes

  * **Redimensionner le tableau** :
    ```python
    c = a.reshape(2, 2) # Change la forme de 'a' en 2x2
    ```
  * **Aplatir le tableau** :
    ```python
    c.ravel() # Ramène un tableau 2D à 1D
    ```
  * **Ajouter une dimension** :
    ```python
    a[:, np.newaxis] # Transforme un tableau 1D en 2D (colonne)
    ```

-----

## Opérations mathématiques

NumPy permet d'effectuer des calculs sur des tableaux entiers, ce qui est très performant.

  * **Opérations arithmétiques** :
    ```python
    a + 2 # Ajoute 2 à chaque élément
    a * 2 # Multiplie chaque élément par 2
    a + a # Additionne deux tableaux (élément par élément)
    ```
  * **Fonctions universelles (ufunc)** :
    ```python
    np.sqrt(a) # Racine carrée de chaque élément
    np.sin(a) # Sinus de chaque élément
    ```
  * **Statistiques** :
    ```python
    np.mean(a) # Moyenne des éléments
    np.sum(a) # Somme des éléments
    np.max(a) # Valeur maximale
    ```
  * **Produit matriciel** :
    ```python
    np.dot(a, b) # Produit de deux matrices
    # Ou a @ b depuis Python 3.5
    ```

-----

## Sauvegarde

  * **Sauvegarder en fichier binaire** :
    ```python
    np.save('mon_tableau.npy', a)
    ```
  * **Charger un fichier binaire** :
    ```python
    loaded_array = np.load('mon_tableau.npy')
    ```