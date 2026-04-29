"""
Interface de chat Streamlit pour le système RAG Puls-Events.

Ce script fournit une interface web interactive permettant aux utilisateurs de :
- Poser des questions sur les événements culturels en Occitanie
- Visualiser les réponses générées par le système RAG
- Consulter les sources (événements) utilisées pour générer chaque réponse
- Bénéficier d'une gestion de l'historique de conversation

Usage:
    poetry run streamlit run src/rag/chat_interface.py
"""

import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time

# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.rag_system import RAGSystem


# Configuration de la page Streamlit
st.set_page_config(
    page_title="Chatbot Puls-Events",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialisation du système RAG (une seule fois par session)
@st.cache_resource
def initialize_rag_system():
    """
    Initialise le système RAG et le met en cache.
    Cette fonction n'est appelée qu'une fois par session Streamlit.
    
    Returns:
        RAGSystem: Instance initialisée du système RAG
    """
    try:
        with st.spinner("Initialisation du système RAG Puls-Events..."):
            return RAGSystem()
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation : {str(e)}")
        st.stop()


def initialize_session_state():
    """Initialise les variables de session Streamlit."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Bonjour ! Je suis votre assistant pour les événements culturels en Occitanie. "
                      "Posez-moi des questions sur les concerts, expositions, festivals, spectacles et autres événements. "
                      "Comment puis-je vous aider aujourd'hui ?"
        }]
    
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
    
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()


def format_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Formate les sources pour l'affichage dans la sidebar.
    
    Args:
        sources: Liste des documents sources avec métadonnées
        
    Returns:
        String HTML formatée avec les sources
    """
    if not sources:
        return "<i>Aucune source disponible</i>"
    
    html_output = ""
    for source in sources:
        metadata = source.get('metadata', {})
        rank = source.get('rank', '?')
        content = source.get('content', '')
        
        # Extraction des informations principales
        title = metadata.get('title_fr', 'Sans titre')
        date = metadata.get('firstdate_begin', '')
        city = metadata.get('location_city', '')
        region = metadata.get('location_region', '')
        venue = metadata.get('location_name', '')
        
        # Formatage de la date - gérer Timestamp pandas et string
        if date:
            try:
                # Si c'est un Timestamp pandas, le convertir directement
                if hasattr(date, 'strftime'):
                    date_formatted = date.strftime('%d/%m/%Y à %H:%M')
                # Si c'est une string, la parser
                elif isinstance(date, str) and len(date) >= 10:
                    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date_formatted = date_obj.strftime('%d/%m/%Y à %H:%M')
                else:
                    date_formatted = str(date)
            except:
                date_formatted = str(date) if date else "Date non spécifiée"
        else:
            date_formatted = "Date non spécifiée"
        
        # Localisation
        location = f"{city}" if city else (region if region else "Lieu non spécifié")
        if venue:
            location += f" ({venue})"
        
        # Extrait du contenu (première ligne ou 150 caractères)
        if content:
            # Nettoyer et limiter l'extrait
            content_clean = content.replace('\n', ' ').strip()
            if len(content_clean) > 150:
                content_excerpt = content_clean[:150] + "..."
            else:
                content_excerpt = content_clean
        else:
            content_excerpt = "<i>Pas d'extrait disponible</i>"
        
        # Construction de l'entrée source
        html_output += f"""
        <div style="border-left: 3px solid #1f77b4; padding: 10px; margin-bottom: 15px; background-color: #f0f2f6; border-radius: 5px;">
            <p style="margin: 0; font-weight: bold; color: #1f77b4; font-size: 1em;">
                [{rank}] {title}
            </p>
            <p style="margin: 5px 0; font-size: 0.85em; color: #555;">
                📅 {date_formatted}<br>
                📍 {location}
            </p>
            <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #666; font-style: italic;">
                {content_excerpt}
            </p>
        </div>
        """
    
    return html_output


def display_statistics():
    """Affiche les statistiques de la session dans la sidebar."""
    session_duration = (datetime.now() - st.session_state.session_start).total_seconds()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Statistiques de la session")
    st.sidebar.metric("Questions posées", st.session_state.total_queries)
    st.sidebar.metric("Durée de la session", f"{int(session_duration)}s")
    st.sidebar.metric("Messages", len(st.session_state.messages))


def display_help():
    """Affiche l'aide dans la sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exemples de questions")
    st.sidebar.markdown("""
    - *Quels concerts à Toulouse ce mois-ci ?*
    - *Y a-t-il des expositions à Montpellier ?*
    - *Festivals de musique en été en Occitanie*
    - *Spectacles pour enfants à Perpignan*
    - *Événements culturels gratuits*
    """)


def generate_response(rag_system: RAGSystem, prompt: str):
    """
    Génère une réponse à partir du système RAG.
    
    Args:
        rag_system: Instance du système RAG
        prompt: Question de l'utilisateur
    """
    # Ajout du message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Affichage du message utilisateur
    with st.chat_message("user"):
        st.write(prompt)
    
    # Génération de la réponse
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.text("Recherche en cours...")
        
        try:
            # Appel au système RAG avec mesure du temps
            start_time = time.time()
            result = rag_system.query_with_details(prompt)
            response_time = time.time() - start_time
            
            # Vérification des erreurs
            if 'error' in result:
                message_placeholder.error(f"{result['error']}")
                return
            
            # Extraction des données
            answer = result.get('answer', 'Aucune réponse générée')
            sources = result.get('sources', [])
            
            # Affichage de la réponse
            message_placeholder.markdown(answer)
            
            # Affichage des sources directement dans le chat
            if sources:
                with st.expander(f"📚 Sources consultées ({len(sources)} documents)", expanded=False):
                    for idx, source in enumerate(sources, 1):
                        metadata = source.get('metadata', {})
                        rank = source.get('rank', idx)
                        content = source.get('content', '')
                        
                        # Extraction des infos
                        title = metadata.get('title_fr', 'Sans titre')
                        date = metadata.get('firstdate_begin', '')
                        city = metadata.get('location_city', '')
                        venue = metadata.get('location_name', '')
                        
                        # Formatage date - gérer Timestamp pandas et string
                        if date:
                            try:
                                # Si c'est un Timestamp pandas, le convertir directement
                                if hasattr(date, 'strftime'):
                                    date_str = date.strftime('%d/%m/%Y à %H:%M')
                                # Si c'est une string, la parser
                                elif isinstance(date, str) and len(date) >= 10:
                                    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                                    date_str = date_obj.strftime('%d/%m/%Y à %H:%M')
                                else:
                                    date_str = str(date)
                            except:
                                date_str = str(date) if date else "Date non spécifiée"
                        else:
                            date_str = "Date non spécifiée"
                        
                        # Location
                        loc_str = f"{city}" if city else "Lieu non spécifié"
                        if venue:
                            loc_str += f" - {venue}"
                        
                        # Affichage de chaque source
                        st.markdown(f"**[{rank}] {title}**")
                        st.caption(f"📅 {date_str} | 📍 {loc_str}")
                        
                        # Extrait
                        if content:
                            content_clean = content.replace('\n', ' ').strip()
                            excerpt = content_clean[:200] + "..." if len(content_clean) > 200 else content_clean
                            st.text(excerpt)
                        
                        # Séparateur sauf pour le dernier
                        if idx < len(sources):
                            st.markdown("---")
            
            # Affichage du temps de réponse (petit texte)
            st.caption(f"Réponse générée en {response_time:.2f}s")
            
            # Affichage des sources dans la sidebar également
            if sources:
                with st.sidebar:
                    st.markdown("---")
                    st.subheader(f"Dernières sources ({len(sources)})")
                    st.markdown(format_sources(sources), unsafe_allow_html=True)
            
            # Ajout de la réponse à l'historique
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
            
            # Mise à jour des statistiques
            st.session_state.total_queries += 1
            
        except Exception as e:
            message_placeholder.error(f"Erreur lors de la génération : {str(e)}")


def main():
    """Point d'entrée principal de l'application Streamlit."""
    
    # Initialisation
    initialize_session_state()
    rag_system = initialize_rag_system()
    
    # En-tête de l'application
    st.title("🎭 Chatbot Puls-Events")
    st.markdown("**Assistant pour les événements culturels en Occitanie**")
    
    # Sidebar
    with st.sidebar:
        st.header("À propos")
        st.markdown("""
        Ce chatbot vous aide à découvrir les événements culturels en Occitanie :
        - 🎵 Concerts
        - 🎨 Expositions
        - 🎪 Festivals
        - 🎭 Spectacles
        - Et bien plus !
        """)
        
        display_help()
        display_statistics()
        
        # Bouton pour réinitialiser la conversation
        if st.button("Nouvelle conversation", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
            }]
            st.session_state.total_queries = 0
            st.session_state.session_start = datetime.now()
            st.rerun()
    
    # Affichage de l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input utilisateur
    if prompt := st.chat_input("Comment puis-je vous aider ?"):
        generate_response(rag_system, prompt)


if __name__ == "__main__":
    main()
