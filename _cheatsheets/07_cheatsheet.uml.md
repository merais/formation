Bien sûr, voici une antisèche complète pour les diagrammes de classe UML, rédigée en français.

---

### Composants de base 🧱

* **Classe** : Représente un objet avec un nom, des attributs et des opérations.
    * `+` : public
    * `#` : protected
    * `-` : private
    * `~` : package/défaut
* **Attribut** : Une propriété d'une classe.
    * `visibilité nom: type [multiplicité] = valeur_par_défaut {chaîne_de_propriété}`
* **Opération (ou Méthode)** : Une action que la classe peut exécuter.
    * `visibilité nom (paramètre: type): type_de_retour {chaîne_de_propriété}`
* **Multiplicité** : Indique le nombre d'objets qui peuvent être liés.
    * `1` : Exactement un
    * `*` : Zéro ou plusieurs
    * `0..1` : Zéro ou un
    * `1..*` : Un ou plusieurs
    * `m..n` : Une plage de `m` à `n`

---

### Relations 🔗

* **Association** : Une relation générale entre des classes.
    * **Directionnelle (navigable)** : Une ligne continue avec une flèche. `ClasseA` peut "voir" `ClasseB`.
    * `ClasseA` ─────> `ClasseB`
* **Agrégation** : Une relation de type "contient", qui représente une relation tout-partie où la partie peut exister indépendamment du tout.
    * Une ligne continue avec un losange vide du côté du "tout".
    * `Tout` ◇─── `Partie`
* **Composition** : Une relation de type "contient" où la partie ne peut pas exister sans le tout. Si le tout est détruit, la partie est aussi détruite.
    * Une ligne continue avec un losange plein du côté du "tout".
    * `Tout` ◆─── `Partie`
* **Généralisation (Héritage)** : Une relation de type "est-un" où une sous-classe hérite d'une super-classe.
    * Une ligne continue avec une flèche creuse pointant de la sous-classe vers la super-classe.
    * `Sous-classe` ─────────▷ `Super-classe`
* **Dépendance** : Une relation de type "utilise", où une modification dans une classe peut en affecter une autre. Représentée par une ligne en pointillés avec une flèche.
    * `Client` ⇢⇢⇢⇢⇢⇢ `Fournisseur`
* **Réalisation (Implémentation d'interface)** : Une classe implémente le comportement spécifié par une interface. Représentée par une ligne en pointillés avec une flèche creuse.
    * `Classe` ⇢⇢⇢⇢⇢⇢▷ `Interface`

---

### Éléments supplémentaires ➕

* **Interface** : Une collection d'opérations qui spécifient un service, mais pas son implémentation. Représentée par un stéréotype de classe (`<<interface>>`) ou un petit cercle (notation en sucette ou "lollipop").
* **Classe abstraite** : Une classe qui ne peut pas être instanciée. Son nom est écrit en italique.
* **Stéréotype** : Une façon d'étendre le vocabulaire UML, écrit entre guillemets (`<< >>`).
* **Note** : Un commentaire pour ajouter une clarification, lié par une ligne en pointillés.
* **Contraintes** : Règles ou conditions, souvent écrites entre accolades `{ }`.