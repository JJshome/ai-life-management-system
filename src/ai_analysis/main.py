# -*- coding: utf-8 -*-
"""
AI Analysis Module Main Entry Point

This module serves as the main entry point for the AI Analysis Module (120).
It initializes all analyzer components and provides a unified interface for
analyzing data from various sources.
"""

import logging
import time
import json
import os
from typing import Dict, Any, List, Optional, Tuple

from .model_manager import ModelManager, create_model_manager
from .health_analyzer import HealthStateAnalyzer, create_health_analyzer
from .aging_analyzer import AgingRateAnalyzer, create_aging_analyzer
from .integration_engine import IntegrationEngine, create_integration_engine

logger = logging.getLogger(__name__)


class AIAnalysisModule:
    """Main class for the AI Analysis Module (120)"""
    
    def __init__(self, models_directory: str = "models"):
        """Initialize the AI Analysis Module with all components"""
        # Initialize model manager
        self.model_manager = create_model_manager(models_directory)
        
        # Initialize analyzers
        self.health_analyzer = create_health_analyzer(self.model_manager)
        self.aging_analyzer = create_aging_analyzer(self.model_manager)
        
        # Initialize integration engine
        self.integration_engine = create_integration_engine(self.model_manager)
        
        logger.info("AI Analysis Module initialized")
    
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
        logger.info(f"Starting health state analysis for user {user_id}")
        
        try:
            results = self.health_analyzer.analyze_health_state(
                user_id, health_data, medical_history
            )
            
            logger.info(f"Completed health state analysis for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in health state analysis: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
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
        logger.info(f"Starting health trends analysis for user {user_id}")
        
        try:
            results = self.health_analyzer.track_health_trends(
                user_id, health_history, time_period_days
            )
            
            logger.info(f"Completed health trends analysis for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in health trends analysis: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
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
        logger.info(f"Starting aging rate analysis for user {user_id}")
        
        try:
            results = self.aging_analyzer.analyze_aging_rate(
                user_id, impedance_data, health_data, genetic_data, lifestyle_data
            )
            
            logger.info(f"Completed aging rate analysis for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in aging rate analysis: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
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
        logger.info(f"Starting aging trends analysis for user {user_id}")
        
        try:
            results = self.aging_analyzer.track_aging_trends(
                user_id, aging_history, time_period_days
            )
            
            logger.info(f"Completed aging trends analysis for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in aging trends analysis: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def integrate_insights(self, 
                          user_id: str,
                          health_insights: Optional[Dict[str, Any]] = None,
                          aging_insights: Optional[Dict[str, Any]] = None,
                          disease_insights: Optional[Dict[str, Any]] = None,
                          lifestyle_insights: Optional[Dict[str, Any]] = None,
                          financial_insights: Optional[Dict[str, Any]] = None,
                          social_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Integrate insights from all analysis modules
        
        Args:
            user_id: User identifier
            health_insights: Results from health state analysis
            aging_insights: Results from aging rate analysis
            disease_insights: Results from disease risk analysis
            lifestyle_insights: Results from lifestyle analysis
            financial_insights: Results from financial analysis
            social_insights: Results from social relationship analysis
            
        Returns:
            Dict containing integrated insights and recommendations
        """
        logger.info(f"Starting insight integration for user {user_id}")
        
        try:
            results = self.integration_engine.integrate_insights(
                user_id, health_insights, aging_insights, disease_insights,
                lifestyle_insights, financial_insights, social_insights
            )
            
            logger.info(f"Completed insight integration for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in insight integration: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def analyze_complete_profile(self, 
                               user_id: str,
                               health_data: Dict[str, Any],
                               impedance_data: Dict[str, Any],
                               medical_history: Optional[Dict[str, Any]] = None,
                               genetic_data: Optional[Dict[str, Any]] = None,
                               lifestyle_data: Optional[Dict[str, Any]] = None,
                               financial_data: Optional[Dict[str, Any]] = None,
                               social_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a complete analysis of the user's profile
        
        This is a convenience method that runs all analysis modules and integrates the results
        
        Args:
            user_id: User identifier
            health_data: Current health measurements and sensor data
            impedance_data: Electrochemical impedance measurements
            medical_history: User's medical history (optional)
            genetic_data: Genetic information (optional)
            lifestyle_data: Lifestyle information (optional)
            financial_data: Financial information (optional)
            social_data: Social relationship information (optional)
            
        Returns:
            Dict containing comprehensive analysis results and recommendations
        """
        logger.info(f"Starting complete profile analysis for user {user_id}")
        
        try:
            # Analyze health state
            health_insights = self.analyze_health_state(
                user_id, health_data, medical_history
            )
            
            # Analyze aging rate
            aging_insights = self.analyze_aging_rate(
                user_id, impedance_data, health_data, genetic_data, lifestyle_data
            )
            
            # Placeholder for disease risk analysis
            disease_insights = {
                "user_id": user_id,
                "analysis_time": time.time(),
                "overall_risk": 0.2,  # Placeholder value
                "disease_risks": {
                    "cardiovascular_disease": 0.15,
                    "diabetes_type_2": 0.08,
                    "alzheimers": 0.05
                },
                "preventable_risks": ["cardiovascular_disease", "diabetes_type_2"],
                "status": "success"
            }
            
            # Placeholder for lifestyle analysis
            if not lifestyle_data:
                lifestyle_insights = {
                    "user_id": user_id,
                    "analysis_time": time.time(),
                    "overall_score": 70,  # Placeholder value
                    "physical_activity": {
                        "minutes_weekly": 120,
                        "intensity_score": 0.6
                    },
                    "sleep": {
                        "average_hours": 7,
                        "quality_score": 0.7
                    },
                    "diet": {
                        "quality_score": 0.65,
                        "vegetable_servings": 3,
                        "fruit_servings": 2
                    },
                    "stress": 6,  # Scale of 1-10
                    "smoking": False,
                    "alcohol": 5,  # Units per week
                    "improvement_potential": 0.3,
                    "status": "success"
                }
            else:
                lifestyle_insights = lifestyle_data
            
            # Placeholder for financial analysis
            if not financial_data:
                financial_insights = {
                    "user_id": user_id,
                    "analysis_time": time.time(),
                    "financial_health_score": 65,  # Placeholder value
                    "savings_adequacy": 0.6,
                    "retirement_readiness": 0.55,
                    "healthcare_preparedness": 0.5,
                    "concerns": ["retirement_savings", "healthcare_costs"],
                    "status": "success"
                }
            else:
                financial_insights = financial_data
            
            # Placeholder for social relationship analysis
            if not social_data:
                social_insights = {
                    "user_id": user_id,
                    "analysis_time": time.time(),
                    "network_strength": 75,  # Placeholder value
                    "support_level": 0.7,
                    "connection_quality": 0.8,
                    "connection_types": ["family", "friends"],
                    "activity_level": 0.6,
                    "status": "success"
                }
            else:
                social_insights = social_data
            
            # Integrate all insights
            integrated_results = self.integrate_insights(
                user_id, health_insights, aging_insights, disease_insights,
                lifestyle_insights, financial_insights, social_insights
            )
            
            # Compile complete analysis results
            complete_results = {
                "user_id": user_id,
                "analysis_time": time.time(),
                "health_analysis": health_insights,
                "aging_analysis": aging_insights,
                "disease_risk_analysis": disease_insights,
                "lifestyle_analysis": lifestyle_insights,
                "financial_analysis": financial_insights,
                "social_analysis": social_insights,
                "integrated_analysis": integrated_results,
                "status": "success"
            }
            
            logger.info(f"Completed comprehensive profile analysis for user {user_id}")
            return complete_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive profile analysis: {e}")
            return {
                "user_id": user_id,
                "analysis_time": time.time(),
                "error": str(e),
                "status": "error"
            }


# Create an AI analysis module
def create_ai_analysis_module(models_directory: str = "models") -> AIAnalysisModule:
    """Create an AI analysis module with the specified models directory"""
    return AIAnalysisModule(models_directory)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create AI analysis module
    ai_module = create_ai_analysis_module()
    
    # Example health data
    health_data = {
        "heart_rate": 72,
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "weight": 75,  # kg
        "height": 175,  # cm
        "bmi": 24.5,
        "blood_glucose": 5.2,  # mmol/L
        "cholesterol": 185,  # mg/dL
        "age": 45
    }
    
    # Example impedance data
    impedance_data = {
        "chronological_age": 45,
        "frequency_scan": [
            {"frequency": 100, "impedance": 1010, "phase": 45},
            {"frequency": 200, "impedance": 980, "phase": 43},
            {"frequency": 500, "impedance": 920, "phase": 40},
            {"frequency": 1000, "impedance": 850, "phase": 35},
            {"frequency": 2000, "impedance": 780, "phase": 30},
            {"frequency": 5000, "impedance": 650, "phase": 25}
        ]
    }
    
    # Analyze health state
    health_results = ai_module.analyze_health_state("user123", health_data)
    print(f"Health analysis completed: {health_results['status']}")
    
    # Analyze aging rate
    aging_results = ai_module.analyze_aging_rate("user123", impedance_data, health_data)
    print(f"Aging analysis completed: {aging_results['status']}")
    
    # Perform complete profile analysis
    complete_results = ai_module.analyze_complete_profile("user123", health_data, impedance_data)
    print(f"Complete profile analysis completed: {complete_results['status']}")
    
    # Save example results to file
    results_dir = os.path.join(os.path.dirname(__file__), "../../examples/analysis_results")
    os.makedirs(results_dir, exist_ok=True)
    
    with open(os.path.join(results_dir, "health_analysis_example.json"), 'w') as f:
        json.dump(health_results, f, indent=2)
    
    with open(os.path.join(results_dir, "aging_analysis_example.json"), 'w') as f:
        json.dump(aging_results, f, indent=2)
    
    with open(os.path.join(results_dir, "complete_analysis_example.json"), 'w') as f:
        json.dump(complete_results, f, indent=2)
