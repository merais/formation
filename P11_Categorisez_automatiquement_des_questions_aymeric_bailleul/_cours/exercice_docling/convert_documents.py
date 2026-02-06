"""
Script de conversion de documents municipaux avec Docling
Ce script parcourt un répertoire de documents et les convertit en Markdown
"""

import os
from pathlib import Path
from docling.document_converter import DocumentConverter

def setup_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas"""
    source_dir = Path("sources/RAW")
    output_dir = Path("sources/convert")
    
    source_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return source_dir, output_dir

def get_supported_files(directory):
    """
    Parcourt le répertoire et retourne la liste des fichiers supportés
    
    Args:
        directory: Chemin du répertoire à parcourir
        
    Returns:
        Liste des chemins de fichiers supportés
    """
    supported_extensions = {
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', 
        '.pptx', '.ppt', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
    }
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            file_path = Path(root) / filename
            if file_path.suffix.lower() in supported_extensions:
                files.append(file_path)
    
    return files

def convert_document(file_path, output_dir, converter):
    """
    Convertit un document en Markdown
    
    Args:
        file_path: Chemin du fichier source
        output_dir: Répertoire de sortie
        converter: Instance de DocumentConverter
    """
    try:
        print(f"Conversion en cours : {file_path.name}")
        
        # Conversion du document
        result = converter.convert(str(file_path))
        
        # Génération du nom de fichier de sortie
        output_filename = file_path.stem + ".md"
        output_path = output_dir / output_filename
        
        # Sauvegarde du résultat en Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_markdown())
        
        print(f"Converti avec succès : {output_filename}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la conversion de {file_path.name} : {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("Conversion de documents municipaux avec Docling")
    print("=" * 60)
    print()
    
    # Configuration des répertoires
    source_dir, output_dir = setup_directories()
    
    # Vérification de l'existence de documents source
    if not any(source_dir.iterdir()):
        print("Aucun document trouvé dans le dossier 'sources/RAW/'")
        print("Veuillez y placer vos documents à convertir.")
        return
    
    # Récupération des fichiers supportés
    files = get_supported_files(source_dir)
    
    if not files:
        print("Aucun fichier supporté trouvé dans 'sources/RAW/'")
        print("Formats supportés : PDF, Word, Excel, PowerPoint, Images")
        return
    
    print(f"Fichiers trouvés : {len(files)}")
    print()
    
    # Initialisation du convertisseur Docling
    converter = DocumentConverter()
    
    # Conversion de chaque fichier
    success_count = 0
    for file_path in files:
        if convert_document(file_path, output_dir, converter):
            success_count += 1
    
    # Résumé
    print()
    print("=" * 60)
    print(f"Conversion terminée : {success_count}/{len(files)} fichiers convertis")
    print(f"Fichiers Markdown disponibles dans : {output_dir.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
