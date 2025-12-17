# Schéma de la Base de Données MongoDB

## Collection : `measurements`

### Description
Collection unique contenant toutes les mesures météorologiques de l'ensemble des stations (InfoClimat et Weather Underground). Le choix d'une collection unique permet une requête simplifiée et une structure homogène malgré des sources hétérogènes.

### Schéma JSON

```json
{
  "_id": ObjectId("..."),                                    // ID MongoDB auto-généré
  "id_station": "07015",                                     // ID unique de la station
  "nom_station": "Lille-Lesquin",                            // Nom de la ville/station
  "dh_utc": ISODate("2024-10-05T00:00:00.000Z"),            // Date/heure UTC (index)
  "temperature": 7.6,                                        // °C (converti depuis °F si nécessaire)
  "pression": 1020.7,                                        // hPa (converti depuis inHg si nécessaire)
  "humidite": 89.0,                                          // % (0-100)
  "point_de_rosee": 5.9,                                     // °C
  "visibilite": 6000.0,                                      // mètres
  "vent_moyen": 3.6,                                         // km/h (converti depuis mph si nécessaire)
  "vent_rafales": 7.2,                                       // km/h
  "vent_direction": 90.0,                                    // degrés (0-360, converti depuis texte si nécessaire)
  "pluie_3h": 0.0,                                           // mm (converti depuis in si nécessaire)
  "pluie_1h": 0.0,                                           // mm
  "neige_au_sol": null,                                      // mm (nullable)
  "precip_accum": null,                                      // mm (nullable)
  "solar": null,                                             // W/m² (nullable)
  "precip_rate": null,                                       // mm/h (nullable)
  "uv": null,                                                // index UV (nullable)
  "source_file": "2025_12_10_1765356670402_0.jsonl",        // Nom du fichier source (traçabilité)
  "processed_at": ISODate("2025-12-10T09:51:34.000Z"),      // Timestamp du traitement ETL
  "unique_key": "07015_2024-10-05T00:00:00.000Z"            // Clé unique (id_station + dh_utc)
}
```

### Types de données

| Champ | Type MongoDB | Description | Unité |
|-------|-------------|-------------|-------|
| `_id` | ObjectId | Identifiant MongoDB auto-généré | - |
| `id_station` | String | Identifiant unique de la station | - |
| `nom_station` | String | Nom de la station météorologique | - |
| `dh_utc` | Date | Date et heure UTC de la mesure | ISO 8601 |
| `temperature` | Double | Température de l'air | °C |
| `pression` | Double | Pression atmosphérique | hPa |
| `humidite` | Double | Humidité relative | % |
| `point_de_rosee` | Double | Point de rosée | °C |
| `visibilite` | Double | Visibilité | mètres |
| `vent_moyen` | Double | Vitesse moyenne du vent | km/h |
| `vent_rafales` | Double | Vitesse des rafales de vent | km/h |
| `vent_direction` | Double | Direction du vent | degrés |
| `pluie_3h` | Double | Précipitations sur 3 heures | mm |
| `pluie_1h` | Double | Précipitations sur 1 heure | mm |
| `neige_au_sol` | Double / Null | Hauteur de neige au sol | mm |
| `precip_accum` | Double / Null | Précipitations accumulées | mm |
| `solar` | Double / Null | Rayonnement solaire | W/m² |
| `precip_rate` | Double / Null | Taux de précipitations | mm/h |
| `uv` | Double / Null | Indice UV | - |
| `source_file` | String | Nom du fichier JSONL source | - |
| `processed_at` | Date | Timestamp du traitement ETL | ISO 8601 |
| `unique_key` | String | Clé composite unique (index) | - |

### Index MongoDB

```javascript
// Index unique sur unique_key pour éviter les doublons
db.measurements.createIndex({ "unique_key": 1 }, { unique: true })

// Index composé pour les requêtes par station et période
db.measurements.createIndex({ "id_station": 1, "dh_utc": -1 })

// Index sur la date pour les requêtes temporelles
db.measurements.createIndex({ "dh_utc": -1 })
```

### Validation de schéma

```javascript
db.createCollection("measurements", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_station", "nom_station", "dh_utc", "unique_key", "processed_at"],
      properties: {
        id_station: {
          bsonType: "string",
          description: "ID de la station (requis)"
        },
        nom_station: {
          bsonType: "string",
          description: "Nom de la station (requis)"
        },
        dh_utc: {
          bsonType: "date",
          description: "Date/heure UTC (requis)"
        },
        unique_key: {
          bsonType: "string",
          description: "Clé unique (requis)"
        },
        temperature: {
          bsonType: ["double", "null"]
        },
        pression: {
          bsonType: ["double", "null"]
        },
        humidite: {
          bsonType: ["double", "null"],
          minimum: 0,
          maximum: 100
        }
      }
    }
  }
})
```

## Collection : `import_metadata`

### Description
Collection secondaire contenant les métadonnées d'import pour le suivi et l'audit.

### Schéma

```json
{
  "_id": ObjectId("..."),
  "import_date": ISODate("2025-12-10T10:00:00.000Z"),
  "source_file": "20251210_101806_weather_allFiles.json",
  "records_count": 4950,
  "success": true,
  "duration_seconds": 2.3,
  "errors": []
}
```

## Statistiques actuelles

- **Collection** : `measurements`
- **Nombre de documents** : 4 950
- **Stations** : 6 (Bergues, Hazebrouck, Armentières, Lille-Lesquin, Ichtegem, La Madeleine)
- **Période couverte** : Octobre 2024 - Décembre 2024
- **Taux d'erreur** : 0% (aucun doublon, toutes les données importées)
- **Taille moyenne par document** : ~500 bytes

## Requêtes d'exemple

```javascript
// Récupérer les données d'une station pour une journée donnée
db.measurements.find({
  "id_station": "07015",
  "dh_utc": {
    $gte: ISODate("2024-10-05T00:00:00Z"),
    $lt: ISODate("2024-10-06T00:00:00Z")
  }
})

// Moyenne des températures par station
db.measurements.aggregate([
  {
    $group: {
      _id: "$nom_station",
      temp_moyenne: { $avg: "$temperature" },
      count: { $sum: 1 }
    }
  },
  { $sort: { temp_moyenne: -1 } }
])

// Données les plus récentes par station
db.measurements.aggregate([
  { $sort: { "dh_utc": -1 } },
  {
    $group: {
      _id: "$nom_station",
      derniere_mesure: { $first: "$$ROOT" }
    }
  }
])
```
