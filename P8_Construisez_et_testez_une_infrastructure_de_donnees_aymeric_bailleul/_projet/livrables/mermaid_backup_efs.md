```mermaid
flowchart TB
    subgraph ECS["AWS ECS Fargate"]
        MongoDB[MongoDB Container<br/>0.5 vCPU, 1GB RAM<br/>Port: 27017]
    end
    
    subgraph EFS["Amazon EFS - Multi-AZ"]
        Volume[(EFS File System<br/>fs-xxxxx<br/>/data/db<br/>~5 GB)]
        
        subgraph Zone1["AZ eu-west-1a"]
            Replica1[(Réplica 1)]
        end
        
        subgraph Zone2["AZ eu-west-1b"]
            Replica2[(Réplica 2)]
        end
    end
    
    subgraph Backup["AWS Backup Service"]
        Plan[Backup Plan<br/>Quotidien 3h AM<br/>Rétention: 30 jours]
        
        subgraph Vault["Backup Vault"]
            Snap1[Snapshot J-1<br/>12/12/2025<br/>5.2 GB]
            Snap2[Snapshot J-7<br/>06/12/2025<br/>5.1 GB]
            Snap3[Snapshot J-30<br/>12/11/2025<br/>4.8 GB]
        end
    end
    
    subgraph Restore["Processus de Restauration"]
        RestoreJob[Create Restore Job<br/>Sélection snapshot]
        NewEFS[(Nouveau EFS Volume<br/>fs-yyyyy<br/>Données restaurées)]
        UpdateTask[Mise à jour<br/>Task Definition<br/>Nouveau volume ID]
        RestartService[Redémarrage<br/>Service ECS<br/>mongodb]
    end
    
    %% Flux principal
    MongoDB -->|Mount| Volume
    Volume --> Replica1
    Volume --> Replica2
    
    %% Backup automatique
    Plan -.->|Trigger quotidien| Volume
    Volume -.->|Snapshot incrémental| Snap1
    Snap1 -.->|Rotation| Snap2
    Snap2 -.->|Rotation| Snap3
    Snap3 -.->|Suppression après 30j| Delete[Supprimé]
    
    %% Restauration
    Snap1 -->|Sélection| RestoreJob
    Snap2 -->|ou| RestoreJob
    Snap3 -->|ou| RestoreJob
    RestoreJob -->|Restauration| NewEFS
    NewEFS --> UpdateTask
    UpdateTask --> RestartService
    RestartService -.->|Nouveau mount| MongoDB
    
    %% Styles
    classDef container fill:#3498DB,stroke:#2874A6,stroke-width:2px,color:#fff
    classDef storage fill:#9B59B6,stroke:#7D3C98,stroke-width:2px,color:#fff
    classDef backup fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
    classDef restore fill:#F39C12,stroke:#D68910,stroke-width:2px,color:#fff
    classDef delete fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    
    class MongoDB container
    class Volume,Replica1,Replica2,NewEFS storage
    class Plan,Snap1,Snap2,Snap3 backup
    class RestoreJob,UpdateTask,RestartService restore
    class Delete delete
```

## 📋 Configuration AWS Backup

**Création du plan de backup:**
```bash
# backup-plan.json
{
  "BackupPlanName": "mongodb-efs-daily-backup",
  "Rules": [{
    "RuleName": "DailyBackup3AM",
    "TargetBackupVaultName": "Default",
    "ScheduleExpression": "cron(0 3 * * ? *)",
    "StartWindowMinutes": 60,
    "CompletionWindowMinutes": 120,
    "Lifecycle": {
      "DeleteAfterDays": 30
    }
  }]
}

# Créer le plan
aws backup create-backup-plan --backup-plan file://backup-plan.json
```

**Assignation du file system EFS:**
```bash
# selection.json
{
  "SelectionName": "mongodb-efs-selection",
  "IamRoleArn": "arn:aws:iam::343374742393:role/AWSBackupDefaultServiceRole",
  "Resources": [
    "arn:aws:elasticfilesystem:eu-west-1:343374742393:file-system/fs-xxxxx"
  ]
}

# Assigner
aws backup create-backup-selection \
  --backup-plan-id <plan-id> \
  --backup-selection file://selection.json
```

## 🔄 Processus de restauration

**1. Lister les snapshots disponibles:**
```bash
aws backup list-recovery-points-by-backup-vault \
  --backup-vault-name Default \
  --by-resource-arn "arn:aws:elasticfilesystem:eu-west-1:343374742393:file-system/fs-xxxxx"
```

**2. Créer un job de restauration:**
```bash
aws backup start-restore-job \
  --recovery-point-arn <recovery-point-arn> \
  --metadata file-system-id=fs-new,Encrypted=false \
  --iam-role-arn arn:aws:iam::343374742393:role/AWSBackupDefaultServiceRole
```

**3. Mettre à jour la Task Definition ECS:**
```json
{
  "volumes": [{
    "name": "efs-mongodb",
    "efsVolumeConfiguration": {
      "fileSystemId": "fs-new",  // ← Nouveau file system restauré
      "transitEncryption": "ENABLED"
    }
  }]
}
```

**4. Redémarrer le service:**
```bash
aws ecs update-service \
  --cluster weather-pipeline-cluster \
  --service mongodb \
  --force-new-deployment
```

## 💰 Coût

| Ressource | Taille | Coût/mois |
|-----------|--------|-----------|
| EFS Storage | ~5 GB | ~1.50$ |
| EFS Backup Storage | ~5 GB × 30 jours | ~0.30$ |
| **TOTAL** | - | **~1.80$/mois** |

**RTO (Recovery Time Objective)**: ~10-15 minutes  
**RPO (Recovery Point Objective)**: 24 heures (backup quotidien)
