"""
Script de reconstruction complète de la base vectorielle.

Ce script orchestre toutes les étapes du pipeline de création de la base
vectorielle, de la collecte des données brutes jusqu'à l'index FAISS final.

Usage:
    python src/build_vectorstore.py

Étapes exécutées:
    1. Nettoyage des données (clean_data.py)
    2. Découpage en chunks (chunk_texts.py)
    3. Vectorisation avec Mistral (vectorize_data.py)
    4. Création de l'index FAISS (create_faiss_index.py)

Prérequis:
    - Fichier data/raw/evenements-publics-openagenda.parquet présent
    - Variable d'environnement MISTRAL_API_KEY configurée
    - Environnement virtuel activé avec toutes les dépendances
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

# Forcer UTF-8 sur stdout/stderr (evite UnicodeEncodeError sur Windows cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================================
# CONSTANTES
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS = [
    {
        "name": "Nettoyage des données",
        "script": "src/preprocessing/clean_data.py",
        "description": "Filtrage géographique/temporel, nettoyage HTML, création text_for_rag"
    },
    {
        "name": "Découpage en chunks",
        "script": "src/preprocessing/chunk_texts.py",
        "description": "Création de chunks de 250 tokens avec 75 tokens d'overlap"
    },
    {
        "name": "Vectorisation Mistral",
        "script": "src/vectorization/vectorize_data.py",
        "description": "Génération des embeddings 1024D avec mistral-embed"
    },
    {
        "name": "Création index FAISS",
        "script": "src/vectorization/create_faiss_index.py",
        "description": "Indexation des vecteurs avec IndexFlatIP"
    }
]


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def print_header(text: str) -> None:
    """Affiche un en-tête formaté."""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")


def print_step(step_num: int, total: int, name: str, description: str) -> None:
    """Affiche les informations d'une étape."""
    print(f"\n{'─'*80}")
    print(f"ÉTAPE {step_num}/{total} : {name}")
    print(f"{'─'*80}")
    print(f"Description : {description}")
    print(f"Début : {datetime.now().strftime('%H:%M:%S')}\n")


def check_prerequisites() -> bool:
    """
    Vérifie que tous les prérequis sont satisfaits.
    
    Returns:
        bool: True si tous les prérequis sont OK
    """
    print_header("VÉRIFICATION DES PRÉREQUIS")
    
    all_ok = True
    
    # 1. Vérifier le fichier de données brutes
    raw_data = PROJECT_ROOT / "data" / "raw" / "evenements-publics-openagenda.parquet"
    if raw_data.exists():
        size_mb = raw_data.stat().st_size / 1024 / 1024
        print(f"[OK] Données brutes présentes : {raw_data.name} ({size_mb:.2f} MB)")
    else:
        print(f"[ERREUR] Fichier de données brutes introuvable : {raw_data}")
        all_ok = False
    
    # 2. Vérifier le fichier .env
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        print(f"[OK] Fichier .env présent")
        # Vérifier que MISTRAL_API_KEY est définie
        with open(env_file, 'r') as f:
            content = f.read()
            if 'MISTRAL_API_KEY' in content:
                print(f"[OK] Variable MISTRAL_API_KEY configurée")
            else:
                print(f"[ERREUR] MISTRAL_API_KEY non trouvée dans .env")
                all_ok = False
    else:
        print(f"[ERREUR] Fichier .env introuvable : {env_file}")
        all_ok = False
    
    # 3. Vérifier que les scripts existent
    print(f"\nVérification des scripts:")
    for step in SCRIPTS:
        script_path = PROJECT_ROOT / step["script"]
        if script_path.exists():
            print(f"   [OK] {step['script']}")
        else:
            print(f"   [ERREUR] Script introuvable : {step['script']}")
            all_ok = False
    
    # 4. Vérifier Python
    print(f"\nVersion Python : {sys.version.split()[0]}")
    
    return all_ok


def run_script(script_path: Path) -> tuple[bool, float]:
    """
    Exécute un script Python et retourne le statut.
    
    Args:
        script_path: Chemin vers le script à exécuter
    
    Returns:
        tuple: (succès: bool, durée: float en secondes)
    """
    start_time = time.time()
    
    try:
        # Exécuter le script avec le même interpréteur Python
        # -u : mode unbuffered pour affichage en temps réel même dans un pipe
        result = subprocess.run(
            [sys.executable, "-u", str(script_path)],
            cwd=PROJECT_ROOT,
            capture_output=False,  # Afficher la sortie en direct
            text=True,
            check=True
        )
        
        elapsed = time.time() - start_time
        return True, elapsed
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n[ERREUR] Erreur lors de l'exécution du script")
        print(f"   Code de sortie : {e.returncode}")
        return False, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERREUR] Erreur inattendue : {e}")
        return False, elapsed


def format_duration(seconds: float) -> str:
    """Formate une durée en secondes de manière lisible."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """
    Fonction principale : orchestre la reconstruction complète.
    """
    print_header("RECONSTRUCTION DE LA BASE VECTORIELLE")
    print(f"Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Répertoire : {PROJECT_ROOT}")
    
    overall_start = time.time()
    
    # 1. Vérifier les prérequis
    if not check_prerequisites():
        print("\n[ERREUR] Prérequis non satisfaits. Arrêt du pipeline.")
        sys.exit(1)
    
    # 2. Exécuter chaque étape
    results = []
    total_steps = len(SCRIPTS)
    
    for i, step in enumerate(SCRIPTS, start=1):
        print_step(i, total_steps, step["name"], step["description"])
        
        script_path = PROJECT_ROOT / step["script"]
        success, duration = run_script(script_path)
        
        results.append({
            "name": step["name"],
            "success": success,
            "duration": duration
        })
        
        if success:
            print(f"\n[OK] Étape {i}/{total_steps} terminée avec succès")
            print(f"Durée : {format_duration(duration)}")
        else:
            print(f"\n[ERREUR] Étape {i}/{total_steps} échouée")
            print(f"Durée : {format_duration(duration)}")
            print(f"\n[ATTENTION] Le pipeline s'arrête suite à l'erreur.")
            break
    
    # 3. Résumé final
    overall_duration = time.time() - overall_start
    
    print_header("RÉSUMÉ DE LA RECONSTRUCTION")
    
    print("Résultats par étape :\n")
    for i, result in enumerate(results, start=1):
        status = "[OK] Succès" if result["success"] else "[ERREUR] Échec"
        duration = format_duration(result["duration"])
        print(f"   {i}. {result['name']:.<60} {status} ({duration})")
    
    # Statistiques globales
    total_success = sum(1 for r in results if r["success"])
    total_failed = len(results) - total_success
    
    print(f"\nStatistiques :")
    print(f"   - Étapes complétées : {total_success}/{total_steps}")
    print(f"   - Étapes échouées : {total_failed}")
    print(f"   - Durée totale : {format_duration(overall_duration)}")
    print(f"   - Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 4. Vérifier les fichiers générés
    if total_success == total_steps:
        print("\nFichiers générés :")
        
        files_to_check = [
            ("data/processed/evenements_occitanie_clean.parquet", "Données nettoyées"),
            ("data/processed/evenements_chunks.parquet", "Chunks"),
            ("data/vectorstore/embeddings.npy", "Embeddings"),
            ("data/vectorstore/metadata.parquet", "Métadonnées"),
            ("data/vectorstore/faiss_index.bin", "Index FAISS"),
            ("data/vectorstore/config.txt", "Configuration embeddings"),
            ("data/vectorstore/index_config.txt", "Configuration index")
        ]
        
        all_files_ok = True
        for file_path, description in files_to_check:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                size_mb = full_path.stat().st_size / 1024 / 1024
                print(f"   [OK] {description:.<50} {size_mb:>8.2f} MB")
            else:
                print(f"   [MANQUANT] {description:.<50} MANQUANT")
                all_files_ok = False
        
        if all_files_ok:
            print("\n" + "="*80)
            print("[SUCCÈS] RECONSTRUCTION TERMINÉE AVEC SUCCÈS".center(80))
            print("="*80)
            return 0
        else:
            print("\n[ATTENTION] Certains fichiers sont manquants.")
            return 1
    else:
        print("\n" + "="*80)
        print("[ÉCHEC] RECONSTRUCTION ÉCHOUÉE".center(80))
        print("="*80)
        print("\nVérifiez les erreurs ci-dessus et réessayez.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTION] Reconstruction interrompue par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERREUR FATALE] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
