# 🔍 Comment Vérifier le Déploiement dans AWS Console

## 📊 Résumé Rapide (via CLI)

### État Actuel de Votre Déploiement

```
=== SERVICES ECS ===
✅ mongodb          : 1/1 RUNNING
✅ mongo-express    : 1/1 RUNNING  
⚠️ mongodb-importer : 0/1 (démarrage en cours)
⚠️ s3-cleanup       : 0/1 (démarrage en cours)

Cluster: 1 tâche running, 3 pending, 4 services actifs
```

---

## 🌐 Vérification via AWS Console (Interface Web)

### 1️⃣ Accéder à ECS (Elastic Container Service)

**URL directe :** https://eu-west-1.console.aws.amazon.com/ecs/v2/clusters

**OU Navigation manuelle :**
1. Connectez-vous à https://console.aws.amazon.com
2. Région : **Europe (Ireland) eu-west-1** (en haut à droite)
3. Services → Containers → **Elastic Container Service**

### 2️⃣ Vérifier le Cluster

1. Cliquez sur **weather-pipeline-cluster**
2. Vous devriez voir :
   - **Status:** ACTIVE ✅
   - **Services:** 4 actifs
   - **Tasks:** 1-4 en cours d'exécution

**Onglets à vérifier :**

#### **📋 Services Tab**
- `mongodb` : ACTIVE, Desired: 1, Running: 1 ✅
- `mongo-express` : ACTIVE, Desired: 1, Running: 1 ✅
- `mongodb-importer` : ACTIVE, Desired: 1, Running: 0-1 ⚠️
- `s3-cleanup` : ACTIVE, Desired: 1, Running: 0-1 ⚠️

#### **📦 Tasks Tab**
Vous devriez voir 1-4 tâches avec :
- **Last status:** RUNNING ✅
- **Desired status:** RUNNING
- **Health status:** HEALTHY (après quelques minutes)

Cliquez sur une tâche pour voir :
- Logs (lien direct vers CloudWatch)
- Network bindings (IP publique pour mongo-express)
- Container details

#### **🔗 Networking Tab**
- VPC: weather-pipeline-vpc
- Subnets: 4 (2 public, 2 private)
- Security groups: weather-pipeline-ecs-sg

---

### 3️⃣ Vérifier CloudFormation

**URL directe :** https://eu-west-1.console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks

**Ce que vous devriez voir :**

| Stack Name | Status | Created |
|------------|--------|---------|
| **weather-pipeline-vpc** | ✅ CREATE_COMPLETE | 2025-12-09 09:14 |
| **weather-pipeline-iam** | ✅ UPDATE_COMPLETE | 2025-12-09 08:58 |

**Détails à vérifier pour weather-pipeline-vpc :**
1. Onglet **Resources** (28 ressources) :
   - VPC
   - InternetGateway
   - NatGateway
   - 4 Subnets (2 public, 2 private)
   - Route Tables
   - Security Groups (ECS, EFS)

2. Onglet **Outputs** :
   - VPCId
   - PublicSubnet1, PublicSubnet2
   - PrivateSubnet1, PrivateSubnet2
   - ECSSecurityGroup
   - EFSSecurityGroup

---

### 4️⃣ Vérifier EFS (Elastic File System)

**URL directe :** https://eu-west-1.console.aws.amazon.com/efs/home?region=eu-west-1#/file-systems

**Ce que vous devriez voir :**
- **File system ID:** fs-0e949e0f67c2d330d
- **Name:** weather-pipeline-efs
- **State:** ✅ Available
- **Metered size:** ~6 KB (augmente avec les données MongoDB)

**Détails à vérifier :**
1. Onglet **Network** :
   - 2 mount targets (un dans chaque subnet privé)
   - State: Available ✅

2. Onglet **Access points** :
   - **fsap-0a27d89ed9744cc06** (pour MongoDB)
   - Path: /mongodb
   - POSIX user: UID 999, GID 999

---

### 5️⃣ Vérifier Secrets Manager

**URL directe :** https://eu-west-1.console.aws.amazon.com/secretsmanager/home?region=eu-west-1#!/listSecrets/

**Secrets créés (4) :**
- ✅ `weather-pipeline/aws-credentials`
- ✅ `weather-pipeline/mongodb-credentials`
- ✅ `weather-pipeline/mongo-express-credentials`
- ✅ `weather-pipeline/s3-config`

**Vérification :**
1. Cliquez sur un secret
2. Onglet **Secret value** → **Retrieve secret value**
3. Vérifiez que les clés/valeurs sont correctes

---

### 6️⃣ Vérifier ECR (Container Registry)

**URL directe :** https://eu-west-1.console.aws.amazon.com/ecr/repositories?region=eu-west-1

**Repositories créés (2) :**
- ✅ `weather-etl` (1 image)
- ✅ `weather-mongodb` (1 image)

**Détails à vérifier :**
1. Cliquez sur un repository
2. Vous devriez voir une image avec tag **latest**
3. Image scan status: Complete
4. Size: ~100-500 MB

---

### 7️⃣ Vérifier CloudWatch Logs

**URL directe :** https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1#logsV2:log-groups

**Log groups créés :**
- `/ecs/weather-mongodb` ✅
- `/ecs/weather-mongo-express` ✅
- `/ecs/weather-etl` (si exécuté)
- `/ecs/weather-importer` (si démarré)
- `/ecs/weather-s3-cleanup` (si démarré)

**Voir les logs en direct :**
1. Cliquez sur un log group (ex: `/ecs/weather-mongodb`)
2. Cliquez sur le log stream le plus récent
3. Vous devriez voir les logs de démarrage MongoDB

**Logs attendus pour MongoDB :**
```
MongoDB starting...
Waiting for connections on port 27017
```

---

### 8️⃣ Vérifier VPC

**URL directe :** https://eu-west-1.console.aws.amazon.com/vpc/home?region=eu-west-1#vpcs:

**VPC créé :**
- **Name:** weather-pipeline-vpc
- **VPC ID:** vpc-xxx...
- **CIDR:** 10.0.0.0/16
- **State:** ✅ Available

**Détails à vérifier :**

#### **Subnets (4) :**
- `weather-pipeline-public-subnet-1` : 10.0.1.0/24, eu-west-1a
- `weather-pipeline-public-subnet-2` : 10.0.2.0/24, eu-west-1b
- `weather-pipeline-private-subnet-1` : 10.0.10.0/24, eu-west-1a
- `weather-pipeline-private-subnet-2` : 10.0.11.0/24, eu-west-1b

#### **Security Groups (2) :**
- `weather-pipeline-ecs-sg` :
  - Inbound: Port 8081 (Mongo Express), Port 27017 (MongoDB inter-containers)
  - Outbound: All traffic
  
- `weather-pipeline-efs-sg` :
  - Inbound: Port 2049 (NFS) from ECS security group

#### **NAT Gateway :**
- **Name:** weather-pipeline-nat
- **State:** ✅ Available
- **Elastic IP:** Attached
- Permet aux containers privés d'accéder à Internet

---

## 🎯 Accéder à Mongo Express

### Méthode 1 : Via AWS Console

1. ECS → Clusters → weather-pipeline-cluster
2. Onglet **Tasks**
3. Cliquez sur la tâche **mongo-express**
4. Section **Network bindings** ou **Configuration**
5. Cherchez **Public IP** (ex: 52.210.5.234)
6. Accédez à : `http://[IP_PUBLIQUE]:8081`

### Méthode 2 : Via CLI (plus rapide)

```powershell
# Déjà exécuté, l'IP est visible dans les résultats ci-dessus
# Ou relancez :
.\check-mongo-express-ip.ps1
```

### Méthode 3 : Via EC2 Console

1. EC2 → Network Interfaces
2. Filtrez par "weather-pipeline"
3. Trouvez l'ENI avec "mongo-express" dans la description
4. Copiez l'**IPv4 Public IP**

---

## 🔍 Diagnostic des Problèmes

### Si un service ne démarre pas :

1. **ECS → Services → [nom_service]**
2. Onglet **Events** : Voir les 10 derniers événements
3. Messages courants :
   - ✅ "has reached a steady state" = OK
   - ⚠️ "was unable to place a task" = Problème de ressources/permissions
   - ❌ "Essential container... exited" = Erreur applicative

### Vérifier les logs d'une tâche en erreur :

1. ECS → Tasks → Cliquez sur la tâche qui a échoué
2. Onglet **Logs** (lien direct vers CloudWatch)
3. Analysez les dernières lignes

### Problèmes fréquents :

| Erreur | Solution |
|--------|----------|
| `AccessDeniedException: logs:CreateLogGroup` | IAM role manque permissions CloudWatch → Corriger iam-roles.yaml |
| `No such file or directory` (EFS) | Utiliser Access Point EFS avec Path pré-créé |
| `ResourceNotFoundException` (Secret) | Vérifier nom du secret dans Secrets Manager |
| `CannotPullContainerError` | Vérifier que l'image existe dans ECR |

---

## 📈 Métriques et Monitoring

### CloudWatch Metrics

**URL :** https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1#metricsV2:

**Métriques à surveiller :**
- **ECS/ClusterName** :
  - CPUUtilization (cible: < 70%)
  - MemoryUtilization (cible: < 80%)
  - RunningTasksCount

- **EFS** :
  - BurstCreditBalance
  - TotalIOBytes

### Créer des Alarms CloudWatch

1. CloudWatch → Alarms → Create alarm
2. Sélectionnez une métrique (ex: ECS CPUUtilization)
3. Définissez le seuil (ex: > 80%)
4. Configurez SNS pour recevoir des emails

---

## ✅ Checklist de Vérification

Cochez chaque élément pour confirmer le déploiement :

- [ ] **Cluster ECS** : ACTIVE avec 4 services
- [ ] **Service mongodb** : 1/1 RUNNING
- [ ] **Service mongo-express** : 1/1 RUNNING, IP publique accessible
- [ ] **CloudFormation** : 2 stacks CREATE_COMPLETE/UPDATE_COMPLETE
- [ ] **EFS** : Available avec 2 mount targets et 1 access point
- [ ] **Secrets Manager** : 4 secrets créés
- [ ] **ECR** : 2 repositories avec images latest
- [ ] **CloudWatch Logs** : Logs visibles pour mongodb et mongo-express
- [ ] **VPC** : Créé avec subnets, NAT Gateway, Security Groups
- [ ] **Mongo Express accessible** : http://[IP]:8081 répond

---

## 🚀 Commandes Rapides de Vérification

```powershell
# État complet
aws ecs describe-services \
  --cluster weather-pipeline-cluster \
  --services mongodb mongo-express mongodb-importer s3-cleanup \
  --region eu-west-1 \
  --query 'services[*].[serviceName,status,runningCount,desiredCount]' \
  --output table

# Logs en temps réel MongoDB
aws logs tail /ecs/weather-mongodb --follow --region eu-west-1

# Événements récents d'un service
aws ecs describe-services \
  --cluster weather-pipeline-cluster \
  --services mongodb \
  --region eu-west-1 \
  --query 'services[0].events[0:5]'

# Liste des tâches
aws ecs list-tasks --cluster weather-pipeline-cluster --region eu-west-1

# Détails d'une tâche
aws ecs describe-tasks \
  --cluster weather-pipeline-cluster \
  --tasks [TASK_ARN] \
  --region eu-west-1
```

---

## 📞 Support

Si quelque chose ne fonctionne pas :
1. Vérifiez les **Events** du service dans ECS Console
2. Consultez les **CloudWatch Logs**
3. Vérifiez les **CloudFormation Stack Events** pour les erreurs de déploiement
4. Relancez le script deploy.ps1 si nécessaire

**Dernière vérification :** 9 décembre 2025, 10:35 CET
