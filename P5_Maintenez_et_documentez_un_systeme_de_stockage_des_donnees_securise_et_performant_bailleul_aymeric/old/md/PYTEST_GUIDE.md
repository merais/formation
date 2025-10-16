# 🧪 Guide des Tests avec Pytest

## Vue d'ensemble

Ce projet utilise **pytest** pour tester la sécurité et les fonctionnalités de MongoDB avec différents niveaux de permissions.

---

## 📋 Types de Tests Disponibles

### 1. Tests Généraux de Connexion
**Fichier**: `docker_tests_bdd_pytest.py`
- Test de connexion à MongoDB
- Vérification de la présence de la collection
- Tests de base

**Commande**:
```bash
docker compose run --rm tests
```

### 2. Tests de Sécurité - Lecture Seule (readonly_user)
**Fichier**: `test_readonly_security.py`
- ✅ **Doit réussir**: Lecture des données
- ❌ **Doit échouer**: Insertion, mise à jour, suppression

**Commande**:
```bash
docker compose run --rm readonly_test
```

**Tests inclus**:
- `test_connection_success` - Connexion réussie
- `test_read_count_documents` - Comptage des documents
- `test_read_find_one` - Lecture d'un document
- `test_read_find_multiple` - Lecture de plusieurs documents
- `test_insert_should_fail` - Insertion refusée ✗
- `test_update_should_fail` - Mise à jour refusée ✗
- `test_delete_should_fail` - Suppression refusée ✗
- `test_drop_collection_should_fail` - Suppression collection refusée ✗
- `test_filter_by_gender` - Filtrage par genre
- `test_aggregation_pipeline` - Pipeline d'agrégation
- `test_sort_and_limit` - Tri et limitation

### 3. Tests de Sécurité - Lecture/Écriture (app_user)
**Fichier**: `test_readwrite_security.py`
- ✅ **Doit réussir**: Toutes les opérations CRUD

**Commande**:
```bash
docker compose run --rm readwrite_test
```

**Tests inclus**:
- `test_connection_success` - Connexion réussie
- `test_read_permissions` - Lecture autorisée
- `test_insert_document` - Insertion autorisée ✓
- `test_update_document` - Mise à jour autorisée ✓
- `test_delete_document` - Suppression autorisée ✓
- `test_create_index` - Création d'index autorisée ✓
- `test_drop_collection` - Suppression collection autorisée ✓
- `test_bulk_insert` - Insertion en masse ✓
- `test_bulk_update` - Mise à jour en masse ✓
- `test_bulk_delete` - Suppression en masse ✓
- `test_complex_query` - Requête complexe ✓
- `test_aggregation_pipeline` - Agrégation complexe ✓

---

## 🚀 Utilisation

### Exécuter tous les tests
```bash
# Test de connexion de base
docker compose run --rm tests

# Tests de lecture seule
docker compose run --rm readonly_test

# Tests de lecture/écriture
docker compose run --rm readwrite_test
```

### Options pytest utiles

```bash
# Mode verbose avec sortie des prints
docker compose run --rm tests pytest -v -s

# Exécuter un test spécifique
docker compose run --rm readonly_test pytest -v test_readonly_security.py::TestReadOnlyPermissions::test_read_count_documents

# Afficher seulement les tests qui échouent
docker compose run --rm tests pytest -v --tb=short

# Mode très détaillé
docker compose run --rm tests pytest -vv

# Arrêter au premier échec
docker compose run --rm tests pytest -x
```

---

## 📊 Interprétation des Résultats

### ✅ Test Réussi (PASSED)
```
test_readonly_security.py::TestReadOnlyPermissions::test_read_count_documents PASSED
```
Le test a réussi comme prévu.

### ❌ Test Échoué (FAILED)
```
test_readonly_security.py::TestReadOnlyPermissions::test_insert_should_fail FAILED
```
Le test a échoué - nécessite une investigation.

### ⚠️ Test Ignoré (SKIPPED)
```
test_readonly_security.py::TestReadOnlyPermissions::test_optional SKIPPED
```
Le test a été ignoré (condition non remplie).

---

## 🔧 Structure des Tests

### Fixtures
Les fixtures sont des fonctions qui préparent l'environnement de test :

```python
@pytest.fixture(scope="module")
def mongodb_connection():
    """Fixture pour la connexion MongoDB."""
    client = MongoClient(mongodb_uri)
    yield client
    client.close()
```

**Scopes disponibles**:
- `function` : Exécuté à chaque test (par défaut)
- `module` : Exécuté une fois par fichier
- `session` : Exécuté une fois pour toute la session

### Classes de Tests
Organisent les tests par thématique :

```python
class TestReadOnlyPermissions:
    """Tests de permissions en lecture seule."""
    
    def test_read_count_documents(self, collection):
        count = collection.count_documents({})
        assert count > 0
```

### Assertions
Vérifient les conditions :

```python
assert count > 0, "La collection devrait contenir des documents"
assert document is not None
assert "not authorized" in str(error)
```

---

## 🛠️ Développement de Nouveaux Tests

### Créer un nouveau fichier de test
```python
# test_my_feature.py
import pytest
from pymongo import MongoClient

@pytest.fixture
def mongodb_connection():
    # Setup
    client = MongoClient("mongodb://...")
    yield client
    # Teardown
    client.close()

def test_my_feature(mongodb_connection):
    """Test de ma fonctionnalité."""
    db = mongodb_connection["test_db"]
    result = db.collection.find_one()
    assert result is not None
```

### Ajouter le test au Dockerfile
```dockerfile
# Dockerfile.tests
COPY test_my_feature.py /app/
```

### Créer un service dans docker-compose.yml
```yaml
my_feature_test:
  build:
    context: .
    dockerfile: Dockerfile.tests
  command: ["pytest", "-v", "-s", "test_my_feature.py"]
  environment:
    MONGODB_URI: mongodb://...
```

---

## 📈 Bonnes Pratiques

1. **Nommage des tests**:
   - Commencer par `test_`
   - Nom descriptif : `test_user_can_read_documents`

2. **Organisation**:
   - Grouper par classes thématiques
   - Un fichier par domaine fonctionnel

3. **Assertions**:
   - Toujours ajouter un message d'erreur
   - `assert value, "Message explicatif"`

4. **Fixtures**:
   - Réutiliser les fixtures communes
   - Nettoyer les ressources (close, drop)

5. **Prints**:
   - Ajouter des prints pour tracer l'exécution
   - Utiliser `-s` pour les voir

---

## 🐛 Dépannage

### Erreur "Connection refused"
```bash
# Vérifier que MongoDB est démarré
docker compose ps

# Redémarrer MongoDB
docker compose up -d mongodb
```

### Erreur "Authentication failed"
```bash
# Vérifier que les utilisateurs sont créés
.\create-users.ps1
```

### Tests qui échouent de manière aléatoire
```bash
# Nettoyer et redémarrer
docker compose down -v
docker compose up -d mongodb
.\create-users.ps1
docker compose run --rm import_scripts
```

### Voir plus de détails sur un échec
```bash
docker compose run --rm tests pytest -vv --tb=long
```

---

## 📚 Ressources

- [Documentation Pytest](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

---

## ✅ Checklist Avant Commit

- [ ] Tous les tests passent
- [ ] Nouveaux tests ajoutés pour les nouvelles fonctionnalités
- [ ] Messages d'erreur descriptifs
- [ ] Fixtures nettoyées (close, drop)
- [ ] Documentation mise à jour
