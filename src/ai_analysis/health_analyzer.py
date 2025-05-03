# -*- coding: utf-8 -*-
"""
Health State Analyzer Module

This module uses deep learning models to analyze the user's overall health state
based on sensor data, medical records, and manually entered health information.
It identifies potential health issues and tracks changes over time.
"""

import logging
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class HealthStateAnalyzer:
    """Analyzes the user's overall health state using deep learning models"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model_type = "DeepLearningHealth"
        logger.info("Health State Analyzer initialized")
    
    def analyze_health_state(self, 
                            user_id: str, 
                            health_data: Dict[str, Any],
                            medical_history: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the user's overall health state
        
        Args:
            user_id: User identifier
            health_data: Current health measurements and sensor data
            medical_history: User's medical history (optional)
            
        Returns:
            Dict containing health state analysis results
        """
        logger.info(f"Analyzing health state for user {user_id}")
        
        # Prepare input data
        input_data = self._prepare_input_data(health_data, medical_history)
        
        try:
            # Use the latest health analysis model
            results = self.model_manager.predict_with_latest(self.model_type, input_data)
            
            # Enhance results with additional information
            enhanced_results = self._enhance_results(results, health_data)
            
            logger.info(f"Completed health state analysis for user {user_id}")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error analyzing health state: {e}")
            # Return basic results in case of error
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def _prepare_input_data(self, 
                          health_data: Dict[str, Any],
                          medical_history: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare and normalize input data for the model
        
        Args:
            health_data: Current health measurements and sensor data
            medical_history: User's medical history (optional)
            
        Returns:
            Normalized and prepared input data
        """
        # Start with current health data
        input_data = health_data.copy()
        
        # Add medical history if available
        if medical_history:
            # Extract relevant features from medical history
            # In a real implementation, this would be more sophisticated
            input_data["has_chronic_conditions"] = len(medical_history.get("chronic_conditions", [])) > 0
            input_data["medication_count"] = len(medical_history.get("medications", []))
            input_data["has_family_history"] = any(medical_history.get("family_history", {}).values())
        
        # Normalize certain values
        if "heart_rate" in input_data:
            # Normalize heart rate to 0-1 range (assuming normal range is 60-100)
            hr = input_data["heart_rate"]
            input_data["heart_rate_normalized"] = max(0, min(1, (hr - 40) / 100))
        
        if "blood_pressure" in input_data and isinstance(input_data["blood_pressure"], dict):
            bp = input_data["blood_pressure"]
            # Normalize systolic (assuming normal range is 90-140)
            if "systolic" in bp:
                input_data["systolic_normalized"] = max(0, min(1, (bp["systolic"] - 90) / 70))
            # Normalize diastolic (assuming normal range is a60-90)
            if "diastolic" in bp:
                input_data["diastolic_normalized"] = max(0, min(1, (bp["diastolic"] - 60) / 40))
        
        if "blood_glucose" in input_data:
            # Normalize blood glucose (assuming normal range is 4-7 mmol/L)
            bg = input_data["blood_glucose"]
            input_data["blood_glucose_normalized"] = max(0, min(1, (bg - 4) / 6))
        
        # Add timestamp
        input_data["analysis_timestamp"] = time.time()
        
        return input_data
    
    def _enhance_results(self, 
                        model_results: Dict[str, Any], 
                        original_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance model results with additional insights and explanations
        
        Args:
            model_results: Raw model prediction results
            original_data: Original input data
            
        Returns:
            Enhanced results with additional context and explanations
        """
        enhanced = model_results.copy()
        
        # Add timestamp if not present
        if "prediction_time" not in enhanced:
            enhanced["prediction_time"] = time.time()
        
        # Add confidence levels if not present
        if "confidence" not in enhanced:
            enhanced["confidence"] = 0.85  # Default confidence
        
        # Add explanations for health status
        if "health_status" in enhanced:
            status = enhanced["health_status"]
            
            if status == "excellent":
                enhanced["explanation"] = "All health parameters are optimal."
            elif status == "good":
                enhanced["explanation"] = "Most health parameters are within normal ranges."
            elif status == "fair":
                enhanced["explanation"] = "Some health parameters show room for improvement."
            elif status == "poor":
                enhanced["explanation"] = "Several health parameters are outside normal ranges."
            elif status == "critical":
                enhanced["explanation"] = "Urgent attention required for multiple health parameters."
        
        # Add detailed analysis of specific health parameters
        enhanced["parameter_analysis"] = {}
        
        # Heart rate analysis
        if "heart_rate" in original_data:
            hr = original_data["heart_rate"]
            hr_analysis = {}
            
            if hr < 60:
                hr_analysis["status"] = "low"
                hr_analysis["description"] = "Heart rate is below normal range."
            elif hr <= 100:
                hr_analysis["status"] = "normal"
                hr_analysis["description"] = "Heart rate is within normal range."
            else:
                hr_analysis["status"] = "high"
                hr_analysis["description"] = "Heart rate is above normal range."
            
            enhanced["parameter_analysis"]["heart_rate"] = hr_analysis
        
        # Blood pressure analysis
        if "blood_pressure" in original_data and isinstance(original_data["blood_pressure"], dict):
            bp = original_data["blood_pressure"]
            bp_analysis = {}
            
            if "systolic" in bp and "diastolic" in bp:
                systolic = bp["systolic"]
                diastolic = bp["diastolic"]
                
                if systolic < 120 and diastolic < 80:
                    bp_analysis["status"] = "normal"
                    bp_analysis["description"] = "Blood pressure is within ideal range."
                elif systolic < 130 and diastolic < 85:
                    bp_analysis["status"] = "elevated"
                    bp_analysis["description"] = "Blood pressure is slightly elevated."
                elif systolic < 140 and diastolic < 90:
                    bp_analysis["status"] = "high_normal"
                    bp_analysis["description"] = "Blood pressure is at the high end of normal range."
                else:
                    bp_analysis["status"] = "high"
                    bp_analysis["description"] = "Blood pressure is above normal range."
                
                enhanced["parameter_analysis"]["blood_pressure"] = bp_analysis
        
        # Add recommendations based on analysis
        if "risk_factors" in enhanced:
            recommendations = []
            
            for risk in enhanced["risk_factors"]:
                if risk == "sedentary_lifestyle":
                    recommendations.append({
                        "action": "Increase daily physical activity",
                        "description": "Aim for at least 30 minutes of moderate exercise most days.",
                        "priority": "high"
                    })
                elif risk == "irregular_sleep":
                    recommendations.append({
                        "action": "Improve sleep consistency",
                        "description": "Maintain a regular sleep schedule with 7-8 hours per night.",
                        "priority": "medium"
                    })
                elif risk == "high_blood_pressure":
                    recommendations.append({
                        "action": "Monitor blood pressure regularly",
                        "description": "Consider dietary changes like reducing sodium intake.",
                        "priority": "high"
                    })
                elif risk == "elevated_glucose":
                    recommendations.append({
                        "action": "Monitor blood glucose levels",
                        "description": "Consider dietary changes to regulate blood sugar.",
                        "priority": "medium"
                    })
            
            enhanced["recommendations"] = recommendations
        
        return enhanced
    
    def track_health_trends(self, 
                          user_id: str, 
                          health_history: List[Dict[str, Any]],
                          time_period_days: int = 90) -> Dict[str, Any]:
        """
        Analyze health trends over time
        
        Args:
            user_id: User identifier
            health_history: Historical health data points
            time_period_days: Time period to analyze in days
            
        Returns:
            Dict containing trend analysis results
        """
        if not health_history or len(health_history) < 2:
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": "Insufficient historical data for trend analysis",
                "status": "error"
            }
        
        logger.info(f"Analyzing health trends for user {user_id} over {time_period_days} days")
        
        try:
            # Sort history by timestamp
            sorted_history = sorted(health_history, key=lambda x: x.get("timestamp", 0))
            
            # Calculate trends for various health parameters
            trends = {}
            
            # Analyze heart rate trend
            if all("heart_rate" in data for data in sorted_history):
                hr_values = [data["heart_rate"] for data in sorted_history]
                hr_trend = self._calculate_trend(hr_values)
                trends["heart_rate"] = {
                    "direction": hr_trend[0],
                    "magnitude": hr_trend[1],
                    "description": f"Heart rate is {hr_trend[0]} by approximately {hr_trend[1]:.1f} bpm.",
                    "values": hr_values
                }
            
            # Analyze blood pressure trend
            if all("blood_pressure" in data and isinstance(data["blood_pressure"], dict) for data in sorted_history):
                if all("systolic" in data["blood_pressure"] for data in sorted_history):
                    sys_values = [data["blood_pressure"]["systolic"] for data in sorted_history]
                    sys_trend = self._calculate_trend(sys_values)
                    trends["systolic_bp"] = {
                        "direction": sys_trend[0],
                        "magnitude": sys_trend[1],
                        "description": f"Systolic blood pressure is {sys_trend[0]} by approximately {sys_trend[1]:.1f} mmHg.",
                        "values": sys_values
                    }
                
                if all("diastolic" in data["blood_pressure"] for data in sorted_history):
                    dia_values = [data["blood_pressure"]["diastolic"] for data in sorted_history]
                    dia_trend = self._calculate_trend(dia_values)
                    trends["diastolic_bp"] = {
                        "direction": dia_trend[0],
                        "magnitude": dia_trend[1],
                        "description": f"Diastolic blood pressure is {dia_trend[0]} by approximately {dia_trend[1]:.1f} mmHg.",
                        "values": dia_values
                    }
            
            # Analyze weight trend
            if all("weight" in data for data in sorted_history):
                weight_values = [data["weight"] for data in sorted_history]
                weight_trend = self._calculate_trend(weight_values)
                trends["weight"] = {
                    "direction": weight_trend[0],
                    "magnitude": weight_trend[1],
                    "description": f"Weight is {weight_trend[0]} by approximately {weight_trend[1]:.1f} kg.",
                    "values": weight_values
                }
            
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
            logger.error(f"Error analyzing health trends: {e}")
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
        Provide an overall assessment of health trends
        
        Args:
            trends: Dictionary of trend analysis for each parameter
            
        Returns:
            String containing overall assessment
        """
        improving_count = 0
        worsening_count = 0
        
        for param, trend_data in trends.items():
            direction = trend_data["direction"]
            
            if param == "heart_rate":
                # For heart rate, closer to normal range (60-100) is better
                avg_value = sum(trend_data["values"]) / len(trend_data["values"])
                if avg_value < 60 and direction == "increasing":
                    improving_count += 1
                elif avg_value > 100 and direction == "decreasing":
                    improving_count += 1
                elif 60 <= avg_value <= 100 and direction != "stable":
                    worsening_count += 1
            
            elif param in ["systolic_bp", "diastolic_bp"]:
                # For blood pressure, lower is generally better (within normal range)
                if direction == "decreasing":
                    improving_count += 1
                elif direction == "increasing":
                    worsening_count += 1
            
            elif param == "weight":
                # For weight, stability or slight decrease is usually better
                # (this is a simplification; ideal weight trends depend on many factors)
                if direction == "stable":
                    improving_count += 1
                elif direction == "decreasing":
                    avg_change = trend_data["magnitude"]
                    if avg_change < 5:  # Moderate weight loss
                        improving_count += 1
                    else:  # Rapid weight loss might be concerning
                        worsening_count += 1
                elif direction == "increasing":
                    worsening_count += 1
        
        # Generate overall assessment
        if improving_count > worsening_count:
            return "Overall health trends are positive. Continue with current health practices."
        elif improving_count < worsening_count:
            return "Some concerning health trends detected. Consider consulting a healthcare professional."
        else:
            return "Health trends are mixed or stable. Maintain focus on healthy lifestyle habits."


# Factory function to create health analyzer
def create_health_analyzer(model_manager: ModelManager) -> HealthStateAnalyzer:
    """Create a health state analyzer with the given model manager"""
    return HealthStateAnalyzer(model_manager)
