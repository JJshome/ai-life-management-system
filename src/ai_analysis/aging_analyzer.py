# -*- coding: utf-8 -*-
"""
Aging Rate Analyzer Module

This module employs machine learning algorithms to estimate the user's biological age
and aging rate using electrochemical impedance measurements, genetic data, and lifestyle
factors. This helps in creating personalized aging-related recommendations.
"""

import logging
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class AgingRateAnalyzer:
    """Analyzes the user's aging rate and biological age"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model_type = "MachineLearningAging"
        logger.info("Aging Rate Analyzer initialized")
    
    def analyze_aging_rate(self, 
                          user_id: str, 
                          impedance_data: Dict[str, Any],
                          health_data: Optional[Dict[str, Any]] = None,
                          genetic_data: Optional[Dict[str, Any]] = None,
                          lifestyle_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the user's aging rate and biological age
        
        Args:
            user_id: User identifier
            impedance_data: Electrochemical impedance measurements
            health_data: Current health measurements (optional)
            genetic_data: Genetic information (optional)
            lifestyle_data: Lifestyle information (optional)
            
        Returns:
            Dict containing aging analysis results
        """
        logger.info(f"Analyzing aging rate for user {user_id}")
        
        # Prepare input data
        input_data = self._prepare_input_data(
            impedance_data, health_data, genetic_data, lifestyle_data
        )
        
        try:
            # Use the latest aging analysis model
            results = self.model_manager.predict_with_latest(self.model_type, input_data)
            
            # Enhance results with additional information
            enhanced_results = self._enhance_results(
                results, impedance_data, health_data, lifestyle_data
            )
            
            logger.info(f"Completed aging rate analysis for user {user_id}")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error analyzing aging rate: {e}")
            # Return basic results in case of error
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def _prepare_input_data(self, 
                           impedance_data: Dict[str, Any],
                           health_data: Optional[Dict[str, Any]] = None,
                           genetic_data: Optional[Dict[str, Any]] = None,
                           lifestyle_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare and normalize input data for the model
        
        Args:
            impedance_data: Electrochemical impedance measurements
            health_data: Current health measurements (optional)
            genetic_data: Genetic information (optional)
            lifestyle_data: Lifestyle information (optional)
            
        Returns:
            Normalized and prepared input data
        """
        # Start with impedance data
        input_data = {}
        
        # Extract impedance features
        if "frequency_scan" in impedance_data and isinstance(impedance_data["frequency_scan"], list):
            scan_data = impedance_data["frequency_scan"]
            frequencies = []
            impedances = []
            phases = []
            
            for data_point in scan_data:
                if "frequency" in data_point and "impedance" in data_point and "phase" in data_point:
                    frequencies.append(data_point["frequency"])
                    impedances.append(data_point["impedance"])
                    phases.append(data_point["phase"])
            
            # Calculate impedance features
            if frequencies and impedances and phases:
                # Frequency range features
                input_data["min_frequency"] = min(frequencies)
                input_data["max_frequency"] = max(frequencies)
                input_data["frequency_range"] = max(frequencies) - min(frequencies)
                
                # Impedance features
                input_data["min_impedance"] = min(impedances)
                input_data["max_impedance"] = max(impedances)
                input_data["avg_impedance"] = sum(impedances) / len(impedances)
                input_data["impedance_range"] = max(impedances) - min(impedances)
                
                # Phase features
                input_data["min_phase"] = min(phases)
                input_data["max_phase"] = max(phases)
                input_data["avg_phase"] = sum(phases) / len(phases)
                input_data["phase_range"] = max(phases) - min(phases)
                
                # Calculate impedance slope (simplified linear regression)
                n = len(frequencies)
                x = np.array(frequencies)
                y = np.array(impedances)
                
                impedance_slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
                input_data["impedance_slope"] = impedance_slope
                
                # Calculate phase slope
                y_phase = np.array(phases)
                phase_slope = (n * np.sum(x * y_phase) - np.sum(x) * np.sum(y_phase)) / (n * np.sum(x**2) - np.sum(x)**2)
                input_data["phase_slope"] = phase_slope
        
        # Add individual impedance measurements if available
        for freq in [100, 200, 500, 1000, 2000, 5000]:
            freq_key = f"freq_{freq}"
            if freq_key in impedance_data:
                input_data[f"impedance_{freq}"] = impedance_data[freq_key].get("impedance", 0)
                input_data[f"phase_{freq}"] = impedance_data[freq_key].get("phase", 0)
        
        # Add chronological age
        if "chronological_age" in impedance_data:
            input_data["chronological_age"] = impedance_data["chronological_age"]
        elif health_data and "age" in health_data:
            input_data["chronological_age"] = health_data["age"]
        else:
            input_data["chronological_age"] = 0  # Default value, should be replaced
        
        # Add health data features if available
        if health_data:
            # Add relevant health metrics
            for key in ["heart_rate", "weight", "height", "bmi"]:
                if key in health_data:
                    input_data[key] = health_data[key]
            
            # Add blood pressure if available
            if "blood_pressure" in health_data and isinstance(health_data["blood_pressure"], dict):
                bp = health_data["blood_pressure"]
                if "systolic" in bp:
                    input_data["systolic_bp"] = bp["systolic"]
                if "diastolic" in bp:
                    input_data["diastolic_bp"] = bp["diastolic"]
            
            # Add other relevant health metrics
            for key in ["blood_glucose", "cholesterol", "hdl", "ldl", "triglycerides"]:
                if key in health_data:
                    input_data[key] = health_data[key]
        
        # Add genetic data features if available
        if genetic_data:
            # Add genetic risk scores or specific markers
            for key, value in genetic_data.items():
                if key.startswith("genetic_"):
                    input_data[key] = value
            
            # Add longevity markers if available
            if "longevity_markers" in genetic_data and isinstance(genetic_data["longevity_markers"], dict):
                for marker, value in genetic_data["longevity_markers"].items():
                    input_data[f"longevity_{marker}"] = value
        
        # Add lifestyle data features if available
        if lifestyle_data:
            # Physical activity
            if "physical_activity" in lifestyle_data:
                pa = lifestyle_data["physical_activity"]
                if isinstance(pa, dict):
                    input_data["activity_minutes_weekly"] = pa.get("minutes_weekly", 0)
                    input_data["activity_intensity"] = pa.get("intensity_score", 0)
                elif isinstance(pa, (int, float)):
                    input_data["activity_score"] = pa
            
            # Sleep quality
            if "sleep" in lifestyle_data:
                sleep = lifestyle_data["sleep"]
                if isinstance(sleep, dict):
                    input_data["sleep_hours"] = sleep.get("average_hours", 0)
                    input_data["sleep_quality"] = sleep.get("quality_score", 0)
                elif isinstance(sleep, (int, float)):
                    input_data["sleep_score"] = sleep
            
            # Diet quality
            if "diet" in lifestyle_data:
                diet = lifestyle_data["diet"]
                if isinstance(diet, dict):
                    input_data["diet_quality"] = diet.get("quality_score", 0)
                    input_data["diet_vegetable_servings"] = diet.get("vegetable_servings", 0)
                    input_data["diet_fruit_servings"] = diet.get("fruit_servings", 0)
                elif isinstance(diet, (int, float)):
                    input_data["diet_score"] = diet
            
            # Stress level
            if "stress" in lifestyle_data:
                input_data["stress_level"] = lifestyle_data["stress"]
            
            # Smoking status
            if "smoking" in lifestyle_data:
                input_data["is_smoker"] = 1 if lifestyle_data["smoking"] else 0
            
            # Alcohol consumption
            if "alcohol" in lifestyle_data:
                input_data["alcohol_units_weekly"] = lifestyle_data["alcohol"]
        
        # Add timestamp
        input_data["analysis_timestamp"] = time.time()
        
        return input_data
    
    def _enhance_results(self, 
                        model_results: Dict[str, Any], 
                        impedance_data: Dict[str, Any],
                        health_data: Optional[Dict[str, Any]] = None,
                        lifestyle_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance model results with additional insights and explanations
        
        Args:
            model_results: Raw model prediction results
            impedance_data: Original impedance data
            health_data: Health data (optional)
            lifestyle_data: Lifestyle data (optional)
            
        Returns:
            Enhanced results with additional context and explanations
        """
        enhanced = model_results.copy()
        
        # Add timestamp if not present
        if "prediction_time" not in enhanced:
            enhanced["prediction_time"] = time.time()
        
        # Add chronological age if not present
        chronological_age = 0
        if "chronological_age" in impedance_data:
            chronological_age = impedance_data["chronological_age"]
        elif health_data and "age" in health_data:
            chronological_age = health_data["age"]
        
        if chronological_age > 0 and "biological_age" in enhanced:
            enhanced["age_difference"] = enhanced["biological_age"] - chronological_age
            
            # Add interpretation of age difference
            if enhanced["age_difference"] <= -5:
                enhanced["age_difference_interpretation"] = "Your biological age is significantly lower than your chronological age, suggesting excellent aging indicators."
            elif enhanced["age_difference"] < 0:
                enhanced["age_difference_interpretation"] = "Your biological age is lower than your chronological age, suggesting good aging indicators."
            elif enhanced["age_difference"] == 0:
                enhanced["age_difference_interpretation"] = "Your biological age matches your chronological age, suggesting normal aging indicators."
            elif enhanced["age_difference"] <= 5:
                enhanced["age_difference_interpretation"] = "Your biological age is slightly higher than your chronological age, suggesting some aging concerns."
            else:
                enhanced["age_difference_interpretation"] = "Your biological age is significantly higher than your chronological age, suggesting serious aging concerns."
        
        # Add aging rate interpretation
        if "aging_rate" in enhanced:
            rate = enhanced["aging_rate"]
            
            if rate < 0.8:
                enhanced["aging_rate_interpretation"] = "You are aging significantly slower than average."
            elif rate < 0.95:
                enhanced["aging_rate_interpretation"] = "You are aging somewhat slower than average."
            elif rate <= 1.05:
                enhanced["aging_rate_interpretation"] = "You are aging at an average rate."
            elif rate <= 1.2:
                enhanced["aging_rate_interpretation"] = "You are aging somewhat faster than average."
            else:
                enhanced["aging_rate_interpretation"] = "You are aging significantly faster than average."
        
        # Add contributing factors
        contributing_factors = []
        
        # Analyze impedance data for clues
        if "impedance_slope" in model_results:
            slope = model_results["impedance_slope"]
            if slope > 0.5:
                contributing_factors.append({
                    "factor": "Cellular membrane health",
                    "impact": "positive",
                    "description": "Your cellular membrane health appears to be good based on impedance patterns."
                })
            elif slope < -0.5:
                contributing_factors.append({
                    "factor": "Cellular membrane health",
                    "impact": "negative",
                    "description": "Your cellular membrane health may be compromised based on impedance patterns."
                })
        
        # Analyze health data for clues if available
        if health_data:
            # Check blood pressure
            if "blood_pressure" in health_data and isinstance(health_data["blood_pressure"], dict):
                bp = health_data["blood_pressure"]
                if "systolic" in bp and "diastolic" in bp:
                    systolic = bp["systolic"]
                    diastolic = bp["diastolic"]
                    
                    if systolic < 120 and diastolic < 80:
                        contributing_factors.append({
                            "factor": "Blood pressure",
                            "impact": "positive",
                            "description": "Your optimal blood pressure is beneficial for vascular aging."
                        })
                    elif systolic > 140 or diastolic > 90:
                        contributing_factors.append({
                            "factor": "Blood pressure",
                            "impact": "negative",
                            "description": "Elevated blood pressure may be accelerating vascular aging."
                        })
            
            # Check BMI
            if "bmi" in health_data:
                bmi = health_data["bmi"]
                if 18.5 <= bmi <= 24.9:
                    contributing_factors.append({
                        "factor": "Body Mass Index",
                        "impact": "positive",
                        "description": "Your healthy weight is beneficial for metabolic aging."
                    })
                elif bmi >= 30:
                    contributing_factors.append({
                        "factor": "Body Mass Index",
                        "impact": "negative",
                        "description": "Elevated BMI may be accelerating metabolic aging."
                    })
            
            # Check other biomarkers
            if "cholesterol" in health_data and health_data["cholesterol"] > 240:
                contributing_factors.append({
                    "factor": "Cholesterol",
                    "impact": "negative",
                    "description": "Elevated cholesterol may be accelerating cardiovascular aging."
                })
            
            if "blood_glucose" in health_data and health_data["blood_glucose"] > 5.7:
                contributing_factors.append({
                    "factor": "Blood glucose",
                    "impact": "negative",
                    "description": "Elevated blood glucose may be contributing to accelerated aging."
                })
        
        # Analyze lifestyle data for clues if available
        if lifestyle_data:
            # Physical activity
            if "physical_activity" in lifestyle_data:
                pa = lifestyle_data["physical_activity"]
                if isinstance(pa, dict) and pa.get("minutes_weekly", 0) >= 150:
                    contributing_factors.append({
                        "factor": "Physical activity",
                        "impact": "positive",
                        "description": "Your regular physical activity is slowing the aging process."
                    })
                elif isinstance(pa, dict) and pa.get("minutes_weekly", 0) < 60:
                    contributing_factors.append({
                        "factor": "Physical activity",
                        "impact": "negative",
                        "description": "Insufficient physical activity may be accelerating aging."
                    })
            
            # Sleep
            if "sleep" in lifestyle_data:
                sleep = lifestyle_data["sleep"]
                if isinstance(sleep, dict):
                    hours = sleep.get("average_hours", 0)
                    quality = sleep.get("quality_score", 0)
                    
                    if hours >= 7 and quality >= 0.7:
                        contributing_factors.append({
                            "factor": "Sleep",
                            "impact": "positive",
                            "description": "Your healthy sleep patterns are beneficial for cellular repair."
                        })
                    elif hours < 6 or quality < 0.5:
                        contributing_factors.append({
                            "factor": "Sleep",
                            "impact": "negative",
                            "description": "Poor sleep may be accelerating cellular aging."
                        })
            
            # Smoking
            if "smoking" in lifestyle_data and lifestyle_data["smoking"]:
                contributing_factors.append({
                    "factor": "Smoking",
                    "impact": "negative",
                    "description": "Smoking significantly accelerates biological aging through oxidative stress."
                })
            
            # Alcohol
            if "alcohol" in lifestyle_data:
                alcohol = lifestyle_data["alcohol"]
                if alcohol > 14:  # More than 14 units per week
                    contributing_factors.append({
                        "factor": "Alcohol consumption",
                        "impact": "negative",
                        "description": "Excessive alcohol consumption may be accelerating aging."
                    })
            
            # Diet
            if "diet" in lifestyle_data:
                diet = lifestyle_data["diet"]
                if isinstance(diet, dict) and diet.get("quality_score", 0) >= 0.8:
                    contributing_factors.append({
                        "factor": "Diet",
                        "impact": "positive",
                        "description": "Your nutritious diet is supporting healthy aging."
                    })
                elif isinstance(diet, dict) and diet.get("quality_score", 0) < 0.4:
                    contributing_factors.append({
                        "factor": "Diet",
                        "impact": "negative",
                        "description": "Poor diet quality may be accelerating aging processes."
                    })
            
            # Stress
            if "stress" in lifestyle_data and lifestyle_data["stress"] > 7:
                contributing_factors.append({
                    "factor": "Stress",
                    "impact": "negative",
                    "description": "High stress levels may be accelerating biological aging through chronic inflammation."
                })
        
        enhanced["contributing_factors"] = contributing_factors
        
        # Add recommendations
        recommendations = []
        
        # Generate general recommendations based on biological age
        if "biological_age" in enhanced and "chronological_age" in enhanced:
            if enhanced["biological_age"] > enhanced["chronological_age"]:
                recommendations.append({
                    "action": "Comprehensive health assessment",
                    "description": "Consider a comprehensive health assessment to identify specific aging factors.",
                    "priority": "high"
                })
        
        # Generate specific recommendations based on contributing factors
        for factor in contributing_factors:
            if factor["impact"] == "negative":
                if factor["factor"] == "Physical activity":
                    recommendations.append({
                        "action": "Increase physical activity",
                        "description": "Aim for at least 150 minutes of moderate exercise weekly.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Sleep":
                    recommendations.append({
                        "action": "Improve sleep habits",
                        "description": "Aim for 7-8 hours of quality sleep and maintain a consistent schedule.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Diet":
                    recommendations.append({
                        "action": "Improve diet quality",
                        "description": "Increase intake of vegetables, fruits, whole grains, and lean proteins.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Stress":
                    recommendations.append({
                        "action": "Implement stress management practices",
                        "description": "Consider meditation, deep breathing, or other relaxation techniques.",
                        "priority": "medium"
                    })
                elif factor["factor"] == "Smoking":
                    recommendations.append({
                        "action": "Quit smoking",
                        "description": "Consider a smoking cessation program or consult a healthcare provider.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Alcohol consumption":
                    recommendations.append({
                        "action": "Reduce alcohol consumption",
                        "description": "Limit alcohol to no more than 7 drinks per week.",
                        "priority": "medium"
                    })
                elif factor["factor"] == "Blood pressure":
                    recommendations.append({
                        "action": "Manage blood pressure",
                        "description": "Consider dietary changes, stress reduction, and consult a healthcare provider.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Body Mass Index":
                    recommendations.append({
                        "action": "Achieve healthy weight",
                        "description": "Focus on balanced nutrition and regular physical activity.",
                        "priority": "high"
                    })
                elif factor["factor"] == "Cholesterol":
                    recommendations.append({
                        "action": "Improve cholesterol levels",
                        "description": "Consider dietary changes and consult a healthcare provider.",
                        "priority": "medium"
                    })
                elif factor["factor"] == "Blood glucose":
                    recommendations.append({
                        "action": "Manage blood glucose",
                        "description": "Consider dietary changes and consult a healthcare provider.",
                        "priority": "medium"
                    })
                elif factor["factor"] == "Cellular membrane health":
                    recommendations.append({
                        "action": "Support cellular health",
                        "description": "Focus on antioxidant-rich foods and consider appropriate supplements.",
                        "priority": "medium"
                    })
        
        enhanced["recommendations"] = recommendations
        
        return enhanced
    
    def track_aging_trends(self, 
                         user_id: str, 
                         aging_history: List[Dict[str, Any]],
                         time_period_days: int = 365) -> Dict[str, Any]:
        """
        Analyze aging trends over time
        
        Args:
            user_id: User identifier
            aging_history: Historical aging analysis data points
            time_period_days: Time period to analyze in days
            
        Returns:
            Dict containing trend analysis results
        """
        if not aging_history or len(aging_history) < 2:
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": "Insufficient historical data for trend analysis",
                "status": "error"
            }
        
        logger.info(f"Analyzing aging trends for user {user_id} over {time_period_days} days")
        
        try:
            # Sort history by timestamp
            sorted_history = sorted(aging_history, key=lambda x: x.get("timestamp", 0))
            
            # Calculate trends for biological age and aging rate
            trends = {}
            
            # Analyze biological age trend
            if all("biological_age" in data for data in sorted_history):
                bio_age_values = [data["biological_age"] for data in sorted_history]
                bio_age_trend = self._calculate_trend(bio_age_values)
                
                # Calculate expected trend based on time elapsed
                first_timestamp = sorted_history[0].get("timestamp", 0)
                last_timestamp = sorted_history[-1].get("timestamp", 0)
                time_elapsed_years = (last_timestamp - first_timestamp) / (365 * 24 * 60 * 60)
                expected_change = time_elapsed_years  # 1 year should increase biological age by 1 year
                
                # Compare actual change to expected change
                actual_change = bio_age_trend[1]
                relative_aging_rate = actual_change / expected_change if expected_change > 0 else 1.0
                
                trends["biological_age"] = {
                    "direction": bio_age_trend[0],
                    "magnitude": bio_age_trend[1],
                    "expected_change": expected_change,
                    "relative_aging_rate": relative_aging_rate,
                    "values": bio_age_values,
                    "description": f"Biological age is {bio_age_trend[0]} by approximately {bio_age_trend[1]:.1f} years (expected: {expected_change:.1f} years)."
                }
            
            # Analyze aging rate trend
            if all("aging_rate" in data for data in sorted_history):
                aging_rate_values = [data["aging_rate"] for data in sorted_history]
                aging_rate_trend = self._calculate_trend(aging_rate_values)
                trends["aging_rate"] = {
                    "direction": aging_rate_trend[0],
                    "magnitude": aging_rate_trend[1],
                    "values": aging_rate_values,
                    "description": f"Aging rate is {aging_rate_trend[0]} by approximately {aging_rate_trend[1]:.2f}."
                }
            
            # Analyze impedance trends
            impedance_trends = {}
            for freq in [100, 200, 500, 1000, 2000, 5000]:
                key = f"impedance_{freq}"
                if all(key in data for data in sorted_history):
                    values = [data[key] for data in sorted_history]
                    trend = self._calculate_trend(values)
                    impedance_trends[key] = {
                        "direction": trend[0],
                        "magnitude": trend[1],
                        "values": values
                    }
            
            if impedance_trends:
                trends["impedance"] = impedance_trends
            
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "time_period_days": time_period_days,
                "data_points": len(sorted_history),
                "trends": trends,
                "overall_assessment": self._assess_overall_trends(trends),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing aging trends: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """
        Calculate trend direction and magnitude from a series of values
        
        Args:
            values: List of numerical values
            
        Returns:
            Tuple of (direction, magnitude) where direction is "increasing", 
            "decreasing", or "stable"
        """
        if len(values) < 2:
            return ("stable", 0.0)
        
        # Simple linear regression to find slope
        n = len(values)
        x = np.array(range(n))
        y = np.array(values)
        
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        
        # Determine trend direction and magnitude
        if abs(slope) < 0.01:
            return ("stable", 0.0)
        elif slope > 0:
            return ("increasing", slope * n)  # Magnitude over the entire period
        else:
            return ("decreasing", -slope * n)  # Magnitude over the entire period
    
    def _assess_overall_trends(self, trends: Dict[str, Dict[str, Any]]) -> str:
        """
        Provide an overall assessment of aging trends
        
        Args:
            trends: Dictionary of trend analysis for each parameter
            
        Returns:
            String containing overall assessment
        """
        improving = False
        worsening = False
        
        # Check biological age trend
        if "biological_age" in trends:
            bio_age_trend = trends["biological_age"]
            
            if "relative_aging_rate" in bio_age_trend:
                rate = bio_age_trend["relative_aging_rate"]
                
                if rate < 0.9:
                    improving = True
                elif rate > 1.1:
                    worsening = True
        
        # Check aging rate trend
        if "aging_rate" in trends:
            aging_rate_trend = trends["aging_rate"]
            
            if aging_rate_trend["direction"] == "decreasing":
                improving = True
            elif aging_rate_trend["direction"] == "increasing":
                worsening = True
        
        # Generate overall assessment
        if improving and not worsening:
            return "Your aging trends are positive, suggesting that your current lifestyle and health practices are effectively slowing the aging process."
        elif worsening and not improving:
            return "Your aging trends suggest accelerated aging. Consider reviewing the recommendations to address specific aging factors."
        elif improving and worsening:
            return "Your aging trends show mixed signals. While some aspects are improving, others may need attention."
        else:
            return "Your aging trends are stable. Continue with your current health practices and consider the recommendations for potential improvements."


# Factory function to create aging analyzer
def create_aging_analyzer(model_manager: ModelManager) -> AgingRateAnalyzer:
    """Create an aging rate analyzer with the given model manager"""
    return AgingRateAnalyzer(model_manager)
