# Liens Github et Google Drive - P8

## Liens Github
- https://github.com/merais/formation/tree/main/P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul/_projet

## Google Drive
- https://drive.google.com/drive/folders/1BZqY8X9KqZ5nLmN3Pq4RsT6Uv7Wx8Yz9?usp=drive_link

## URLs des services AWS déployés

### CloudWatch Logs
- **Log Group**: `/ecs/p8-etl-cluster`
- **URL CloudWatch**: https://eu-west-3.console.aws.amazon.com/cloudwatch/home?region=eu-west-3#logsV2:log-groups/log-group/$252Fecs$252Fp8-etl-cluster

### Mongo Express (Interface Web MongoDB)
- **URL Application**: http://p8-alb-1867878392.eu-west-3.elb.amazonaws.com:8081
- **Username**: admin
- **Password**: [Voir AWS Secrets Manager - mongo-express-credentials]

### Services ECS
- **Cluster**: p8-etl-cluster
- **Région**: eu-west-3 (Paris)
- **Services**:
  - `mongo-express-service` - Interface web MongoDB
  - `mongodb-service` - Base de données MongoDB
  - `etl-service` - Pipeline ETL
  - `import-service` - Import automatique vers MongoDB

### Commandes pour relancer les services

#### Via AWS CLI
```bash
# Redémarrer tous les services
aws ecs update-service --cluster p8-etl-cluster --service mongo-express-service --force-new-deployment --region eu-west-3
aws ecs update-service --cluster p8-etl-cluster --service mongodb-service --force-new-deployment --region eu-west-3
aws ecs update-service --cluster p8-etl-cluster --service etl-service --force-new-deployment --region eu-west-3
aws ecs update-service --cluster p8-etl-cluster --service import-service --force-new-deployment --region eu-west-3
```

#### Via Console AWS
1. Accéder à ECS: https://eu-west-3.console.aws.amazon.com/ecs/v2/clusters/p8-etl-cluster/services
2. Sélectionner le service
3. Cliquer sur "Update service"
4. Cocher "Force new deployment"
5. Cliquer sur "Update"

## Date de déploiement
- **Dernier déploiement**: 9 décembre 2024
- **Statut**: Services arrêtés (nécessitent redémarrage)
