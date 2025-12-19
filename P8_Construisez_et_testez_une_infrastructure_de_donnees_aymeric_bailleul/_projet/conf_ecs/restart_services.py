#!/usr/bin/env python3
"""
Script pour redémarrer les services AWS ECS du cluster weather-pipeline
Alternative à AWS CLI en utilisant boto3
"""

import boto3
import os
import sys
from typing import List

# Configuration
REGION = "eu-west-1"
CLUSTER_NAME = "weather-pipeline-cluster"
SERVICES = ["mongodb", "mongo-express", "weather-etl", "mongodb-importer", "s3-cleanup"]

# Credentials depuis .env
AWS_ACCESS_KEY_ID = "AKIAU74V2YN4QRLU3TNJ"
AWS_SECRET_ACCESS_KEY = "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"


def get_ecs_client():
    """Créer un client ECS avec les credentials"""
    return boto3.client(
        'ecs',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )


def resume_services(services: List[str] = SERVICES):
    """Redémarrer tous les services (desired_count=1)"""
    client = get_ecs_client()
    
    print("\n▶️  REDÉMARRAGE DES SERVICES")
    print("=" * 50)
    
    for service in services:
        try:
            print(f"  ▶️  Démarrage de {service}...")
            response = client.update_service(
                cluster=CLUSTER_NAME,
                service=service,
                desiredCount=1
            )
            print(f"    ✓ {service} redémarré (desired=1)")
        except Exception as e:
            print(f"    ✗ Erreur pour {service}: {str(e)}")
    
    print("\n✅ Cluster redémarré")
    print("\n⏳ Attendre 1-2 minutes pour que tous les services soient opérationnels")


def pause_services(services: List[str] = SERVICES):
    """Mettre en pause tous les services (desired_count=0)"""
    client = get_ecs_client()
    
    print("\n⏸️  MISE EN PAUSE DES SERVICES")
    print("=" * 50)
    
    for service in services:
        try:
            print(f"  ⏸️  Arrêt de {service}...")
            response = client.update_service(
                cluster=CLUSTER_NAME,
                service=service,
                desiredCount=0
            )
            print(f"    ✓ {service} mis en pause (desired=0)")
        except Exception as e:
            print(f"    ✗ Erreur pour {service}: {str(e)}")
    
    print("\n✅ Cluster mis en pause - Facturation arrêtée")


def get_status(services: List[str] = SERVICES):
    """Afficher l'état des services"""
    client = get_ecs_client()
    
    print("\n📊 ÉTAT DU CLUSTER")
    print("=" * 50)
    print(f"{'Service':<20} {'Status':<12} {'Running':<8} {'Desired':<8}")
    print("-" * 50)
    
    try:
        response = client.describe_services(
            cluster=CLUSTER_NAME,
            services=services
        )
        
        total_running = 0
        for service in response['services']:
            name = service['serviceName']
            status = service['status']
            running = service['runningCount']
            desired = service['desiredCount']
            total_running += running
            print(f"{name:<20} {status:<12} {running:<8} {desired:<8}")
        
        print("\n💰 Estimation des coûts:")
        if total_running == 0:
            print("   ✓ Cluster en pause - Pas de facturation Fargate")
        else:
            monthly_cost = round(total_running * 0.04 * 24 * 30, 2)
            print(f"   ⚠️  {total_running} tâche(s) en cours")
            print(f"   → ~{monthly_cost} USD/mois (estimation)")
            
    except Exception as e:
        print(f"\n✗ Erreur: {str(e)}")


def get_mongo_express_url():
    """Récupérer l'IP publique de Mongo Express"""
    client = get_ecs_client()
    ec2_client = boto3.client(
        'ec2',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    try:
        # Récupérer les tâches du service mongo-express
        response = client.list_tasks(
            cluster=CLUSTER_NAME,
            serviceName='mongo-express',
            desiredStatus='RUNNING'
        )
        
        if not response['taskArns']:
            print("\n⚠️  Aucune tâche mongo-express en cours")
            print("   Dernière URL connue: http://52.210.5.234:8081")
            return None
        
        # Récupérer les détails de la tâche
        task_details = client.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=response['taskArns']
        )
        
        for task in task_details['tasks']:
            for attachment in task['attachments']:
                if attachment['type'] == 'ElasticNetworkInterface':
                    for detail in attachment['details']:
                        if detail['name'] == 'networkInterfaceId':
                            eni_id = detail['value']
                            
                            # Récupérer l'IP publique de l'ENI
                            eni_response = ec2_client.describe_network_interfaces(
                                NetworkInterfaceIds=[eni_id]
                            )
                            
                            if eni_response['NetworkInterfaces']:
                                association = eni_response['NetworkInterfaces'][0].get('Association', {})
                                public_ip = association.get('PublicIp')
                                
                                if public_ip:
                                    url = f"http://{public_ip}:8081"
                                    print(f"\n🌐 Mongo Express URL: {url}")
                                    print(f"   Username: admin")
                                    print(f"   Password: pass")
                                    return url
        
        print("\n⚠️  IP publique non trouvée")
        print("   Dernière URL connue: http://52.210.5.234:8081")
        return None
        
    except Exception as e:
        print(f"\n✗ Erreur lors de la récupération de l'URL: {str(e)}")
        print("   Dernière URL connue: http://52.210.5.234:8081")
        return None


def get_cloudwatch_urls():
    """Afficher les URLs CloudWatch"""
    print("\n📊 CLOUDWATCH LOGS")
    print("=" * 50)
    
    base_url = f"https://{REGION}.console.aws.amazon.com/cloudwatch/home?region={REGION}#logsV2:log-groups"
    
    logs = [
        "/ecs/weather-mongodb",
        "/ecs/weather-mongo-express",
        "/ecs/weather-etl",
        "/ecs/weather-importer",
        "/ecs/weather-s3-cleanup"
    ]
    
    for log_group in logs:
        encoded_log = log_group.replace("/", "$252F")
        url = f"{base_url}/log-group/{encoded_log}"
        print(f"\n{log_group}:")
        print(f"   {url}")
    
    # Dashboard
    print("\n\n📈 CLOUDWATCH DASHBOARD")
    print("=" * 50)
    dashboard_url = f"https://{REGION}.console.aws.amazon.com/cloudwatch/home?region={REGION}#dashboards:name=weather-pipeline"
    print(f"\n   {dashboard_url}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python restart_services.py resume    - Redémarrer tous les services")
        print("  python restart_services.py pause     - Mettre en pause tous les services")
        print("  python restart_services.py status    - Afficher l'état")
        print("  python restart_services.py urls      - Afficher les URLs")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "resume":
        resume_services()
        get_mongo_express_url()
    elif action == "pause":
        pause_services()
    elif action == "status":
        get_status()
    elif action == "urls":
        get_mongo_express_url()
        get_cloudwatch_urls()
    else:
        print(f"Action inconnue: {action}")
        sys.exit(1)
