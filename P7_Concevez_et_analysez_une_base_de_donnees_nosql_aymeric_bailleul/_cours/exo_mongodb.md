## **Pour chacune des questions suivantes, veuillez fournir la commande associée et non le résultat.**

1. **Importez le jeu de données tour-pedia.json dans une base de données “tourPedia” avec une collection “paris” ;**
---
    - use tourPedia
    - db.createCollection("paris")
    - mongoimport --db toutPedia --collection paris --file tourPedia_paris.json --jsonArray
---
1.  **Filtrez les lieux par type “accommodation” et service “blanchisserie” ;** 
---
    - db["paris"].find({"category" : "accommodation"}) > 3376
    - db["paris"].find({"services":"blanchisserie"}) > 616
    - db["paris"].find({"category" : "accommodation","services":"blanchisserie"}) > 616
---
1.  **Projetez les adresses des lieux de type "accommodation" ;** 
---
    - db["paris"].find({"category" : "accommodation"},{"location.address" : 1})
---
1.  **Filtrez les listes de commentaires (reviews) des lieux, pour lesquelles au moins un commentaire (reviews) est écrit en anglais (en) et a une note (rating) supérieure à 3 (attention, LE commentaire en anglais doit avoir un rating de 3 ou plus) ;** 
---
    - db["paris"].find({
        reviews: {
            $elemMatch: {
            language: "en",
            rating: { $gt: 3 }
            }
        }
      })
---
1.  **Groupez les lieux par catégorie et comptez les ;**
---

---
6.  **Créez un pipeline d’agrégation pour les lieux de catégorie "accommodation", et donnez le nombre de lieux par valeur de "services" ;**
---

---