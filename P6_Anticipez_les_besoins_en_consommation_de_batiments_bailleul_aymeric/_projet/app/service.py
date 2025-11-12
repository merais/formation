# IMPORTATIONS
import bentoml  # Framework de serving ML
import pandas as pd  # Manipulation de données
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator  # Pydantic V2
import warnings  # Gestion des avertissements

# CHARGEMENT DU MODÈLE
# Utilise le dernier modèle seattle_energy_predictor disponible
bento_model_ref = bentoml.models.get("seattle_energy_predictor")
META = getattr(getattr(bento_model_ref, "info", None), "metadata", {}) or {}
_CUSTOM_OBJECTS = getattr(bento_model_ref, "custom_objects", {}) or {}
FEATURE_NAMES: List[str] = list(_CUSTOM_OBJECTS.get("feature_names", []) or [])
SAMPLE_INPUT: Dict = dict(_CUSTOM_OBJECTS.get("sample_input", {}) or {})

# Charger le modèle ML sous-jacent (RandomForestRegressor)
model = bento_model_ref.load_model()


# --------- Pydantic response models ---------
class PredictionResponse(BaseModel):
    predicted_energy_kwh: float = Field(description="Consommation énergétique prédite en kWh", ge=0)
    predicted_energy_formatted: str = Field(description="Consommation formatée pour l'affichage")
    model_info: Dict = Field(description="Informations sur le modèle utilisé")
    status: str = Field(description="Statut de la prédiction")
    warnings: List[str] = Field(default=[], description="Avertissements sur les données d'entrée")

    @field_validator("predicted_energy_kwh")
    def validate_prediction(cls, v):
        if v < 0:
            raise ValueError("La prédiction ne peut pas être négative")
        if v > 50_000_000:
            warnings.warn(f"Prédiction très élevée: {v:,.0f} kWh")
        return v

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["success", "warning", "error"]:
            raise ValueError("Statut invalide")
        return v


class BatchPredictionResponse(BaseModel):
    predictions: List[Dict]
    total_count: int = Field(ge=0)
    status: str


# --------- Input model (restricted, minimal) ---------
PRIMARY_TYPES: List[str] = [c.replace("PrimaryPropertyType_", "") for c in FEATURE_NAMES if c.startswith("PrimaryPropertyType_")]
BUILDING_GROUP_COLS: List[str] = [c for c in FEATURE_NAMES if c.startswith("Building_Group_")]

# Exemples complets pour tous les PrimaryPropertyType
_EXAMPLE_BASE = {"PropertyGFATotal": 50000, "NumberofFloors": 5, "YearBuilt": 1995}
PRIMARY_TYPE_EXAMPLES: List[Dict] = [
    {**_EXAMPLE_BASE, "PrimaryPropertyType": pt} for pt in PRIMARY_TYPES
]


class RestrictedPredictionInput(BaseModel):
    PropertyGFATotal: float = Field(..., gt=10, le=1000000, description="Surface totale du bâtiment en sq ft (>10 et <=1,000,000)")
    NumberofFloors: int = Field(..., ge=1, le=100, description="Nombre d'étages (>=1 et <=100)")
    PrimaryPropertyType: str = Field(
        ...,
        description="Type principal du bâtiment (doit appartenir à la liste autorisée)",
        json_schema_extra={"enum": PRIMARY_TYPES},
    )
    YearBuilt: Optional[int] = Field(None, gt=1800, le=2050, description="Année de construction (>1800 et <=2050)")

    @field_validator("PrimaryPropertyType")
    def validate_primary_type(cls, v):
        if PRIMARY_TYPES and v not in PRIMARY_TYPES:
            raise ValueError(f"PrimaryPropertyType doit être dans {PRIMARY_TYPES}")
        return v

    class Config:
        json_schema_extra = {
            "example": {**_EXAMPLE_BASE, "PrimaryPropertyType": "Large Office"},
        }


# --------- Helpers ---------
# Mapping global pour exposition dans la doc Swagger
GROUP_MAP: Dict[str, str] = {
    "Hospital": "Healthcare",
    "Medical Office": "Healthcare",
    "Senior Care Community": "Healthcare",
    "Hotel": "Hospitality",
    "Residence Hall": "Hospitality",
    "Large Office": "Office",
    "Small- and Mid-Sized Office": "Office",
    "Retail Store": "Retail",
    "Supermarket / Grocery Store": "Retail",
    "Restaurant": "Retail",
    "Warehouse": "Storage",
    "Refrigerated Warehouse": "Storage",
    "Self-Storage Facility": "Storage",
}
def _algo_info() -> Dict:
    perf = META.get("performance", {}) if isinstance(META.get("performance"), dict) else {}
    return {
        "algorithm": META.get("algorithm") or "Random Forest Regressor",
        **perf,
        "model_tag": str(bento_model_ref.tag),
        "features_count": len(FEATURE_NAMES),
    }


def _derive_building_group(primary_type: str) -> str:
    # Mapping heuristique du type vers un groupe (aligné aux colonnes Building_Group_*)
    return GROUP_MAP.get(primary_type, "Other")


from typing import Tuple


def _from_restricted_to_full(payload: RestrictedPredictionInput) -> Tuple[pd.DataFrame, List[str]]:
    warnings_list: List[str] = []

    # Point de départ: échantillon enregistré ou zéro
    base = dict(SAMPLE_INPUT) if SAMPLE_INPUT else {k: 0 for k in FEATURE_NAMES}

    # Affectations directes si présentes dans le modèle
    if "PropertyGFATotal" in base:
        base["PropertyGFATotal"] = payload.PropertyGFATotal
    if "NumberofFloors" in base:
        base["NumberofFloors"] = payload.NumberofFloors

    # Derived features
    if "Surface_par_etage" in base:
        if payload.NumberofFloors > 0:
            base["Surface_par_etage"] = payload.PropertyGFATotal / payload.NumberofFloors
        else:
            warnings_list.append("NumberofFloors <= 0, Surface_par_etage conservée depuis l'échantillon")

    # Age et features associées
    if payload.YearBuilt is not None:
        ref_year = 2016  # année du dataset
        age = max(0, ref_year - payload.YearBuilt)
        if "Age_batiment" in base:
            base["Age_batiment"] = age
        if "Surface_x_Age" in base:
            base["Surface_x_Age"] = payload.PropertyGFATotal * age
        if "Categorie_age" in base:
            # Binning simple (0=récent,1=moyen,2=ancien)
            base["Categorie_age"] = 0 if age < 10 else (1 if age < 30 else 2)
    else:
        # Conserver les valeurs de l'échantillon mais signaler
        if any(k in base for k in ["Age_batiment", "Surface_x_Age", "Categorie_age"]):
            warnings_list.append("YearBuilt manquant: Age/Categorie_age/Surface_x_Age conservés depuis l'échantillon")

    # Taille/Hauteur heuristiques (si colonnes attendues)
    if "Taille_batiment" in base:
        area = payload.PropertyGFATotal
        base["Taille_batiment"] = 0 if area < 20_000 else (1 if area < 100_000 else 2)
    if "Hauteur_batiment" in base:
        floors = payload.NumberofFloors
        base["Hauteur_batiment"] = 0 if floors <= 3 else (1 if floors <= 7 else 2)

    # Mettre à zéro tous les one-hot PrimaryPropertyType_*
    for col in FEATURE_NAMES:
        if col.startswith("PrimaryPropertyType_"):
            base[col] = 0
    # Activer celui choisi
    chosen_pt_col = f"PrimaryPropertyType_{payload.PrimaryPropertyType}"
    if chosen_pt_col in base:
        base[chosen_pt_col] = 1
    else:
        warnings_list.append(f"Type {payload.PrimaryPropertyType} non trouvé dans le modèle, conservé défaut échantillon")

    # Groupes de bâtiment
    for col in BUILDING_GROUP_COLS:
        base[col] = 0
    chosen_group = _derive_building_group(payload.PrimaryPropertyType)
    group_col = f"Building_Group_{chosen_group}"
    if group_col in base:
        base[group_col] = 1
    else:
        if BUILDING_GROUP_COLS:
            warnings_list.append(f"Groupe {chosen_group} absent des features, groupes conservés à 0")

    # Construire DataFrame dans l'ordre des features
    row = {col: base.get(col, 0) for col in FEATURE_NAMES}
    df = pd.DataFrame([row])
    return df, warnings_list


# --------- Service ---------
@bentoml.service(
    name="seattle-energy-predictor",
    resources={"cpu": "2"},
    traffic={"timeout": 20},
)
class SeattleEnergyPredictor:
    def _format_validation_error(self, error: Exception) -> PredictionResponse:
        warnings_list: List[str] = []
        if hasattr(error, "errors"):
            try:
                for err in error.errors():
                    field = " -> ".join(str(x) for x in err.get("loc", []))
                    message = err.get("msg", str(error))
                    warnings_list.append(f"{field}: {message}")
            except Exception:
                warnings_list.append(str(error))
        else:
            warnings_list.append(str(error))

        return PredictionResponse(
            predicted_energy_kwh=0.0,
            predicted_energy_formatted="0 kWh",
            model_info=_algo_info(),
            status="error",
            warnings=warnings_list,
        )

    @bentoml.api
    def predict_single(self, data: RestrictedPredictionInput) -> PredictionResponse:
        # Entrée restreinte et sans fuite; reconstitution des features attendues
        try:
            df, warn_list = _from_restricted_to_full(data)
            pred = float(model.predict(df)[0])
            status = "warning" if warn_list else "success"
            return PredictionResponse(
                predicted_energy_kwh=pred,
                predicted_energy_formatted=f"{pred:,.0f} kWh",
                model_info=_algo_info(),
                status=status,
                warnings=warn_list,
            )
        except Exception as e:
            return self._format_validation_error(e)

    @bentoml.api
    def predict_batch(self, data_list: List[RestrictedPredictionInput]) -> BatchPredictionResponse:
        try:
            if not data_list:
                raise ValueError("La liste ne peut pas être vide")
            if len(data_list) > 1000:
                raise ValueError("Maximum 1000 bâtiments par requête")

            dfs = []
            all_warns: List[str] = []
            for item in data_list:
                df, warns = _from_restricted_to_full(item)
                dfs.append(df)
                all_warns.extend(warns)

            X = pd.concat(dfs, ignore_index=True)
            preds = model.predict(X)
            results = [
                {
                    "building_id": i + 1,
                    "predicted_energy_kwh": float(p),
                    "predicted_energy_formatted": f"{p:,.0f} kWh",
                }
                for i, p in enumerate(preds)
            ]

            return BatchPredictionResponse(
                predictions=results,
                total_count=len(results),
                status="warning" if all_warns else "success",
            )
        except Exception:
            return BatchPredictionResponse(predictions=[], total_count=0, status="error")

    @bentoml.api
    def get_feature_info(self) -> Dict:
        # Construire des exemples par type pour les clients
        examples_by_type = {
            pt: {"PropertyGFATotal": 50000, "NumberofFloors": 5, "PrimaryPropertyType": pt, "YearBuilt": 1995}
            for pt in PRIMARY_TYPES
        }
        # Mapping explicite PrimaryPropertyType -> Building_Group
        primary_type_group_map = {pt: _derive_building_group(pt) for pt in PRIMARY_TYPES}

        return {
            "model_info": _algo_info(),
            "required_minimal_input": [
                "PropertyGFATotal",
                "NumberofFloors",
                "PrimaryPropertyType",
                "YearBuilt (optionnel)",
            ],
            "allowed_primary_property_types": PRIMARY_TYPES,
            "building_group_columns": BUILDING_GROUP_COLS,
            "example_payloads_by_type": examples_by_type,
            "primary_type_to_group_map": primary_type_group_map,
            "notes": [
                "Aucune variable de consommation directe n'est acceptée",
                "Certaines features dérivées sont reconstruites heuristiquement ou à partir de l'échantillon",
            ],
        }

    @bentoml.api
    def health(self) -> Dict:
        try:
            # Utiliser l'échantillon pour un test de bout en bout
            if not FEATURE_NAMES:
                raise RuntimeError("FEATURE_NAMES vide: vérifiez le modèle BentoML")
            base = {c: SAMPLE_INPUT.get(c, 0) for c in FEATURE_NAMES}
            df = pd.DataFrame([base])
            pred = float(model.predict(df)[0])
            return {
                "status": "healthy",
                "service": "seattle-energy-predictor",
                "model_loaded": True,
                "model_tag": str(bento_model_ref.tag),
                "test_prediction": pred,
                "features_count": len(FEATURE_NAMES),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": False,
            }

    @bentoml.api
    def get_group_map(self) -> Dict:
        # Expose clairement le mapping PrimaryPropertyType -> Building_Group dans Swagger
        return {
            "group_map": GROUP_MAP,
            "allowed_primary_property_types": PRIMARY_TYPES,
            "building_group_columns": BUILDING_GROUP_COLS,
            "note": "Tout type non listé est mappé vers 'Other'",
        }

    @bentoml.api
    def validate_data(self, data: RestrictedPredictionInput) -> Dict:
        try:
            df, warns = _from_restricted_to_full(data)
            summary = {
                "computed": {
                    k: df.iloc[0][k]
                    for k in [
                        col
                        for col in [
                            "Surface_par_etage",
                            "Age_batiment",
                            "Surface_x_Age",
                            "Categorie_age",
                            "Taille_batiment",
                            "Hauteur_batiment",
                        ]
                        if col in df.columns
                    ]
                },
                "one_hot_primary_type": data.PrimaryPropertyType,
                "warnings": warns,
            }
            return {"validation_status": "valid", "status": "warning" if warns else "success", **summary}
        except Exception as e:
            return {"validation_status": "invalid", "status": "error", "error": str(e)}