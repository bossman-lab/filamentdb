"""
FilamentDB — open-source filament parameter database.

Core features:
- Search filaments by brand, type, or model name
- Get AI-recommended print settings for any filament
- Compare two filaments side by side
- Find alternatives by material type
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Optional


DATA_DIR = Path(__file__).parent.parent / "data"
FILAMENTS_PATH = DATA_DIR / "filaments.json"


def _load_db() -> dict:
    """Load the filament database."""
    if not FILAMENTS_PATH.exists():
        return {"brands": {}, "material_types": {}}
    with open(FILAMENTS_PATH) as f:
        return json.load(f)


def list_brands() -> list[str]:
    """List all available brands."""
    db = _load_db()
    return sorted(db.get("brands", {}).keys())


def list_types() -> list[str]:
    """List all available material types."""
    db = _load_db()
    return sorted(db.get("material_types", {}).keys())


def search(query: str, limit: int = 10) -> list[dict]:
    """
    Search filaments by brand, type, or model name.

    Returns list of matching filament entries with full details.
    """
    db = _load_db()
    query_lower = query.lower().strip()
    results = []

    for brand_name, brand_data in db.get("brands", {}).items():
        for model_name, model_data in brand_data.get("models", {}).items():
            score = 0
            # Exact brand match
            if query_lower == brand_name.lower():
                score += 10
            elif query_lower in brand_name.lower():
                score += 5

            # Exact model match
            if query_lower == model_name.lower():
                score += 10
            elif query_lower in model_name.lower():
                score += 5

            # Type match
            mat_type = model_data.get("type", "").lower()
            if query_lower == mat_type:
                score += 8
            elif query_lower in mat_type:
                score += 4

            # Partial match across brand+model
            full_name = f"{brand_name} {model_name}".lower()
            if query_lower in full_name:
                score += 3

            if score > 0:
                results.append({
                    "brand": brand_name,
                    "model": model_name,
                    "type": model_data.get("type", ""),
                    "settings": model_data,
                    "score": score,
                })

    results.sort(key=lambda x: -x["score"])
    return results[:limit]


def recommend(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    material_type: Optional[str] = None,
) -> dict:
    """
    Get recommended print settings.

    If a specific brand+model is found, returns exact settings.
    Otherwise, falls back to material-type defaults.
    """
    db = _load_db()

    # Exact match
    if brand and model:
        brand_data = db.get("brands", {}).get(brand)
        if brand_data:
            model_data = brand_data.get("models", {}).get(model)
            if model_data:
                return {
                    "source": "exact_match",
                    "brand": brand,
                    "model": model,
                    "type": model_data.get("type", ""),
                    "nozzle_temp": model_data.get("nozzle_temp", {}),
                    "bed_temp": model_data.get("bed_temp", {}),
                    "max_volumetric_speed": model_data.get("max_volumetric_speed"),
                    "retraction_distance": model_data.get("retraction_distance"),
                    "retraction_speed": model_data.get("retraction_speed"),
                    "fan_speed": model_data.get("fan_speed"),
                    "bed_adhesion": model_data.get("bed_adhesion"),
                    "drying": model_data.get("drying"),
                    "enclosure_required": model_data.get("enclosure_required", False),
                    "notes": model_data.get("notes", ""),
                }

    # Brand match (any model)
    if brand:
        brand_data = db.get("brands", {}).get(brand)
        if brand_data:
            models = brand_data.get("models", {})
            if material_type:
                # Find the first model of this type for this brand
                for m_name, m_data in models.items():
                    if m_data.get("type", "").lower() == material_type.lower():
                        result = recommend(brand, m_name)
                        result["source"] = "brand_type_match"
                        return result
            # Just return the first PLA model as generic brand recommendation
            for m_name, m_data in models.items():
                if m_data.get("type", "") == "PLA":
                    result = recommend(brand, m_name)
                    result["source"] = "brand_match"
                    result["model"] = f"{m_name} (generic)"
                    return result

    # Type match (material defaults)
    mat_data = db.get("material_types", {}).get(material_type, {})
    if mat_data:
        return {
            "source": "material_type_default",
            "brand": "Generic",
            "model": material_type,
            "type": material_type,
            "nozzle_temp": mat_data.get("typical_nozzle_temp", {}),
            "bed_temp": mat_data.get("typical_bed_temp", {}),
            "max_volumetric_speed": None,
            "retraction_distance": None,
            "retraction_speed": None,
            "fan_speed": mat_data.get("fan_speed"),
            "bed_adhesion": "PEI",
            "drying": mat_data.get("drying"),
            "enclosure_required": mat_data.get("enclosure_required", False),
            "notes": f"Generic {material_type} settings. For best results, search your exact brand.",
        }

    return {"source": "not_found", "error": f"No settings found for {brand} {model}"}


def compare(filament_a: str, filament_b: str) -> dict:
    """
    Compare two filaments by their full names (e.g. "Bambu Lab PLA Basic" vs "eSun PLA+").
    """
    results_a = search(filament_a, limit=1)
    results_b = search(filament_b, limit=1)

    if not results_a:
        return {"error": f"Filament not found: {filament_a}"}
    if not results_b:
        return {"error": f"Filament not found: {filament_b}"}

    a = results_a[0]
    b = results_b[0]

    a_settings = a["settings"]
    b_settings = b["settings"]

    comparison = {
        "a": {"brand": a["brand"], "model": a["model"], "type": a["type"]},
        "b": {"brand": b["brand"], "model": b["model"], "type": b["type"]},
        "nozzle_temp": {
            "a_rec": a_settings.get("nozzle_temp", {}).get("recommended"),
            "b_rec": b_settings.get("nozzle_temp", {}).get("recommended"),
            "difference": abs(
                (a_settings.get("nozzle_temp", {}).get("recommended", 0) or 0)
                - (b_settings.get("nozzle_temp", {}).get("recommended", 0) or 0)
            ),
        },
        "bed_temp": {
            "a_rec": a_settings.get("bed_temp", {}).get("recommended"),
            "b_rec": b_settings.get("bed_temp", {}).get("recommended"),
        },
        "retraction": {
            "a_dist": a_settings.get("retraction_distance"),
            "b_dist": b_settings.get("retraction_distance"),
            "a_speed": a_settings.get("retraction_speed"),
            "b_speed": b_settings.get("retraction_speed"),
        },
        "ratings": {
            "a": a_settings.get("rating"),
            "b": b_settings.get("rating"),
        },
    }

    return comparison


def get_alternatives(
    material_type: str,
    exclude_brand: Optional[str] = None,
) -> list[dict]:
    """
    Find alternative filaments by material type.
    Useful when your usual brand is out of stock.
    """
    db = _load_db()
    results = []

    for brand_name, brand_data in db.get("brands", {}).items():
        if exclude_brand and brand_name.lower() == exclude_brand.lower():
            continue
        for model_name, model_data in brand_data.get("models", {}).items():
            if model_data.get("type", "").lower() == material_type.lower():
                results.append({
                    "brand": brand_name,
                    "model": model_name,
                    "rating": model_data.get("rating", 0),
                    "notes": model_data.get("notes", ""),
                })

    results.sort(key=lambda x: -x["rating"])
    return results
