"""
Producteur de tickets clients pour Redpanda
Génère des tickets aléatoires et les envoie au topic 'client_tickets'
"""
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

# Configuration
KAFKA_BROKER = 'redpanda:29092'
TOPIC_NAME = 'client_tickets'
fake = Faker('fr_FR')

# Types de demandes et priorités
TYPES_DEMANDE = [
    'Technique',
    'Facturation',
    'Commercial',
    'Support',
    'Réclamation'
]

PRIORITES = ['Basse', 'Moyenne', 'Haute', 'Critique']

DEMANDES_EXEMPLES = {
    'Technique': [
        'Impossible de se connecter à mon compte',
        'Erreur lors du téléchargement',
        'Le site est lent',
        'Problème d\'affichage sur mobile',
        'Fonctionnalité ne répond pas'
    ],
    'Facturation': [
        'Question sur ma facture du mois dernier',
        'Erreur de montant facturé',
        'Demande de remboursement',
        'Changement de mode de paiement',
        'Facture non reçue'
    ],
    'Commercial': [
        'Demande de devis',
        'Information sur les tarifs',
        'Upgrade de forfait',
        'Résiliation de contrat',
        'Proposition de partenariat'
    ],
    'Support': [
        'Comment utiliser la fonctionnalité X ?',
        'Besoin d\'aide pour configurer',
        'Documentation manquante',
        'Tutoriel vidéo disponible ?',
        'Formation à distance possible ?'
    ],
    'Réclamation': [
        'Service non conforme',
        'Délai de livraison non respecté',
        'Qualité insuffisante',
        'Non-respect des engagements',
        'Demande de dédommagement'
    ]
}


def create_ticket():
    """Génère un ticket client aléatoire"""
    ticket_id = fake.uuid4()
    client_id = f"CLI-{random.randint(1000, 9999)}"
    type_demande = random.choice(TYPES_DEMANDE)
    demande = random.choice(DEMANDES_EXEMPLES[type_demande])
    priorite = random.choice(PRIORITES)
    
    ticket = {
        'ticket_id': ticket_id,
        'client_id': client_id,
        'date_creation': datetime.now().isoformat(),
        'demande': demande,
        'type_demande': type_demande,
        'priorite': priorite
    }
    
    return ticket


def main():
    """Fonction principale pour produire des tickets"""
    print(f"Démarrage du producteur de tickets...")
    print(f"Connexion à Kafka: {KAFKA_BROKER}")
    print(f"Topic: {TOPIC_NAME}")
    
    # Attendre que Redpanda soit prêt
    time.sleep(10)
    
    # Créer le producteur Kafka
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 2)
    )
    
    print("Producteur connecté avec succès!")
    print("Génération de tickets en cours...\n")
    
    ticket_count = 0
    
    try:
        while True:
            # Créer un ticket
            ticket = create_ticket()
            
            # Envoyer au topic
            producer.send(TOPIC_NAME, value=ticket)
            
            ticket_count += 1
            print(f"Ticket #{ticket_count} envoyé: {ticket['type_demande']} - {ticket['priorite']} - Client: {ticket['client_id']}")
            
            # Attendre entre 1 et 5 secondes avant le prochain ticket
            time.sleep(random.uniform(1, 5))
            
    except KeyboardInterrupt:
        print("\nArrêt du producteur...")
    finally:
        producer.close()
        print(f"Total de tickets envoyés: {ticket_count}")
        print("Producteur arrêté")


if __name__ == "__main__":
    main()
