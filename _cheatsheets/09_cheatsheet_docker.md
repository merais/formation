## Docker : Commandes de Base

### Construction et Images

  * **Construire une image :**
      * `docker build -t mon-image:latest .`
        (Construit à partir du `Dockerfile` dans le répertoire courant et **tag** l'image.)
  * **Lister les images locales :**
      * `docker images` ou `docker image ls`
  * **Télécharger une image (Pull) :**
      * `docker pull ubuntu:22.04`
  * **Supprimer une image :**
      * `docker rmi mon-image:latest`

### Conteneurs (Lancement et Exécution)

  * **Créer et démarrer un conteneur :**
      * `docker run -d -p 8080:80 --name mon-web nginx`
          * `-d` : Détaché (en arrière-plan).
          * `-p HOTE:CONTAINER` : Mappe le port.
          * `--name NOM` : Nomme le conteneur.
  * **Lancer en mode interactif (Shell) :**
      * `docker run -it ubuntu bash`
  * **Exécuter une commande dans un conteneur en cours :**
      * `docker exec -it mon-web /bin/bash`
  * **Lister les conteneurs en cours d'exécution :**
      * `docker ps`
  * **Lister tous les conteneurs (y compris arrêtés) :**
      * `docker ps -a`
  * **Afficher les logs :**
      * `docker logs -f mon-web` (le flag `-f` suit la sortie)

### Contrôle et Nettoyage

  * **Démarrer / Arrêter / Redémarrer un conteneur :**
      * `docker start mon-web`
      * `docker stop mon-web`
      * `docker restart mon-web`
  * **Supprimer un conteneur arrêté :**
      * `docker rm nom_du_conteneur`
  * **Nettoyage général (supprime les conteneurs arrêtés, les réseaux inutilisés, etc.) :**
      * `docker system prune`
  * **Nettoyage complet (ajoute les images non utilisées) :**
      * `docker system prune -a`

-----

## Docker Compose : Gestion Multi-Conteneurs

Docker Compose utilise un fichier **`compose.yaml`** (ou `docker-compose.yml`) pour définir votre application.

### Commandes `docker compose`

**(Utilisez la commande `docker compose` sans tiret pour les installations récentes.)**

  * **Démarrer l'application (Build + Run) :**
      * `docker compose up -d`
        (Construit les images si nécessaire et démarre les services en arrière-plan.)
      * `docker compose up --build`
        (Force la reconstruction des images avant de démarrer.)
  * **Arrêter et supprimer l'application :**
      * `docker compose down`
        (Arrête les conteneurs et supprime les conteneurs et les réseaux.)
      * `docker compose down -v`
        (Supprime également les **volumes nommés**.)
  * **Lister les services en cours :**
      * `docker compose ps`
  * **Afficher les logs de tous les services :**
      * `docker compose logs -f`
  * **Exécuter une commande ponctuelle (one-off command) :**
      * `docker compose run web sh`
  * **Exécuter une commande dans un service déjà en cours :**
      * `docker compose exec db psql -U user`

### Structure de `compose.yaml` (Points Clés)

```yaml
version: '3.8'

services:
  web:
    # 1. Image : Utiliser une image existante
    # image: nginx:latest
    # 2. Build : Construire à partir du Dockerfile local
    build: .
    ports:
      - "8080:80" # HOTE:CONTAINER
    volumes:
      - ./mon-code:/app # Monter le répertoire local dans le conteneur
    environment:
      - API_URL=http://api:3000
    depends_on:
      - api # Assure l'ordre de démarrage

  api:
    image: node:18-alpine
    # ... autres configurations
```