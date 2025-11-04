# IMPORTATIONS
import bentoml  # Framework de serving ML
import pandas as pd  # Manipulation de données
from typing import Dict, List  # Annotations de types
from pydantic import BaseModel, Field, field_validator, model_validator  # Validation Pydantic V2
import warnings  # Gestion des avertissements

# CHARGEMENT DU MODÈLE
# Référence au modèle sauvegardé (méthode recommandée BentoML 1.4+)
# Utilise le dernier modèle seattle_energy_predictor disponible
bento_model_ref = bentoml.models.get("seattle_energy_predictor")

# Charger le modèle Python sous-jacent (LinearRegression de scikit-learn)
# Cette approche est plus efficace que de charger le modèle à chaque prédiction
model = bento_model_ref.load_model()

# MODÈLES PYDANTIC - RÉPONSES API
# Modèle de réponse pour les prédictions individuelles avec validation des sorties
class PredictionResponse(BaseModel):
    # Réponse structurée pour les prédictions avec validation des données de sortie
    predicted_energy_kwh: float = Field(
        description="Consommation énergétique prédite en kWh",
        ge=0
    )
    predicted_energy_formatted: str = Field(
        description="Consommation formatée pour l'affichage"
    )
    model_info: Dict = Field(
        description="Informations sur le modèle utilisé"
    )
    status: str = Field(
        description="Statut de la prédiction"
    )
    warnings: List[str] = Field(
        default=[],
        description="Avertissements sur les données d'entrée"
    )
    
    @field_validator('predicted_energy_kwh')
    def validate_prediction(cls, v):
        # Validation de la prédiction
        if v < 0:
            raise ValueError('La prédiction ne peut pas être négative')
        if v > 50_000_000:  # 50M kWh semble irréaliste
            warnings.warn(f"Prédiction très élevée: {v:,.0f} kWh")
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        # Validation du statut
        valid_statuses = ['success', 'warning', 'error']
        if v not in valid_statuses:
            raise ValueError(f'Statut doit être un de: {valid_statuses}')
        return v

class BatchPredictionResponse(BaseModel):
    # Réponse pour les prédictions par lot avec validation du nombre total
    predictions: List[Dict] = Field(
        description="Liste des prédictions"
    )
    total_count: int = Field(
        description="Nombre total de prédictions",
        ge=0
    )
    status: str = Field(
        description="Statut global du traitement"
    )
    
    @field_validator('total_count')
    def validate_total_count(cls, v, info):
        # Validation du nombre total
        # Note: En Pydantic V2, la validation cross-field se fait plutôt avec @model_validator
        # Cette validation sera déplacée vers un model_validator si nécessaire
        return v


# MODÈLE PYDANTIC - DONNÉES D'ENTRÉE
# Modèle d'entrée avec validation complète - Features exactes du modèle ML entraîné
class PredictionInput(BaseModel):
    # Caractéristiques d'un bâtiment pour la prédiction de consommation énergétique
    # Inclut validation des champs, logique métier et avertissements personnalisés
    PropertyGFATotal: float = Field(
        description="Surface totale du bâtiment en pieds carrés",
        example=50000,
        ge=0
    )
    NumberofFloors: int = Field(
        description="Nombre d'étages du bâtiment",
        example=5,
        ge=1
    )
    Electricity_kWh: float = Field(
        description="Consommation électrique en kWh",
        example=800000,
        ge=0
    )
    NaturalGas_kWh: float = Field(
        description="Consommation de gaz naturel en kWh",
        example=200000,
        ge=0
    )
    PrimaryPropertyType_Large_Office: int = Field(
        description="1 si le bâtiment est un grand bureau, 0 sinon",
        example=1,
        ge=0,
        le=1
    )
    PrimaryPropertyType_Other: int = Field(
        description="1 si le type de bâtiment est 'Autre', 0 sinon",
        example=0,
        ge=0,
        le=1
    )
    PrimaryPropertyType_Retail_Store: int = Field(
        description="1 si le bâtiment est un magasin, 0 sinon",
        example=0,
        ge=0,
        le=1
    )
    PrimaryPropertyType_Small_and_Mid_Sized_Office: int = Field(
        description="1 si le bâtiment est un petit/moyen bureau, 0 sinon",
        example=0,
        ge=0,
        le=1
    )
    PrimaryPropertyType_Warehouse: int = Field(
        description="1 si le bâtiment est un entrepôt, 0 sinon",
        example=0,
        ge=0,
        le=1
    )
    
    # VALIDATEURS PYDANTIC - NIVEAU CHAMP
    # Validateurs personnalisés pour chaque champ avec règles métier
    
    @field_validator('PropertyGFATotal')
    def validate_property_gfa_total(cls, v):
        # Validation de la surface totale du bâtiment
        if v <= 0:
            raise ValueError('La surface totale doit être positive')
        if v < 500:
            warnings.warn(f"Surface très petite ({v} sq ft) - vérifiez la valeur")
        if v > 2_000_000:
            warnings.warn(f"Surface très grande ({v:,.0f} sq ft) - vérifiez la valeur")
        return v
    
    @field_validator('NumberofFloors')
    def validate_number_of_floors(cls, v):
        # Validation du nombre d'étages
        if v < 1:
            raise ValueError('Le nombre d\'étages doit être au minimum 1')
        if v > 200:
            raise ValueError('Nombre d\'étages irréaliste (> 200)')
        return v
    
    @field_validator('Electricity_kWh')
    def validate_electricity_kwh(cls, v):
        # Validation de la consommation électrique
        if v < 0:
            raise ValueError('La consommation électrique ne peut pas être négative')
        if v > 10_000_000:
            warnings.warn(f"Consommation électrique très élevée ({v:,.0f} kWh)")
        return v
    
    @field_validator('NaturalGas_kWh')
    def validate_natural_gas_kwh(cls, v):
        # Validation de la consommation de gaz naturel
        if v < 0:
            raise ValueError('La consommation de gaz naturel ne peut pas être négative')
        if v > 5_000_000:
            warnings.warn(f"Consommation de gaz naturel très élevée ({v:,.0f} kWh)")
        return v
    
    # VALIDATEURS PYDANTIC - NIVEAU MODÈLE (CROSS-FIELD)
    # Validation des types de propriété : une seule variable à 1, les autres à 0
    @model_validator(mode='after')
    def validate_property_types(self):
        # Validation que seulement un type de propriété est sélectionné
        property_types = [
            self.PrimaryPropertyType_Large_Office,
            self.PrimaryPropertyType_Other,
            self.PrimaryPropertyType_Retail_Store,
            self.PrimaryPropertyType_Small_and_Mid_Sized_Office,
            self.PrimaryPropertyType_Warehouse
        ]
        
        # Vérifier que toutes les valeurs sont 0 ou 1
        for i, val in enumerate(property_types):
            if val not in [0, 1]:
                raise ValueError(f'Les types de propriété doivent être 0 ou 1, reçu: {val}')
        
        # Vérifier qu'exactement un type est sélectionné
        sum_types = sum(property_types)
        if sum_types != 1:
            raise ValueError(
                f'Exactement un type de propriété doit être sélectionné (somme = 1), '
                f'reçu somme = {sum_types}. '
                f'Une seule des variables PrimaryPropertyType_* doit être à 1, les autres à 0.'
            )
        
        return self
    
    @model_validator(mode='after')
    def validate_energy_density(self):
        # Validation de la densité énergétique
        total_energy = self.Electricity_kWh + self.NaturalGas_kWh
        if self.PropertyGFATotal > 0:  # Éviter division par zéro
            energy_density = total_energy / self.PropertyGFATotal
            if energy_density > 500:  # kWh par sq ft
                warnings.warn(f"Densité énergétique élevée: {energy_density:.1f} kWh/sq ft")
        return self
    
    @model_validator(mode='after')
    def validate_building_logic(self):
        # Validations logiques entre les différents champs
        floors = self.NumberofFloors
        area = self.PropertyGFATotal
        
        # Validation de la surface par étage
        if floors > 0 and area > 0:
            area_per_floor = area / floors
            if area_per_floor < 100:
                warnings.warn(f"Surface par étage très petite: {area_per_floor:.0f} sq ft/floor")
            elif area_per_floor > 100_000:
                warnings.warn(f"Surface par étage très grande: {area_per_floor:,.0f} sq ft/floor")
        
        # Validation cohérence type de bâtiment vs caractéristiques
        if self.PrimaryPropertyType_Warehouse == 1:
            if floors > 5:
                warnings.warn("Les entrepôts ont généralement moins de 5 étages")
        
        if self.PrimaryPropertyType_Large_Office == 1:
            if area < 30_000:
                warnings.warn("Un 'Large Office' a généralement plus de 30,000 sq ft")
        
        return self
    
    class Config:
        # Configuration Pydantic
        validate_assignment = True  # Validation lors des modifications
        extra = 'forbid'  # Interdire les champs supplémentaires
        
        json_schema_extra = {
            "example": {
                "PropertyGFATotal": 50000,
                "NumberofFloors": 5,
                "Electricity_kWh": 800000,
                "NaturalGas_kWh": 200000,
                "PrimaryPropertyType_Large_Office": 1,
                "PrimaryPropertyType_Other": 0,
                "PrimaryPropertyType_Retail_Store": 0,
                "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
                "PrimaryPropertyType_Warehouse": 0
            }
        }

# SERVICE BENTOML PRINCIPAL
@bentoml.service(
    name="seattle-energy-predictor",  # Nom du service pour identification
    resources={"cpu": "2"},  # Allocation de 2 CPU pour les prédictions
    traffic={"timeout": 20}  # Timeout de 20 secondes par requête
)
class SeattleEnergyPredictor:
    
    def _validate_business_logic(self, data: PredictionInput, warning_list: List[str]):
        # Validations métier supplémentaires pour vérifier la cohérence des données
        # Calcule les intensités énergétiques et vérifie les seuils par type de bâtiment
        # Validation de l'intensité énergétique globale du bâtiment
        total_energy = data.Electricity_kWh + data.NaturalGas_kWh
        if data.PropertyGFATotal > 0:  # Éviter division par zéro
            energy_intensity = total_energy / data.PropertyGFATotal
            
            # Seuils basés sur l'analyse des données réelles de Seattle
            # Intensité normale: 20-80 kWh/sq ft selon le type de bâtiment
            if energy_intensity > 100:  # kWh/sq ft - Seuil élevé
                warning_list.append(f"Intensité énergétique élevée: {energy_intensity:.1f} kWh/sq ft")
            elif energy_intensity < 10:  # kWh/sq ft - Seuil bas
                warning_list.append(f"Intensité énergétique faible: {energy_intensity:.1f} kWh/sq ft")
        
        # Validation spécifique par type de bâtiment vs consommation attendue
        if data.PrimaryPropertyType_Warehouse == 1:
            # Les entrepôts ont généralement moins de consommation électrique (éclairage, peu d'équipements)
            # Seuil basé sur l'analyse des entrepôts de Seattle: moyenne ~20 kWh/sq ft
            elec_intensity = data.Electricity_kWh / data.PropertyGFATotal if data.PropertyGFATotal > 0 else 0
            if elec_intensity > 30:  # kWh/sq ft - Seuil élevé pour entrepôt
                warning_list.append("Consommation électrique élevée pour un entrepôt")
        
        if data.PrimaryPropertyType_Large_Office == 1:
            # Les grands bureaux ont une consommation électrique élevée (éclairage, AC, équipements IT)
            # Seuil basé sur l'analyse des bureaux de Seattle: moyenne ~35 kWh/sq ft
            elec_intensity = data.Electricity_kWh / data.PropertyGFATotal if data.PropertyGFATotal > 0 else 0
            if elec_intensity < 15:  # kWh/sq ft - Seuil bas pour grand bureau
                warning_list.append("Consommation électrique faible pour un grand bureau")
        
        # Validation cohérence architecturale : étages vs surface totale
        if data.NumberofFloors > 1:
            avg_floor_area = data.PropertyGFATotal / data.NumberofFloors
            # Surface moyenne typique par étage: 5,000 - 25,000 sq ft
            if avg_floor_area > 50000:  # Seuil pour surface exceptionnellement grande
                warning_list.append(f"Surface moyenne par étage très grande: {avg_floor_area:,.0f} sq ft")
    
    def _format_validation_error(self, error: Exception) -> Dict:
        # Formatage standardisé des erreurs de validation Pydantic
        # Transforme les erreurs en format JSON lisible pour l'API
        if hasattr(error, 'errors'):  # Erreur Pydantic
            error_details = []
            for err in error.errors():
                field = ' -> '.join(str(x) for x in err['loc'])
                message = err['msg']
                error_details.append(f"{field}: {message}")
            
            return {
                "error": "Erreur de validation des données",
                "details": error_details,
                "status": "error"
            }
        else:
            return {
                "error": str(error),
                "status": "error"
            }
    
    @bentoml.api
    def predict_single(self, data: PredictionInput) -> PredictionResponse:
        # Cette fonction effectue une prédiction de consommation énergétique annuelle
        # pour un bâtiment spécifique avec validation complète des données.
        warning_list = []
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                # Convertir le modèle Pydantic en dictionnaire avec les noms exacts attendus par le modèle ML
                # Les noms de colonnes doivent correspondre exactement à ceux utilisés lors de l'entraînement
                data_dict = {
                    'PropertyGFATotal': data.PropertyGFATotal,
                    'NumberofFloors': data.NumberofFloors,
                    'Electricity(kWh)': data.Electricity_kWh,
                    'NaturalGas(kWh)': data.NaturalGas_kWh,
                    'PrimaryPropertyType_Large Office': data.PrimaryPropertyType_Large_Office,
                    'PrimaryPropertyType_Other': data.PrimaryPropertyType_Other,
                    'PrimaryPropertyType_Retail Store': data.PrimaryPropertyType_Retail_Store,
                    'PrimaryPropertyType_Small- and Mid-Sized Office': data.PrimaryPropertyType_Small_and_Mid_Sized_Office,
                    'PrimaryPropertyType_Warehouse': data.PrimaryPropertyType_Warehouse
                }
                
                # Validation supplémentaire des données avec règles métier spécifiques
                self._validate_business_logic(data, warning_list)
                
                # Convertir en DataFrame pandas pour compatibilité avec le modèle sklearn
                df_input = pd.DataFrame([data_dict])
                
                # Effectuer la prédiction avec le modèle Linear Regression chargé
                prediction = model.predict(df_input)[0]
                
                # Capturer tous les avertissements générés pendant la validation
                if w:
                    warning_list.extend([str(warning.message) for warning in w])
                
                # Validation finale de la prédiction pour s'assurer qu'elle est logique
                if prediction < 0:
                    raise ValueError("La prédiction ne peut pas être négative")
                
                return PredictionResponse(
                    predicted_energy_kwh=float(prediction),
                    predicted_energy_formatted=f"{prediction:,.0f} kWh",
                    model_info={
                        "algorithm": "Linear Regression",
                        "r2_score": "0.9343 (93.43%)",
                        "mae_test": "90,144 kWh",
                        "rmse_test": "261,530 kWh"
                    },
                    status="warning" if warning_list else "success",
                    warnings=warning_list
                )
                
            except Exception as e:
                return self._format_validation_error(e)
    
    @bentoml.api
    def predict_batch(self, data_list: List[Dict]) -> BatchPredictionResponse:
        # Permet de traiter plusieurs bâtiments simultanément pour optimiser les performances.
        # Limite à 1000 bâtiments par requête pour éviter les timeouts.
        try:
            # Validation de la taille du lot pour éviter les surcharges serveur
            if len(data_list) == 0:
                raise ValueError("La liste ne peut pas être vide")
            if len(data_list) > 1000:
                raise ValueError("Maximum 1000 bâtiments par requête pour éviter les timeouts")
            
            # Valider chaque élément individuellement avec Pydantic
            validated_data = []
            all_warnings = []
            
            for i, item in enumerate(data_list):
                try:
                    # Validation stricte avec le modèle Pydantic PredictionInput
                    validated_item = PredictionInput(**item)
                    validated_data.append(validated_item)
                except Exception as e:
                    # Indiquer précisément quel élément pose problème
                    raise ValueError(f"Erreur dans l'élément {i+1}: {str(e)}")
            
            # Convertir chaque élément validé au format attendu par le modèle ML
            data_dicts = []
            for data in validated_data:
                data_dict = {
                    'PropertyGFATotal': data.PropertyGFATotal,
                    'NumberofFloors': data.NumberofFloors,
                    'Electricity(kWh)': data.Electricity_kWh,
                    'NaturalGas(kWh)': data.NaturalGas_kWh,
                    'PrimaryPropertyType_Large Office': data.PrimaryPropertyType_Large_Office,
                    'PrimaryPropertyType_Other': data.PrimaryPropertyType_Other,
                    'PrimaryPropertyType_Retail Store': data.PrimaryPropertyType_Retail_Store,
                    'PrimaryPropertyType_Small- and Mid-Sized Office': data.PrimaryPropertyType_Small_and_Mid_Sized_Office,
                    'PrimaryPropertyType_Warehouse': data.PrimaryPropertyType_Warehouse
                }
                data_dicts.append(data_dict)
            
            # Convertir en DataFrame pandas pour traitement vectorisé efficace
            df_input = pd.DataFrame(data_dicts)
            
            # Effectuer les prédictions en lot (plus efficace que individuellement)
            predictions = model.predict(df_input)
            
            # Construire les résultats finaux avec validation métier pour chaque prédiction
            results = []
            for i, (prediction, original_data) in enumerate(zip(predictions, validated_data)):
                item_warnings = []
                # Appliquer la validation métier spécifique à chaque bâtiment
                self._validate_business_logic(original_data, item_warnings)
                
                result_item = {
                    "building_id": i + 1,
                    "predicted_energy_kwh": float(prediction),
                    "predicted_energy_formatted": f"{prediction:,.0f} kWh",
                    "warnings": item_warnings
                }
                results.append(result_item)
                all_warnings.extend(item_warnings)
            
            return BatchPredictionResponse(
                predictions=results,
                total_count=len(results),
                status="warning" if all_warnings else "success"
            )
            
        except Exception as e:
            return self._format_validation_error(e)
    
    @bentoml.api
    def get_feature_info(self) -> Dict:
        # Fournit toutes les informations nécessaires pour utiliser correctement l'API,
        # incluant les descriptions des champs, règles de validation et exemples.
        return {
            "model_info": {
                "algorithm": "Linear Regression",
                "r2_score": "0.9343 (93.43%)",
                "mae_test": "90,144 kWh",
                "rmse_test": "261,530 kWh",
                "features_count": 9
            },
            "required_features": [
                "PropertyGFATotal",
                "NumberofFloors",
                "Electricity_kWh",
                "NaturalGas_kWh",
                "PrimaryPropertyType_Large_Office",
                "PrimaryPropertyType_Other",
                "PrimaryPropertyType_Retail_Store",
                "PrimaryPropertyType_Small_and_Mid_Sized_Office",
                "PrimaryPropertyType_Warehouse"
            ],
            "feature_descriptions": {
                "PropertyGFATotal": "Surface totale du bâtiment en pieds carrés (>= 0)",
                "NumberofFloors": "Nombre d'étages du bâtiment (>= 1)",
                "Electricity_kWh": "Consommation électrique en kWh (>= 0)",
                "NaturalGas_kWh": "Consommation de gaz naturel en kWh (>= 0)",
                "PrimaryPropertyType_Large_Office": "1 si grand bureau, 0 sinon",
                "PrimaryPropertyType_Other": "1 si type 'Autre', 0 sinon",
                "PrimaryPropertyType_Retail_Store": "1 si magasin, 0 sinon",
                "PrimaryPropertyType_Small_and_Mid_Sized_Office": "1 si petit/moyen bureau, 0 sinon",
                "PrimaryPropertyType_Warehouse": "1 si entrepôt, 0 sinon"
            },
            "validation_rules": {
                "property_types": "Une seule des variables PrimaryPropertyType_* doit être à 1, les autres à 0",
                "numeric_values": "Toutes les valeurs numériques doivent être positives ou nulles",
                "floors": "Le nombre d'étages doit être au minimum 1"
            },
            "example_inputs": {
                "large_office": {
                    "PropertyGFATotal": 75000,
                    "NumberofFloors": 10,
                    "Electricity_kWh": 1200000,
                    "NaturalGas_kWh": 300000,
                    "PrimaryPropertyType_Large_Office": 1,
                    "PrimaryPropertyType_Other": 0,
                    "PrimaryPropertyType_Retail_Store": 0,
                    "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
                    "PrimaryPropertyType_Warehouse": 0
                },
                "retail_store": {
                    "PropertyGFATotal": 25000,
                    "NumberofFloors": 2,
                    "Electricity_kWh": 600000,
                    "NaturalGas_kWh": 150000,
                    "PrimaryPropertyType_Large_Office": 0,
                    "PrimaryPropertyType_Other": 0,
                    "PrimaryPropertyType_Retail_Store": 1,
                    "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
                    "PrimaryPropertyType_Warehouse": 0
                }
            },
            "target": "SiteEnergyUse(kWh) - Consommation énergétique totale annuelle prédite"
        }

    @bentoml.api
    def health(self) -> Dict:
        # Effectue un test complet du service en réalisant une prédiction de test
        # pour s'assurer que le modèle est correctement chargé et opérationnel.
        try:
            # Test de fonctionnement avec des données de référence
            test_data = pd.DataFrame([{
                'PropertyGFATotal': 50000,
                'NumberofFloors': 5,
                'Electricity(kWh)': 800000,
                'NaturalGas(kWh)': 200000,
                'PrimaryPropertyType_Large Office': 1,
                'PrimaryPropertyType_Other': 0,
                'PrimaryPropertyType_Retail Store': 0,
                'PrimaryPropertyType_Small- and Mid-Sized Office': 0,
                'PrimaryPropertyType_Warehouse': 0
            }])
            
            prediction = model.predict(test_data)
            
            return {
                "status": "healthy",
                "service": "seattle-energy-predictor",
                "model_loaded": True,
                "model_tag": str(bento_model_ref.tag),
                "test_prediction": float(prediction[0]),
                "features_count": len(test_data.columns),
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": False,
                "timestamp": pd.Timestamp.now().isoformat()
            }

    @bentoml.api
    def validate_data(self, data: PredictionInput) -> Dict:
        # Permet de tester la validité des données et obtenir des avertissements
        # sans consommer de ressources pour la prédiction. Utile pour la validation
        # en amont ou le debugging des données d'entrée.
        try:
            warning_list = []
            
            # Application de toutes les règles de validation métier
            self._validate_business_logic(data, warning_list)
            
            return {
                "validation_status": "valid",
                "warnings": warning_list,
                "warning_count": len(warning_list),
                "data_summary": {
                    "PropertyGFATotal": data.PropertyGFATotal,
                    "NumberofFloors": data.NumberofFloors,
                    "total_energy": data.Electricity_kWh + data.NaturalGas_kWh,
                    "energy_intensity": (data.Electricity_kWh + data.NaturalGas_kWh) / data.PropertyGFATotal if data.PropertyGFATotal > 0 else 0,
                    "building_type": self._get_building_type(data)
                },
                "status": "warning" if warning_list else "success"
            }
            
        except Exception as e:
            return self._format_validation_error(e)
    
    def _get_building_type(self, data: PredictionInput) -> str:
        # Fonction utilitaire : Déterminer le type de bâtiment depuis les flags booléens
        # Convertit les variables binaires PrimaryPropertyType_* en label lisible
        if data.PrimaryPropertyType_Large_Office == 1:
            return "Grand Bureau"
        elif data.PrimaryPropertyType_Other == 1:
            return "Autre"
        elif data.PrimaryPropertyType_Retail_Store == 1:
            return "Magasin"
        elif data.PrimaryPropertyType_Small_and_Mid_Sized_Office == 1:
            return "Petit/Moyen Bureau"
        elif data.PrimaryPropertyType_Warehouse == 1:
            return "Entrepôt"
        else:
            return "Type non défini"