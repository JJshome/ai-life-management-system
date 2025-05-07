#!/usr/bin/env python3
"""
Simulation Runner for AI Life Management System

This script runs a complete simulation of the AI-based Life Management and 
Aging Preparation Decision System, generating synthetic data, performing AI analysis,
and visualizing the results.

Based on patented technology by Ucaretron Inc.
"""

import os
import json
import random
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from simulation.data_generator import DataGenerator
from simulation.predictor import LifePredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulation.log')
    ]
)

logger = logging.getLogger(__name__)


class SimulationRunner:
    """
    Main class to run the simulation of the AI Life Management System.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the simulation runner.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Set up paths
        self.output_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize data generator and predictor
        random_seed = self.config.get('random_seed')
        self.data_generator = DataGenerator(seed=random_seed)
        self.predictor = LifePredictor(config=self.config.get('predictor_config'))
        
        logger.info("Simulation runner initialized")
    
    def run_single_user_simulation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a simulation for a single user.
        
        Args:
            user_id: Optional user ID (generated if not provided)
            
        Returns:
            Dictionary containing the simulation results
        """
        logger.info(f"Running simulation for user {user_id or 'new user'}")
        
        # Generate synthetic user data
        user_data = self.data_generator.generate_complete_user_dataset(user_id)
        
        # Save the generated data
        data_file_path = os.path.join(self.output_dir, f"{user_data['user_profile']['user_id']}_data.json")
        with open(data_file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        logger.info(f"Generated user data saved to {data_file_path}")
        
        # Run analysis
        analysis_results = self.predictor.run_complete_analysis(user_data)
        
        # Save the analysis results
        results_file_path = os.path.join(self.output_dir, f"{user_data['user_profile']['user_id']}_analysis.json")
        with open(results_file_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        logger.info(f"Analysis results saved to {results_file_path}")
        
        # Combine data and results
        simulation_results = {
            "user_data": user_data,
            "analysis_results": analysis_results,
            "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "completed_at": datetime.now().isoformat()
        }
        
        return simulation_results
    
    def run_multiple_users_simulation(self, num_users: int = 5) -> List[Dict[str, Any]]:
        """
        Run simulations for multiple users.
        
        Args:
            num_users: Number of user simulations to run
            
        Returns:
            List of simulation results for each user
        """
        logger.info(f"Running simulation for {num_users} users")
        
        all_results = []
        
        for i in range(num_users):
            user_id = f"user_{i+1:04d}"
            logger.info(f"Processing user {i+1}/{num_users}: {user_id}")
            
            # Run simulation for this user
            user_results = self.run_single_user_simulation(user_id)
            all_results.append(user_results)
        
        # Save summary report
        summary = self._generate_summary_report(all_results)
        summary_path = os.path.join(self.output_dir, "simulation_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Simulation complete for {num_users} users, summary saved to {summary_path}")
        
        return all_results
    
    def _generate_summary_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary report from multiple user simulations.
        
        Args:
            all_results: List of simulation results for multiple users
            
        Returns:
            Dictionary containing the summary report
        """
        # Extract key metrics for summary
        life_expectancies = []
        biological_ages = []
        chronological_ages = []
        bio_age_diffs = []
        health_risks = {
            "cardiovascular": [],
            "metabolic": [],
            "neurological": [],
            "cancer": []
        }
        
        for result in all_results:
            analysis = result["analysis_results"]
            user_data = result["user_data"]
            
            if analysis["status"] == "success":
                # Life expectancy
                life_expectancies.append(analysis["life_expectancy"]["predicted_life_expectancy"])
                
                # Biological age
                chronological_ages.append(analysis["biological_age"]["chronological_age"])
                biological_ages.append(analysis["biological_age"]["biological_age"])
                bio_age_diffs.append(analysis["biological_age"]["age_difference"])
                
                # Health risks
                for risk_type in health_risks.keys():
                    risk_level = analysis["health_risks"]["risks"][risk_type]["risk_level"]
                    health_risks[risk_type].append(risk_level)
        
        # Calculate statistics
        avg_life_expectancy = sum(life_expectancies) / len(life_expectancies) if life_expectancies else 0
        avg_chronological_age = sum(chronological_ages) / len(chronological_ages) if chronological_ages else 0
        avg_biological_age = sum(biological_ages) / len(biological_ages) if biological_ages else 0
        avg_bio_age_diff = sum(bio_age_diffs) / len(bio_age_diffs) if bio_age_diffs else 0
        
        risk_averages = {}
        for risk_type, values in health_risks.items():
            risk_averages[risk_type] = sum(values) / len(values) if values else 0
        
        # Create summary report
        summary = {
            "simulation_id": f"multi_sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "num_users": len(all_results),
            "averages": {
                "life_expectancy": round(avg_life_expectancy, 1),
                "chronological_age": round(avg_chronological_age, 1),
                "biological_age": round(avg_biological_age, 1),
                "biological_age_difference": round(avg_bio_age_diff, 1),
                "risk_levels": {k: round(v, 2) for k, v in risk_averages.items()}
            },
            "distributions": {
                "life_expectancy": self._calculate_distribution(life_expectancies, 5),
                "biological_vs_chronological": self._calculate_distribution(bio_age_diffs, 3)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def _calculate_distribution(self, values: List[float], bin_size: float) -> Dict[str, int]:
        """
        Calculate a simple distribution of values for reporting.
        
        Args:
            values: List of values to bin
            bin_size: Size of each bin
            
        Returns:
            Dictionary with bins as keys and counts as values
        """
        if not values:
            return {}
        
        # Create bins
        min_val = min(values)
        max_val = max(values)
        
        # Adjust min_val to be a multiple of bin_size
        min_val = bin_size * (min_val // bin_size)
        
        # Create bins
        bins = {}
        current = min_val
        while current <= max_val:
            bin_key = f"{current:.1f}_{(current + bin_size):.1f}"
            bins[bin_key] = 0
            current += bin_size
        
        # Count values in each bin
        for val in values:
            bin_index = min(int((val - min_val) / bin_size), len(bins) - 1)
            bin_key = list(bins.keys())[bin_index]
            bins[bin_key] += 1
        
        return bins
    
    def run_scenario_simulation(self, user_id: str, scenario: str) -> Dict[str, Any]:
        """
        Run a simulation for a specific scenario to see impact of interventions.
        
        Args:
            user_id: User ID for simulation
            scenario: Scenario type (e.g., 'improved_diet', 'exercise_program')
            
        Returns:
            Dictionary containing scenario simulation results
        """
        # Load existing user data if available, or generate new
        user_data_path = os.path.join(self.output_dir, f"{user_id}_data.json")
        if os.path.exists(user_data_path):
            with open(user_data_path, 'r') as f:
                user_data = json.load(f)
            logger.info(f"Loaded existing user data for {user_id}")
        else:
            user_data = self.data_generator.generate_complete_user_dataset(user_id)
            logger.info(f"Generated new user data for {user_id}")
        
        # Make a copy of the user data
        scenario_data = json.loads(json.dumps(user_data))
        
        # Modify the data according to the scenario
        if scenario == "improved_diet":
            self._apply_improved_diet_scenario(scenario_data)
        elif scenario == "exercise_program":
            self._apply_exercise_program_scenario(scenario_data)
        elif scenario == "stress_reduction":
            self._apply_stress_reduction_scenario(scenario_data)
        elif scenario == "sleep_optimization":
            self._apply_sleep_optimization_scenario(scenario_data)
        elif scenario == "quit_smoking":
            self._apply_quit_smoking_scenario(scenario_data)
        elif scenario == "optimal_lifestyle":
            self._apply_optimal_lifestyle_scenario(scenario_data)
        else:
            logger.warning(f"Unknown scenario: {scenario}, using original data")
        
        # Run analysis with the scenario data
        scenario_results = self.predictor.run_complete_analysis(scenario_data)
        
        # Save the scenario results
        scenario_file_path = os.path.join(
            self.output_dir, 
            f"{user_id}_scenario_{scenario}_analysis.json"
        )
        with open(scenario_file_path, 'w') as f:
            json.dump(scenario_results, f, indent=2)
        
        logger.info(f"Scenario analysis for '{scenario}' saved to {scenario_file_path}")
        
        # Create output with original and scenario results for comparison
        comparison = {
            "user_id": user_id,
            "scenario": scenario,
            "original_data": user_data,
            "scenario_data": scenario_data,
            "original_analysis": None,
            "scenario_analysis": scenario_results,
            "comparison": self._generate_scenario_comparison(user_id, scenario_results),
            "generated_at": datetime.now().isoformat()
        }
        
        # Load original analysis if it exists
        original_analysis_path = os.path.join(self.output_dir, f"{user_id}_analysis.json")
        if os.path.exists(original_analysis_path):
            with open(original_analysis_path, 'r') as f:
                original_analysis = json.load(f)
            comparison["original_analysis"] = original_analysis
        
        return comparison
    
    def _generate_scenario_comparison(self, user_id: str, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare scenario results with original baseline analysis.
        
        Args:
            user_id: User ID for the comparison
            scenario_results: Analysis results from the scenario
            
        Returns:
            Dictionary containing comparison metrics
        """
        # Try to load original analysis for comparison
        original_analysis_path = os.path.join(self.output_dir, f"{user_id}_analysis.json")
        if not os.path.exists(original_analysis_path):
            return {
                "status": "error",
                "message": "Original analysis not found for comparison"
            }
        
        with open(original_analysis_path, 'r') as f:
            original = json.load(f)
        
        if original["status"] != "success" or scenario_results["status"] != "success":
            return {
                "status": "error",
                "message": "One or both analyses had errors"
            }
        
        # Compare key metrics
        comparison = {
            "status": "success",
            "life_expectancy": {
                "original": original["life_expectancy"]["predicted_life_expectancy"],
                "scenario": scenario_results["life_expectancy"]["predicted_life_expectancy"],
                "difference": round(
                    scenario_results["life_expectancy"]["predicted_life_expectancy"] - 
                    original["life_expectancy"]["predicted_life_expectancy"],
                    1
                )
            },
            "biological_age": {
                "original": original["biological_age"]["biological_age"],
                "scenario": scenario_results["biological_age"]["biological_age"],
                "difference": round(
                    original["biological_age"]["biological_age"] - 
                    scenario_results["biological_age"]["biological_age"],
                    1
                )
            },
            "health_risks": {}
        }
        
        # Compare risk levels
        for risk_type in ["cardiovascular", "metabolic", "neurological", "cancer"]:
            original_risk = original["health_risks"]["risks"][risk_type]["risk_level"]
            scenario_risk = scenario_results["health_risks"]["risks"][risk_type]["risk_level"]
            
            comparison["health_risks"][risk_type] = {
                "original": original_risk,
                "scenario": scenario_risk,
                "difference": round(original_risk - scenario_risk, 2),
                "percent_reduction": round((original_risk - scenario_risk) / original_risk * 100 if original_risk > 0 else 0, 1)
            }
        
        return comparison
    
    def _apply_improved_diet_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply improved diet scenario modifications to user data.
        
        Args:
            user_data: User data to modify
        """
        # Modify dietary patterns
        user_data["lifestyle_data"]["diet"]["type"] = "Mediterranean"
        user_data["lifestyle_data"]["diet"]["fruit_veg_servings_daily"] = min(
            user_data["lifestyle_data"]["diet"]["fruit_veg_servings_daily"] + 3, 
            7
        )
        user_data["lifestyle_data"]["diet"]["processed_food_frequency"] = "Rarely"
        
        # Adjust health metrics that would be affected by diet
        # Reduce weight by 5-10% if overweight
        if user_data["user_profile"]["bmi"] > 25:
            weight_reduction_factor = random.uniform(0.05, 0.10)
            new_weight = user_data["user_profile"]["weight_kg"] * (1 - weight_reduction_factor)
            user_data["user_profile"]["weight_kg"] = round(new_weight, 1)
            
            # Recalculate BMI
            height_m = user_data["user_profile"]["height_cm"] / 100
            user_data["user_profile"]["bmi"] = round(new_weight / (height_m ** 2), 1)
        
        # Improve cholesterol values
        chol_improvement = random.uniform(0.10, 0.15)
        user_data["health_metrics"]["cholesterol"]["total"] = round(
            user_data["health_metrics"]["cholesterol"]["total"] * (1 - chol_improvement)
        )
        user_data["health_metrics"]["cholesterol"]["ldl"] = round(
            user_data["health_metrics"]["cholesterol"]["ldl"] * (1 - chol_improvement * 1.2)
        )
        user_data["health_metrics"]["cholesterol"]["hdl"] = round(
            user_data["health_metrics"]["cholesterol"]["hdl"] * (1 + chol_improvement * 0.5)
        )
        
        # Improve glucose values
        glucose_improvement = random.uniform(0.05, 0.10)
        current_glucose = user_data["health_metrics"]["fasting_glucose"]
        target_glucose = 85  # Ideal fasting glucose
        
        if current_glucose > target_glucose:
            user_data["health_metrics"]["fasting_glucose"] = round(
                current_glucose - (current_glucose - target_glucose) * glucose_improvement
            )
        
        # Adjust HbA1c accordingly
        current_hba1c = user_data["health_metrics"]["hba1c"]
        target_hba1c = 5.0  # Ideal HbA1c
        
        if current_hba1c > target_hba1c:
            user_data["health_metrics"]["hba1c"] = round(
                current_hba1c - (current_hba1c - target_hba1c) * glucose_improvement,
                1
            )
    
    def _apply_exercise_program_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply exercise program scenario modifications to user data.
        
        Args:
            user_data: User data to modify
        """
        current_exercise = user_data["lifestyle_data"]["exercise"]
        
        # Increase exercise minutes substantially
        current_minutes = current_exercise["minutes_per_week"]
        if current_minutes < 150:
            # Aim for at least 150 minutes
            new_minutes = max(150, current_minutes * 2)
        else:
            # Increase by at least 50% up to 300 minutes
            new_minutes = min(300, current_minutes * 1.5)
        
        user_data["lifestyle_data"]["exercise"]["minutes_per_week"] = int(new_minutes)
        
        # Add more exercise types if needed
        current_types = current_exercise["types"]
        all_types = ["Walking", "Running", "Cycling", "Swimming", "Weight Training", 
                     "Yoga", "Team Sports", "HIIT", "Pilates", "Dancing"]
        
        # Ensure a balanced mix of cardio, strength, and flexibility exercises
        if len(current_types) < 3:
            # Categories
            cardio = ["Walking", "Running", "Cycling", "Swimming", "HIIT"]
            strength = ["Weight Training", "HIIT"]
            flexibility = ["Yoga", "Pilates"]
            
            # Ensure at least one from each category
            new_types = list(current_types)  # Copy existing types
            
            # Add cardio if needed
            if not any(t in cardio for t in new_types):
                new_types.append(random.choice(cardio))
                
            # Add strength if needed
            if not any(t in strength for t in new_types):
                new_types.append(random.choice(strength))
                
            # Add flexibility if needed
            if not any(t in flexibility for t in new_types):
                new_types.append(random.choice(flexibility))
            
            user_data["lifestyle_data"]["exercise"]["types"] = new_types
        
        # Improve cardiovascular health metrics
        # Reduce resting heart rate
        heart_rate_reduction = random.uniform(5, 15)
        user_data["health_metrics"]["resting_heart_rate"] = max(
            55, user_data["health_metrics"]["resting_heart_rate"] - heart_rate_reduction
        )
        
        # Improve blood pressure
        bp_systolic_reduction = random.uniform(3, 10)
        bp_diastolic_reduction = random.uniform(2, 6)
        
        user_data["health_metrics"]["blood_pressure"]["systolic"] = max(
            110, user_data["health_metrics"]["blood_pressure"]["systolic"] - bp_systolic_reduction
        )
        user_data["health_metrics"]["blood_pressure"]["diastolic"] = max(
            70, user_data["health_metrics"]["blood_pressure"]["diastolic"] - bp_diastolic_reduction
        )
        
        # Increase VO2 max
        vo2_increase = random.uniform(10, 20)
        user_data["health_metrics"]["vo2_max"] += vo2_increase
        
        # Reduce body fat percentage
        fat_reduction = random.uniform(1, 4)
        user_data["health_metrics"]["body_fat_percentage"] = max(
            10 if user_data["user_profile"]["gender"] == "Male" else 15,
            user_data["health_metrics"]["body_fat_percentage"] - fat_reduction
        )
        
        # Adjust weight if overweight
        if user_data["user_profile"]["bmi"] > 25:
            weight_reduction_factor = random.uniform(0.03, 0.08)
            new_weight = user_data["user_profile"]["weight_kg"] * (1 - weight_reduction_factor)
            user_data["user_profile"]["weight_kg"] = round(new_weight, 1)
            
            # Recalculate BMI
            height_m = user_data["user_profile"]["height_cm"] / 100
            user_data["user_profile"]["bmi"] = round(new_weight / (height_m ** 2), 1)
    
    def _apply_stress_reduction_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply stress reduction scenario modifications to user data.
        
        Args:
            user_data: User data to modify
        """
        # Improve stress level
        current_stress = user_data["lifestyle_data"]["stress_level"]
        
        # Map stress levels to numeric values
        stress_map = {"Low": 0, "Moderate": 1, "High": 2, "Very High": 3}
        reverse_map = {0: "Low", 1: "Moderate", 2: "High", 3: "Very High"}
        
        # Reduce stress by at least one level
        if current_stress in stress_map:
            current_level = stress_map[current_stress]
            new_level = max(0, current_level - 1)
            user_data["lifestyle_data"]["stress_level"] = reverse_map[new_level]
        
        # Improve sleep quality as stress reduction often helps sleep
        current_sleep_quality = user_data["lifestyle_data"]["sleep"]["quality"]
        
        # Map sleep quality to numeric values
        sleep_map = {"Poor": 0, "Fair": 1, "Good": 2, "Excellent": 3}
        reverse_sleep_map = {0: "Poor", 1: "Fair", 2: "Good", 3: "Excellent"}
        
        # Improve sleep quality by one level
        if current_sleep_quality in sleep_map:
            current_level = sleep_map[current_sleep_quality]
            new_level = min(3, current_level + 1)
            user_data["lifestyle_data"]["sleep"]["quality"] = reverse_sleep_map[new_level]
        
        # Increase sleep hours slightly if below optimal
        if user_data["lifestyle_data"]["sleep"]["average_hours"] < 7:
            user_data["lifestyle_data"]["sleep"]["average_hours"] = min(
                8.0, user_data["lifestyle_data"]["sleep"]["average_hours"] + 0.5
            )
        
        # Improve blood pressure (stress affects BP)
        bp_systolic_reduction = random.uniform(2, 8)
        bp_diastolic_reduction = random.uniform(1, 5)
        
        user_data["health_metrics"]["blood_pressure"]["systolic"] = max(
            110, user_data["health_metrics"]["blood_pressure"]["systolic"] - bp_systolic_reduction
        )
        user_data["health_metrics"]["blood_pressure"]["diastolic"] = max(
            70, user_data["health_metrics"]["blood_pressure"]["diastolic"] - bp_diastolic_reduction
        )
        
        # Reduce resting heart rate
        heart_rate_reduction = random.uniform(2, 8)
        user_data["health_metrics"]["resting_heart_rate"] = max(
            60, user_data["health_metrics"]["resting_heart_rate"] - heart_rate_reduction
        )
    
    def _apply_sleep_optimization_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply sleep optimization scenario modifications to user data.
        
        Args:
            user_data: User data to modify
        """
        # Optimize sleep hours to 7-8 range
        current_sleep_hours = user_data["lifestyle_data"]["sleep"]["average_hours"]
        
        if current_sleep_hours < 7:
            user_data["lifestyle_data"]["sleep"]["average_hours"] = random.uniform(7.0, 8.0)
        elif current_sleep_hours > 9:
            user_data["lifestyle_data"]["sleep"]["average_hours"] = random.uniform(7.5, 8.5)
        
        # Improve sleep quality to Good or Excellent
        current_sleep_quality = user_data["lifestyle_data"]["sleep"]["quality"]
        
        # Map sleep quality to numeric values
        sleep_map = {"Poor": 0, "Fair": 1, "Good": 2, "Excellent": 3}
        reverse_sleep_map = {0: "Poor", 1: "Fair", 2: "Good", 3: "Excellent"}
        
        # Improve sleep quality to at least "Good"
        if current_sleep_quality in sleep_map:
            current_level = sleep_map[current_sleep_quality]
            new_level = max(2, current_level + 1)  # At least "Good"
            user_data["lifestyle_data"]["sleep"]["quality"] = reverse_sleep_map[min(3, new_level)]
        
        # Improve stress level as better sleep reduces stress
        current_stress = user_data["lifestyle_data"]["stress_level"]
        
        # Map stress levels to numeric values
        stress_map = {"Low": 0, "Moderate": 1, "High": 2, "Very High": 3}
        reverse_map = {0: "Low", 1: "Moderate", 2: "High", 3: "Very High"}
        
        # Reduce stress by one level if possible
        if current_stress in stress_map:
            current_level = stress_map[current_stress]
            new_level = max(0, current_level - 1)
            user_data["lifestyle_data"]["stress_level"] = reverse_map[new_level]
        
        # Improve some health metrics related to sleep
        
        # Reduce resting heart rate
        heart_rate_reduction = random.uniform(2, 5)
        user_data["health_metrics"]["resting_heart_rate"] = max(
            60, user_data["health_metrics"]["resting_heart_rate"] - heart_rate_reduction
        )
        
        # Slightly improve blood pressure
        bp_systolic_reduction = random.uniform(1, 5)
        bp_diastolic_reduction = random.uniform(1, 3)
        
        user_data["health_metrics"]["blood_pressure"]["systolic"] = max(
            110, user_data["health_metrics"]["blood_pressure"]["systolic"] - bp_systolic_reduction
        )
        user_data["health_metrics"]["blood_pressure"]["diastolic"] = max(
            70, user_data["health_metrics"]["blood_pressure"]["diastolic"] - bp_diastolic_reduction
        )
        
        # Improve glucose metabolism (sleep affects insulin sensitivity)
        glucose_improvement = random.uniform(1, 3)
        current_glucose = user_data["health_metrics"]["fasting_glucose"]
        target_glucose = 85  # Ideal fasting glucose
        
        if current_glucose > target_glucose:
            user_data["health_metrics"]["fasting_glucose"] = max(
                target_glucose, current_glucose - glucose_improvement
            )
    
    def _apply_quit_smoking_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply quit smoking scenario modifications to user data.
        
        Args:
            user_data: User data to modify
        """
        # Only apply if user is a current smoker
        if user_data["user_profile"]["smoking_status"].lower() != "current":
            return
        
        # Change smoking status to former
        user_data["user_profile"]["smoking_status"] = "Former"
        
        # Improve cardiovascular health
        # Reduce heart rate
        heart_rate_reduction = random.uniform(5, 12)
        user_data["health_metrics"]["resting_heart_rate"] = max(
            60, user_data["health_metrics"]["resting_heart_rate"] - heart_rate_reduction
        )
        
        # Improve blood pressure
        bp_systolic_reduction = random.uniform(5, 12)
        bp_diastolic_reduction = random.uniform(3, 8)
        
        user_data["health_metrics"]["blood_pressure"]["systolic"] = max(
            110, user_data["health_metrics"]["blood_pressure"]["systolic"] - bp_systolic_reduction
        )
        user_data["health_metrics"]["blood_pressure"]["diastolic"] = max(
            70, user_data["health_metrics"]["blood_pressure"]["diastolic"] - bp_diastolic_reduction
        )
        
        # Improve lung capacity (VO2 max)
        vo2_increase = random.uniform(5, 15)
        user_data["health_metrics"]["vo2_max"] += vo2_increase
        
        # Improve cholesterol profile slightly
        chol_improvement = random.uniform(0.05, 0.10)
        user_data["health_metrics"]["cholesterol"]["total"] = max(
            150, user_data["health_metrics"]["cholesterol"]["total"] * (1 - chol_improvement)
        )
        user_data["health_metrics"]["cholesterol"]["ldl"] = max(
            70, user_data["health_metrics"]["cholesterol"]["ldl"] * (1 - chol_improvement)
        )
    
    def _apply_optimal_lifestyle_scenario(self, user_data: Dict[str, Any]) -> None:
        """
        Apply optimal lifestyle scenario with all positive interventions.
        
        Args:
            user_data: User data to modify
        """
        # Apply all individual scenarios
        self._apply_improved_diet_scenario(user_data)
        self._apply_exercise_program_scenario(user_data)
        self._apply_stress_reduction_scenario(user_data)
        self._apply_sleep_optimization_scenario(user_data)
        
        # Apply quit smoking if applicable
        if user_data["user_profile"]["smoking_status"].lower() == "current":
            self._apply_quit_smoking_scenario(user_data)
        
        # Optimize alcohol consumption
        if user_data["user_profile"]["alcohol_frequency"].lower() == "frequent":
            user_data["user_profile"]["alcohol_frequency"] = "Moderate"
        
        # Further boost some metrics for synergistic effects
        
        # Improve body composition
        if user_data["user_profile"]["bmi"] > 25:
            # Additional weight loss from combined interventions
            weight_reduction_factor = random.uniform(0.05, 0.12)
            new_weight = user_data["user_profile"]["weight_kg"] * (1 - weight_reduction_factor)
            user_data["user_profile"]["weight_kg"] = round(new_weight, 1)
            
            # Recalculate BMI
            height_m = user_data["user_profile"]["height_cm"] / 100
            user_data["user_profile"]["bmi"] = round(new_weight / (height_m ** 2), 1)
        
        # Reduce body fat percentage further
        fat_reduction = random.uniform(2, 5)
        user_data["health_metrics"]["body_fat_percentage"] = max(
            10 if user_data["user_profile"]["gender"] == "Male" else 15,
            user_data["health_metrics"]["body_fat_percentage"] - fat_reduction
        )
        
        # Additional boost to VO2 max from combined interventions
        vo2_increase = random.uniform(5, 10)
        user_data["health_metrics"]["vo2_max"] += vo2_increase
        
        # Further improvements to cholesterol
        chol_improvement = random.uniform(0.05, 0.10)
        user_data["health_metrics"]["cholesterol"]["total"] = max(
            150, user_data["health_metrics"]["cholesterol"]["total"] * (1 - chol_improvement)
        )
        user_data["health_metrics"]["cholesterol"]["ldl"] = max(
            70, user_data["health_metrics"]["cholesterol"]["ldl"] * (1 - chol_improvement)
        )
        user_data["health_metrics"]["cholesterol"]["hdl"] = min(
            90, user_data["health_metrics"]["cholesterol"]["hdl"] * (1 + chol_improvement)
        )
        
        # Update impedance data to reflect biological age improvements
        bio_age_reduction = random.uniform(3, 8)
        bio_age = user_data["impedance_data"]["estimated_biological_age"]
        chrono_age = user_data["impedance_data"]["chronological_age"]
        
        if bio_age > chrono_age:
            # Reduce biological age but not below chronological age
            user_data["impedance_data"]["estimated_biological_age"] = max(
                chrono_age - 5, bio_age - bio_age_reduction
            )
        else:
            # Further reduce biological age
            user_data["impedance_data"]["estimated_biological_age"] = bio_age - bio_age_reduction / 2


def main():
    """Main function for the simulation runner."""
    parser = argparse.ArgumentParser(description="Run AI Life Management System simulation")
    
    parser.add_argument("--users", type=int, default=1, help="Number of users to simulate")
    parser.add_argument("--scenario", type=str, help="Scenario to simulate")
    parser.add_argument("--user-id", type=str, help="Specific user ID to use")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--output-dir", type=str, help="Directory to save results")
    
    args = parser.parse_args()
    
    # Configure the simulation
    config = {}
    if args.seed is not None:
        config["random_seed"] = args.seed
    
    if args.output_dir:
        config["output_dir"] = args.output_dir
    
    # Initialize the simulation runner
    runner = SimulationRunner(config)
    
    # Run the appropriate simulation
    if args.scenario:
        if not args.user_id:
            parser.error("--user-id is required when running a scenario simulation")
        
        logger.info(f"Running scenario simulation: {args.scenario} for user {args.user_id}")
        results = runner.run_scenario_simulation(args.user_id, args.scenario)
        
        # Print key results
        logger.info("Scenario simulation complete")
        if results.get("comparison", {}).get("status") == "success":
            comp = results["comparison"]
            logger.info(f"Life expectancy change: {comp['life_expectancy']['difference']:+.1f} years")
            logger.info(f"Biological age change: {comp['biological_age']['difference']:+.1f} years")
    
    elif args.user_id:
        # Single user simulation with specified ID
        logger.info(f"Running single user simulation for user {args.user_id}")
        runner.run_single_user_simulation(args.user_id)
    
    elif args.users > 1:
        # Multiple users simulation
        logger.info(f"Running simulation for {args.users} users")
        runner.run_multiple_users_simulation(args.users)
    
    else:
        # Default: single anonymous user
        logger.info("Running single user simulation")
        runner.run_single_user_simulation()
    
    logger.info("Simulation completed successfully")


if __name__ == "__main__":
    main()
