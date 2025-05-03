# -*- coding: utf-8 -*-
"""
Data Preprocessor Module

This module handles data cleaning, normalization, and preparation for the AI analysis module.
It ensures data consistency, handles missing values, and converts data to appropriate formats.
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Main data preprocessing class for all types of collected data"""
    
    def __init__(self):
        self.preprocessing_steps = {}
        logger.info("Data preprocessor initialized")
    
    def register_preprocessing_step(self, data_type: str, step_function, step_order: int = 0) -> None:
        """Register a preprocessing step for a specific data type"""
        if data_type not in self.preprocessing_steps:
            self.preprocessing_steps[data_type] = []
        
        self.preprocessing_steps[data_type].append((step_order, step_function))
        # Sort by step order
        self.preprocessing_steps[data_type].sort(key=lambda x: x[0])
        logger.info(f"Registered preprocessing step for {data_type} with order {step_order}")
    
    def preprocess(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Preprocess data according to registered steps for its type"""
        if data_type not in self.preprocessing_steps:
            logger.warning(f"No preprocessing steps registered for {data_type}")
            return data
        
        processed_data = data.copy()
        for _, step_function in self.preprocessing_steps[data_type]:
            try:
                processed_data = step_function(processed_data)
            except Exception as e:
                logger.error(f"Error in preprocessing step for {data_type}: {e}")
                # Continue with other steps even if one fails
        
        return processed_data
    
    def preprocess_batch(self, data_list: List[Dict[str, Any]], data_type: str) -> List[Dict[str, Any]]:
        """Preprocess a batch of data items"""
        return [self.preprocess(data, data_type) for data in data_list]
    
    def convert_to_dataframe(self, data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert a list of data dictionaries to a pandas DataFrame"""
        return pd.DataFrame(data_list)


# Common preprocessing functions that can be registered

def clean_missing_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace None or empty string values with NaN for proper handling"""
    result = data.copy()
    for key, value in result.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            result[key] = np.nan
    return result


def normalize_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all timestamp fields are in a consistent format"""
    result = data.copy()
    timestamp_fields = [field for field in result.keys() 
                       if "time" in field.lower() or "date" in field.lower()]
    
    for field in timestamp_fields:
        value = result[field]
        if value is None:
            continue
            
        # If already a unix timestamp (float/int), leave as is
        if isinstance(value, (int, float)):
            continue
            
        # Convert string timestamps to unix time
        if isinstance(value, str):
            try:
                # Try several common formats
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(value, fmt)
                        result[field] = dt.timestamp()
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Could not convert timestamp {value}: {e}")
    
    return result


def standardize_units(data: Dict[str, Any], unit_mappings: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Standardize measurement units (e.g., convert all weight to kg)"""
    result = data.copy()
    
    # For each key that might need unit conversion
    for measurement_type, unit_map in unit_mappings.items():
        # Check if the measurement and its unit are in the data
        if measurement_type in result and f"{measurement_type}_unit" in result:
            value = result[measurement_type]
            unit = result[f"{measurement_type}_unit"]
            
            # Only proceed if we have a mapping for this unit
            if unit in unit_map:
                # Apply the conversion factor
                result[measurement_type] = value * unit_map[unit]
                # Update to the standard unit
                result[f"{measurement_type}_unit"] = list(unit_map.keys())[0]  # First unit is standard
    
    return result


def remove_outliers(data: Dict[str, Any], field: str, min_val: float, max_val: float) -> Dict[str, Any]:
    """Remove outlier values for specific fields"""
    result = data.copy()
    if field in result:
        value = result[field]
        if isinstance(value, (int, float)) and (value < min_val or value > max_val):
            result[field] = np.nan
            logger.info(f"Removed outlier value {value} for field {field}")
    return result


class HealthDataPreprocessor:
    """Specialized preprocessor for health data"""
    
    def __init__(self, main_preprocessor: DataPreprocessor):
        self.preprocessor = main_preprocessor
        self._register_steps()
        logger.info("Health data preprocessor initialized")
    
    def _register_steps(self) -> None:
        """Register health data preprocessing steps"""
        # Step 1: Clean missing values
        self.preprocessor.register_preprocessing_step(
            "health", 
            clean_missing_values, 
            step_order=1
        )
        
        # Step 2: Normalize timestamps
        self.preprocessor.register_preprocessing_step(
            "health", 
            normalize_timestamps, 
            step_order=2
        )
        
        # Step 3: Standardize measurement units
        def standardize_health_units(data):
            unit_mappings = {
                "weight": {"kg": 1.0, "g": 0.001, "lb": 0.453592, "oz": 0.0283495},
                "height": {"cm": 1.0, "m": 100.0, "in": 2.54, "ft": 30.48},
                "temperature": {"celsius": 1.0, "fahrenheit": lambda x: (x - 32) * 5/9},
                "blood_glucose": {"mmol/L": 1.0, "mg/dL": 0.0555}
            }
            return standardize_units(data, unit_mappings)
        
        self.preprocessor.register_preprocessing_step(
            "health", 
            standardize_health_units, 
            step_order=3
        )
        
        # Step 4: Remove physiologically impossible values
        def remove_health_outliers(data):
            outlier_ranges = {
                "heart_rate": (30, 220),  # bpm
                "systolic_bp": (60, 250),  # mmHg
                "diastolic_bp": (40, 150),  # mmHg
                "temperature_celsius": (35, 42),  # °C
                "blood_glucose": (2.0, 25.0),  # mmol/L
                "weight_kg": (20, 300),  # kg
                "height_cm": (100, 250)  # cm
            }
            
            result = data.copy()
            for field, (min_val, max_val) in outlier_ranges.items():
                if field in result:
                    result = remove_outliers(result, field, min_val, max_val)
            
            return result
        
        self.preprocessor.register_preprocessing_step(
            "health", 
            remove_health_outliers, 
            step_order=4
        )
    
    def preprocess(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess health data"""
        return self.preprocessor.preprocess(health_data, "health")
    
    def preprocess_batch(self, health_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess a batch of health data"""
        return self.preprocessor.preprocess_batch(health_data_list, "health")


class FinancialDataPreprocessor:
    """Specialized preprocessor for financial data"""
    
    def __init__(self, main_preprocessor: DataPreprocessor):
        self.preprocessor = main_preprocessor
        self._register_steps()
        logger.info("Financial data preprocessor initialized")
    
    def _register_steps(self) -> None:
        """Register financial data preprocessing steps"""
        # Step 1: Clean missing values
        self.preprocessor.register_preprocessing_step(
            "financial", 
            clean_missing_values, 
            step_order=1
        )
        
        # Step 2: Normalize timestamps
        self.preprocessor.register_preprocessing_step(
            "financial", 
            normalize_timestamps, 
            step_order=2
        )
        
        # Step 3: Standardize currency
        def standardize_currency(data):
            # Currency conversion would use real exchange rates in production
            # Here we use fixed rates for demonstration
            currency_rates = {
                "USD": 1.0,
                "EUR": 1.1,
                "GBP": 1.3,
                "JPY": 0.0091,
                "CAD": 0.75,
                "AUD": 0.7
            }
            
            result = data.copy()
            if "amount" in result and "currency" in result:
                currency = result["currency"]
                if currency in currency_rates and currency != "USD":
                    result["amount"] = result["amount"] * currency_rates[currency]
                    result["currency"] = "USD"
                    result["original_amount"] = data["amount"]
                    result["original_currency"] = data["currency"]
            
            return result
        
        self.preprocessor.register_preprocessing_step(
            "financial", 
            standardize_currency, 
            step_order=3
        )
        
        # Step 4: Categorize transactions
        def categorize_transactions(data):
            # This would use more sophisticated rules or ML in production
            result = data.copy()
            
            if "description" in result and "category" not in result:
                description = result["description"].lower()
                
                # Simple keyword-based categorization
                categories = {
                    "food": ["restaurant", "cafe", "grocery", "food", "meal"],
                    "transport": ["uber", "lyft", "taxi", "train", "bus", "subway", "gas", "fuel"],
                    "housing": ["rent", "mortgage", "housing", "apartment", "utilities"],
                    "healthcare": ["doctor", "hospital", "pharmacy", "medical", "health"],
                    "entertainment": ["movie", "concert", "netflix", "spotify", "subscription"]
                }
                
                for category, keywords in categories.items():
                    if any(keyword in description for keyword in keywords):
                        result["category"] = category
                        break
                
                # Default category if no match
                if "category" not in result:
                    result["category"] = "other"
            
            return result
        
        self.preprocessor.register_preprocessing_step(
            "financial", 
            categorize_transactions, 
            step_order=4
        )
    
    def preprocess(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess financial data"""
        return self.preprocessor.preprocess(financial_data, "financial")
    
    def preprocess_batch(self, financial_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess a batch of financial data"""
        return self.preprocessor.preprocess_batch(financial_data_list, "financial")


# Factory function to create specialized preprocessors
def create_data_preprocessor() -> Dict[str, Any]:
    """Create data preprocessor instances for different data types"""
    main_preprocessor = DataPreprocessor()
    
    # Create specialized preprocessors
    health_preprocessor = HealthDataPreprocessor(main_preprocessor)
    financial_preprocessor = FinancialDataPreprocessor(main_preprocessor)
    
    # Return all preprocessors
    return {
        "main": main_preprocessor,
        "health": health_preprocessor,
        "financial": financial_preprocessor
    }
