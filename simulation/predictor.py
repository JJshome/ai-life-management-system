"""
Predictor Module for AI Life Management System Simulation

This module implements the predictive analytics and recommendation generation
capabilities that form the core of the AI-based Life Management and
Aging Preparation Decision System.

Based on patented technology by Ucaretron Inc.
"""

import numpy as np
import pandas as pd
import json
import os
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union


class LifePredictor:
    """
    Implements the AI-based prediction and recommendation algorithms of the system.
    
    This class analyzes health metrics, lifestyle data, genetic information,
    and biosensor readings to predict life expectancy, biological age, 
    and generate personalized recommendations for health and lifestyle optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the predictor with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Risk factor weights derived from simulated longitudinal studies
        self.risk_factor_weights = {
            "base_life_expectancy": {
                "male": 76.1,
                "female": 81.1
            },
            "smoking": {
                "never": 0,
                "former": -2.0,
                "current": -10.0
            },
            "bmi": {
                "optimal_range": (18.5, 25.0),
                "per_unit_above": -0.4,
                "per_unit_below": -0.3
            },
            "blood_pressure": {
                "optimal_systolic": 115,
                "per_10mmHg_above": -1.2
            },
            "cholesterol": {
                "optimal_ratio": 3.5,  # Total/HDL ratio
                "per_unit_above": -1.0
            },
            "exercise": {
                "minutes_per_week": {
                    "0": 0,
                    "1-60": 1.0,
                    "61-150": 2.5,
                    "151-300": 3.5,
                    "300+": 4.2
                }
            },
            "diet": {
                "fruit_veg_servings": 0.4,  # Per serving per day
                "mediterranean": 2.5,
                "processed_food": {
                    "rarely": 0,
                    "sometimes": -0.8,
                    "often": -1.8,
                    "very_frequently": -3.0
                }
            },
            "sleep": {
                "optimal_hours": 7.5,
                "per_hour_deficit": -0.5,
                "quality": {
                    "poor": -1.5,
                    "fair": -0.7,
                    "good": 0,
                    "excellent": 0.8
                }
            },
            "alcohol": {
                "none": 0,
                "rare": 0.5,
                "moderate": 0,
                "frequent": -3.0
            },
            "stress": {
                "low": 1.0,
                "moderate": 0,
                "high": -2.0,
                "very_high": -4.0
            },
            "social_connection": {
                "factor": 1.8  # Added in based on activity types
            },
            "genetic_risk": {
                "cardiovascular_factor": -5.0,  # Multiplied by risk probability
                "diabetes_factor": -3.5,
                "cancer_factor": -4.0,
                "neurodegenerative_factor": -3.0
            },
            "biomarker_aging": {
                "biological_vs_chronological": 1.5  # Per year of difference
            }
        }
    
    def predict_life_expectancy(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict life expectancy based on all available user data.
        
        Args:
            user_data: Complete user dataset
            
        Returns:
            Dictionary containing life expectancy prediction and related metrics
        """
        user_profile = user_data["user_profile"]
        health_metrics = user_data["health_metrics"]
        impedance_data = user_data["impedance_data"]
        lifestyle_data = user_data["lifestyle_data"]
        genetic_data = user_data["genetic_data"]
        
        # Base life expectancy by gender
        gender = user_profile["gender"]
        age = user_profile["age"]
        weights = self.risk_factor_weights
        
        base_expectancy = weights["base_life_expectancy"]["male" if gender.lower() == "male" else "female"]
        
        # Calculate adjustments based on various factors
        adjustments = []
        
        # 1. Smoking adjustment
        smoking_status = user_profile["smoking_status"].lower()
        smoking_adj = weights["smoking"].get(smoking_status, 0)
        adjustments.append(("Smoking", smoking_adj))
        
        # 2. BMI adjustment
        bmi = user_profile["bmi"]
        bmi_adj = 0
        if bmi > weights["bmi"]["optimal_range"][1]:
            bmi_adj = (bmi - weights["bmi"]["optimal_range"][1]) * weights["bmi"]["per_unit_above"]
        elif bmi < weights["bmi"]["optimal_range"][0]:
            bmi_adj = (weights["bmi"]["optimal_range"][0] - bmi) * weights["bmi"]["per_unit_below"]
        adjustments.append(("BMI", bmi_adj))
        
        # 3. Blood pressure adjustment
        systolic = health_metrics["blood_pressure"]["systolic"]
        if systolic > weights["blood_pressure"]["optimal_systolic"]:
            bp_adj = ((systolic - weights["blood_pressure"]["optimal_systolic"]) / 10) * weights["blood_pressure"]["per_10mmHg_above"]
        else:
            bp_adj = 0
        adjustments.append(("Blood Pressure", bp_adj))
        
        # 4. Cholesterol adjustment
        chol_ratio = health_metrics["cholesterol"]["total"] / health_metrics["cholesterol"]["hdl"]
        if chol_ratio > weights["cholesterol"]["optimal_ratio"]:
            chol_adj = (chol_ratio - weights["cholesterol"]["optimal_ratio"]) * weights["cholesterol"]["per_unit_above"]
        else:
            chol_adj = 0
        adjustments.append(("Cholesterol", chol_adj))
        
        # 5. Exercise adjustment
        exercise_minutes = lifestyle_data["exercise"]["minutes_per_week"]
        if exercise_minutes == 0:
            exercise_adj = weights["exercise"]["minutes_per_week"]["0"]
        elif exercise_minutes <= 60:
            exercise_adj = weights["exercise"]["minutes_per_week"]["1-60"]
        elif exercise_minutes <= 150:
            exercise_adj = weights["exercise"]["minutes_per_week"]["61-150"]
        elif exercise_minutes <= 300:
            exercise_adj = weights["exercise"]["minutes_per_week"]["151-300"]
        else:
            exercise_adj = weights["exercise"]["minutes_per_week"]["300+"]
        adjustments.append(("Exercise", exercise_adj))
        
        # 6. Diet adjustment
        diet_adj = 0
        # Fruit and vegetable servings
        fruit_veg = lifestyle_data["diet"]["fruit_veg_servings_daily"]
        diet_adj += fruit_veg * weights["diet"]["fruit_veg_servings"]
        
        # Mediterranean diet bonus
        if lifestyle_data["diet"]["type"].lower() == "mediterranean":
            diet_adj += weights["diet"]["mediterranean"]
        
        # Processed food penalty
        processed_food = lifestyle_data["diet"]["processed_food_frequency"].lower()
        diet_adj += weights["diet"]["processed_food"].get(processed_food, 0)
        
        adjustments.append(("Diet", diet_adj))
        
        # 7. Sleep adjustment
        sleep_adj = 0
        sleep_hours = lifestyle_data["sleep"]["average_hours"]
        if sleep_hours < weights["sleep"]["optimal_hours"]:
            sleep_adj += (sleep_hours - weights["sleep"]["optimal_hours"]) * weights["sleep"]["per_hour_deficit"]
        
        sleep_quality = lifestyle_data["sleep"]["quality"].lower()
        sleep_adj += weights["sleep"]["quality"].get(sleep_quality, 0)
        
        adjustments.append(("Sleep", sleep_adj))
        
        # 8. Alcohol adjustment
        alcohol_freq = user_profile["alcohol_frequency"].lower()
        alcohol_adj = weights["alcohol"].get(alcohol_freq, 0)
        adjustments.append(("Alcohol", alcohol_adj))
        
        # 9. Stress adjustment
        stress_level = lifestyle_data["stress_level"].lower()
        stress_adj = weights["stress"].get(stress_level, 0)
        adjustments.append(("Stress", stress_adj))
        
        # 10. Social connection adjustment (estimated from exercise types)
        social_adj = 0
        team_activities = [act for act in lifestyle_data["exercise"]["types"] 
                           if act.lower() in ["team sports", "dancing", "yoga", "pilates"]]
        if team_activities:
            social_adj = weights["social_connection"]["factor"] * (len(team_activities) / 4)
            social_adj = min(social_adj, weights["social_connection"]["factor"])
        adjustments.append(("Social Connection", social_adj))
        
        # 11. Genetic risk adjustment
        genetic_adj = 0
        
        # Cardiovascular disease risk
        genetic_adj += genetic_data["risk_factors"]["cardiovascular_disease"] * weights["genetic_risk"]["cardiovascular_factor"]
        
        # Diabetes risk
        genetic_adj += genetic_data["risk_factors"]["type_2_diabetes"] * weights["genetic_risk"]["diabetes_factor"]
        
        # Cancer risk (average of all cancer types)
        cancer_risks = genetic_data["risk_factors"]["cancer"].values()
        avg_cancer_risk = sum(cancer_risks) / len(cancer_risks)
        genetic_adj += avg_cancer_risk * weights["genetic_risk"]["cancer_factor"]
        
        # Neurodegenerative disease risk (average of all types)
        neuro_risks = genetic_data["risk_factors"]["neurodegenerative"].values()
        avg_neuro_risk = sum(neuro_risks) / len(neuro_risks)
        genetic_adj += avg_neuro_risk * weights["genetic_risk"]["neurodegenerative_factor"]
        
        adjustments.append(("Genetic Factors", genetic_adj))
        
        # 12. Biomarker aging adjustment
        bio_age = impedance_data["estimated_biological_age"]
        bio_age_diff = age - bio_age  # Positive if biologically younger
        bio_age_adj = bio_age_diff * weights["biomarker_aging"]["biological_vs_chronological"]
        adjustments.append(("Biological Age", bio_age_adj))
        
        # Calculate total adjustment
        total_adjustment = sum(adj for _, adj in adjustments)
        
        # Calculate final life expectancy
        life_expectancy = base_expectancy + total_adjustment
        
        # Calculate remaining years (life expectancy minus current age)
        remaining_years = life_expectancy - age
        
        # Add uncertainty range (95% confidence interval)
        uncertainty = 4.2  # Based on simulated statistical models
        
        # Format the results
        prediction = {
            "user_id": user_profile["user_id"],
            "current_age": age,
            "gender": gender,
            "base_life_expectancy": base_expectancy,
            "predicted_life_expectancy": round(life_expectancy, 1),
            "confidence_interval": [
                round(life_expectancy - uncertainty, 1),
                round(life_expectancy + uncertainty, 1)
            ],
            "expected_remaining_years": round(remaining_years, 1),
            "factors": adjustments,
            "predicted_at": datetime.now().isoformat()
        }
        
        return prediction
    
    def calculate_biological_age(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate biological age based on health metrics and impedance data.
        
        Args:
            user_data: Complete user dataset
            
        Returns:
            Dictionary containing biological age assessment
        """
        user_profile = user_data["user_profile"]
        health_metrics = user_data["health_metrics"]
        impedance_data = user_data["impedance_data"]
        lifestyle_data = user_data["lifestyle_data"]
        
        chronological_age = user_profile["age"]
        gender = user_profile["gender"]
        
        # Factors that influence biological age
        
        # 1. Impedance-based age (from simulated ear sensor data)
        impedance_age = impedance_data["estimated_biological_age"]
        
        # 2. Cardiovascular age
        cv_factors = []
        
        # Blood pressure
        systolic = health_metrics["blood_pressure"]["systolic"]
        diastolic = health_metrics["blood_pressure"]["diastolic"]
        
        if systolic <= 120 and diastolic <= 80:
            bp_age_factor = -5  # Younger than chronological age
        elif systolic <= 130 and diastolic <= 85:
            bp_age_factor = 0   # Same as chronological age
        elif systolic <= 140 and diastolic <= 90:
            bp_age_factor = 5   # Older than chronological age
        else:
            bp_age_factor = 10  # Much older than chronological age
        
        cv_factors.append(bp_age_factor)
        
        # Resting heart rate
        heart_rate = health_metrics["resting_heart_rate"]
        
        if heart_rate < 60:
            hr_age_factor = -5  # Athletic heart, younger
        elif heart_rate <= 70:
            hr_age_factor = -2  # Good heart rate, slightly younger
        elif heart_rate <= 80:
            hr_age_factor = 0   # Average, same as chronological
        elif heart_rate <= 90:
            hr_age_factor = 3   # Slightly higher, slightly older
        else:
            hr_age_factor = 7   # High heart rate, older
        
        cv_factors.append(hr_age_factor)
        
        # Cholesterol
        total_chol = health_metrics["cholesterol"]["total"]
        hdl = health_metrics["cholesterol"]["hdl"]
        ldl = health_metrics["cholesterol"]["ldl"]
        chol_ratio = total_chol / hdl
        
        if chol_ratio < 3.5:
            chol_age_factor = -3  # Excellent ratio, younger
        elif chol_ratio < 4.5:
            chol_age_factor = 0   # Good ratio, neutral
        elif chol_ratio < 5.5:
            chol_age_factor = 3   # Moderate risk, slightly older
        else:
            chol_age_factor = 7   # High risk, older
        
        cv_factors.append(chol_age_factor)
        
        # Calculate cardiovascular age adjustment
        cv_age_adjustment = sum(cv_factors) / len(cv_factors)
        
        # 3. Metabolic age
        metabolic_factors = []
        
        # Glucose levels
        glucose = health_metrics["fasting_glucose"]
        
        if glucose < 90:
            glucose_age_factor = -3  # Excellent glucose, younger
        elif glucose <= 100:
            glucose_age_factor = 0   # Normal glucose, neutral
        elif glucose <= 110:
            glucose_age_factor = 2   # Prediabetic range, slightly older
        elif glucose <= 125:
            glucose_age_factor = 5   # Higher prediabetic range, older
        else:
            glucose_age_factor = 10  # Diabetic range, much older
        
        metabolic_factors.append(glucose_age_factor)
        
        # HbA1c
        hba1c = health_metrics["hba1c"]
        
        if hba1c < 5.0:
            hba1c_age_factor = -3  # Excellent, younger
        elif hba1c <= 5.6:
            hba1c_age_factor = 0   # Normal, neutral
        elif hba1c <= 6.0:
            hba1c_age_factor = 2   # Borderline, slightly older
        elif hba1c <= 6.4:
            hba1c_age_factor = 5   # Prediabetic, older
        else:
            hba1c_age_factor = 10  # Diabetic, much older
        
        metabolic_factors.append(hba1c_age_factor)
        
        # BMI
        bmi = user_profile["bmi"]
        
        if 18.5 <= bmi <= 24.9:
            bmi_age_factor = -2  # Healthy BMI, younger
        elif 25.0 <= bmi <= 29.9:
            bmi_age_factor = 1   # Overweight, slightly older
        elif bmi >= 30:
            bmi_age_factor = 5   # Obese, older
        else:
            bmi_age_factor = 0   # Underweight, neutral (can be unhealthy but varies)
        
        metabolic_factors.append(bmi_age_factor)
        
        # Calculate metabolic age adjustment
        metabolic_age_adjustment = sum(metabolic_factors) / len(metabolic_factors)
        
        # 4. Fitness age
        fitness_factors = []
        
        # VO2 max
        vo2_max = health_metrics["vo2_max"]
        
        # VO2 max reference values vary by gender and age
        if gender.lower() == "male":
            if chronological_age < 30:
                vo2_ref = 45
            elif chronological_age < 40:
                vo2_ref = 42
            elif chronological_age < 50:
                vo2_ref = 38
            elif chronological_age < 60:
                vo2_ref = 35
            else:
                vo2_ref = 32
        else:  # Female
            if chronological_age < 30:
                vo2_ref = 38
            elif chronological_age < 40:
                vo2_ref = 35
            elif chronological_age < 50:
                vo2_ref = 32
            elif chronological_age < 60:
                vo2_ref = 29
            else:
                vo2_ref = 26
        
        # Calculate fitness age factor
        vo2_diff = vo2_max - vo2_ref
        fitness_age_factor = -vo2_diff / 2  # Each 2 points of VO2 max above reference is -1 year
        
        fitness_factors.append(fitness_age_factor)
        
        # Exercise habits
        exercise_minutes = lifestyle_data["exercise"]["minutes_per_week"]
        
        if exercise_minutes >= 300:
            exercise_age_factor = -4  # Very active, much younger
        elif exercise_minutes >= 150:
            exercise_age_factor = -2  # Meeting guidelines, younger
        elif exercise_minutes >= 60:
            exercise_age_factor = 0   # Some activity, neutral
        else:
            exercise_age_factor = 3   # Sedentary, older
        
        fitness_factors.append(exercise_age_factor)
        
        # Calculate fitness age adjustment
        fitness_age_adjustment = sum(fitness_factors) / len(fitness_factors)
        
        # 5. Lifestyle age
        lifestyle_factors = []
        
        # Sleep
        sleep_hours = lifestyle_data["sleep"]["average_hours"]
        sleep_quality = lifestyle_data["sleep"]["quality"].lower()
        
        if sleep_hours >= 7 and sleep_quality in ["good", "excellent"]:
            sleep_age_factor = -3  # Optimal sleep, younger
        elif sleep_hours >= 6.5 and sleep_quality in ["fair", "good", "excellent"]:
            sleep_age_factor = -1  # Decent sleep, slightly younger
        elif sleep_hours < 6 or sleep_quality == "poor":
            sleep_age_factor = 3   # Poor sleep, older
        else:
            sleep_age_factor = 0   # Average sleep, neutral
        
        lifestyle_factors.append(sleep_age_factor)
        
        # Diet
        diet_type = lifestyle_data["diet"]["type"].lower()
        fruit_veg = lifestyle_data["diet"]["fruit_veg_servings_daily"]
        processed_food = lifestyle_data["diet"]["processed_food_frequency"].lower()
        
        diet_age_factor = 0
        
        # Diet type factor
        if diet_type in ["mediterranean", "vegetarian", "vegan"]:
            diet_age_factor -= 2  # Healthier diets, younger
        
        # Fruit and vegetable factor
        if fruit_veg >= 5:
            diet_age_factor -= 2  # Optimal intake, younger
        elif fruit_veg >= 3:
            diet_age_factor -= 1  # Good intake, slightly younger
        elif fruit_veg < 1:
            diet_age_factor += 2  # Poor intake, older
        
        # Processed food factor
        if processed_food == "rarely":
            diet_age_factor -= 1  # Minimal processed food, younger
        elif processed_food == "very frequently":
            diet_age_factor += 2  # High processed food, older
        
        lifestyle_factors.append(diet_age_factor)
        
        # Stress
        stress_level = lifestyle_data["stress_level"].lower()
        
        if stress_level == "low":
            stress_age_factor = -2  # Low stress, younger
        elif stress_level == "moderate":
            stress_age_factor = 0   # Moderate stress, neutral
        elif stress_level == "high":
            stress_age_factor = 2   # High stress, older
        else:  # very high
            stress_age_factor = 4   # Very high stress, much older
        
        lifestyle_factors.append(stress_age_factor)
        
        # Calculate lifestyle age adjustment
        lifestyle_age_adjustment = sum(lifestyle_factors) / len(lifestyle_factors)
        
        # Calculate weighted average of all factors
        # Impedance data gets the highest weight as it's based on direct biological measurements
        factor_weights = {
            "impedance": 0.4,
            "cardiovascular": 0.2,
            "metabolic": 0.2,
            "fitness": 0.1,
            "lifestyle": 0.1
        }
        
        # Calculate biological age
        biological_age = chronological_age
        biological_age += impedance_age - chronological_age
        biological_age += cv_age_adjustment
        biological_age += metabolic_age_adjustment
        biological_age += fitness_age_adjustment
        biological_age += lifestyle_age_adjustment
        
        # Ensure biological age is not unrealistically low
        biological_age = max(20, biological_age)
        
        # Format the results
        bio_age_result = {
            "user_id": user_profile["user_id"],
            "chronological_age": chronological_age,
            "biological_age": round(biological_age, 1),
            "age_difference": round(biological_age - chronological_age, 1),
            "factors": {
                "impedance_based": {
                    "age": round(impedance_age, 1),
                    "weight": factor_weights["impedance"]
                },
                "cardiovascular": {
                    "adjustment": round(cv_age_adjustment, 1),
                    "weight": factor_weights["cardiovascular"]
                },
                "metabolic": {
                    "adjustment": round(metabolic_age_adjustment, 1),
                    "weight": factor_weights["metabolic"]
                },
                "fitness": {
                    "adjustment": round(fitness_age_adjustment, 1),
                    "weight": factor_weights["fitness"]
                },
                "lifestyle": {
                    "adjustment": round(lifestyle_age_adjustment, 1),
                    "weight": factor_weights["lifestyle"]
                }
            },
            "calculated_at": datetime.now().isoformat()
        }
        
        return bio_age_result
    
    def calculate_health_risks(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate health risk assessments for various disease categories.
        
        Args:
            user_data: Complete user dataset
            
        Returns:
            Dictionary containing health risk assessments
        """
        user_profile = user_data["user_profile"]
        health_metrics = user_data["health_metrics"]
        genetic_data = user_data["genetic_data"]
        lifestyle_data = user_data["lifestyle_data"]
        
        # Get base genetic risks
        cardiovascular_genetic_risk = genetic_data["risk_factors"]["cardiovascular_disease"]
        diabetes_genetic_risk = genetic_data["risk_factors"]["type_2_diabetes"]
        cancer_genetic_risks = genetic_data["risk_factors"]["cancer"]
        neurodegenerative_risks = genetic_data["risk_factors"]["neurodegenerative"]
        
        # Calculate cardiovascular risk
        # Factors: genetic risk, BP, cholesterol, smoking, exercise, BMI
        cv_risk_factors = []
        
        # Genetic factor (base risk)
        cv_risk_factors.append(cardiovascular_genetic_risk)
        
        # Blood pressure factor
        systolic = health_metrics["blood_pressure"]["systolic"]
        diastolic = health_metrics["blood_pressure"]["diastolic"]
        
        if systolic > 140 or diastolic > 90:
            bp_risk_factor = 0.3  # High
        elif systolic > 130 or diastolic > 85:
            bp_risk_factor = 0.2  # Elevated
        elif systolic > 120 or diastolic > 80:
            bp_risk_factor = 0.1  # Pre-hypertension
        else:
            bp_risk_factor = 0.0  # Normal
        
        cv_risk_factors.append(bp_risk_factor)
        
        # Cholesterol factor
        total_chol = health_metrics["cholesterol"]["total"]
        hdl = health_metrics["cholesterol"]["hdl"]
        ldl = health_metrics["cholesterol"]["ldl"]
        chol_ratio = total_chol / hdl
        
        if chol_ratio > 5.0:
            chol_risk_factor = 0.3  # High risk
        elif chol_ratio > 4.0:
            chol_risk_factor = 0.2  # Moderate risk
        elif chol_ratio > 3.5:
            chol_risk_factor = 0.1  # Slight risk
        else:
            chol_risk_factor = 0.0  # Low risk
        
        cv_risk_factors.append(chol_risk_factor)
        
        # Smoking factor
        smoking_status = user_profile["smoking_status"].lower()
        
        if smoking_status == "current":
            smoking_risk_factor = 0.4  # High risk
        elif smoking_status == "former":
            smoking_risk_factor = 0.1  # Slight risk
        else:
            smoking_risk_factor = 0.0  # No added risk
        
        cv_risk_factors.append(smoking_risk_factor)
        
        # Exercise factor (inverse relationship)
        exercise_minutes = lifestyle_data["exercise"]["minutes_per_week"]
        
        if exercise_minutes < 30:
            exercise_risk_factor = 0.2  # High risk due to sedentary lifestyle
        elif exercise_minutes < 90:
            exercise_risk_factor = 0.1  # Moderate risk
        else:
            exercise_risk_factor = 0.0  # No added risk
        
        cv_risk_factors.append(exercise_risk_factor)
        
        # BMI factor
        bmi = user_profile["bmi"]
        
        if bmi > 30:
            bmi_risk_factor = 0.2  # Obese - high risk
        elif bmi > 25:
            bmi_risk_factor = 0.1  # Overweight - moderate risk
        else:
            bmi_risk_factor = 0.0  # Normal weight - no added risk
        
        cv_risk_factors.append(bmi_risk_factor)
        
        # Calculate overall cardiovascular risk
        # Using a weighted average of factors
        cardiovascular_risk = sum(cv_risk_factors) / len(cv_risk_factors)
        cardiovascular_risk = min(1.0, cardiovascular_risk)  # Cap at 1.0
        
        # Calculate metabolic risk (diabetes)
        # Factors: genetic risk, glucose levels, BMI, exercise, diet
        metabolic_risk_factors = []
        
        # Genetic factor (base risk)
        metabolic_risk_factors.append(diabetes_genetic_risk)
        
        # Glucose factor
        glucose = health_metrics["fasting_glucose"]
        hba1c = health_metrics["hba1c"]
        
        if glucose > 125 or hba1c > 6.4:
            glucose_risk_factor = 0.5  # Diabetic range - very high risk
        elif glucose > 100 or hba1c > 5.7:
            glucose_risk_factor = 0.3  # Prediabetic range - high risk
        else:
            glucose_risk_factor = 0.0  # Normal range - no added risk
        
        metabolic_risk_factors.append(glucose_risk_factor)
        
        # BMI factor
        if bmi > 30:
            bmi_risk_factor = 0.3  # Obese - high risk
        elif bmi > 25:
            bmi_risk_factor = 0.2  # Overweight - moderate risk
        else:
            bmi_risk_factor = 0.0  # Normal weight - no added risk
        
        metabolic_risk_factors.append(bmi_risk_factor)
        
        # Exercise factor (inverse relationship)
        if exercise_minutes < 30:
            exercise_risk_factor = 0.2  # High risk due to sedentary lifestyle
        elif exercise_minutes < 90:
            exercise_risk_factor = 0.1  # Moderate risk
        else:
            exercise_risk_factor = 0.0  # No added risk
        
        metabolic_risk_factors.append(exercise_risk_factor)
        
        # Diet factor
        processed_food = lifestyle_data["diet"]["processed_food_frequency"].lower()
        fruit_veg = lifestyle_data["diet"]["fruit_veg_servings_daily"]
        
        diet_risk_factor = 0.0
        
        if processed_food == "very frequently":
            diet_risk_factor += 0.2
        elif processed_food == "often":
            diet_risk_factor += 0.1
        
        if fruit_veg < 2:
            diet_risk_factor += 0.1
        
        metabolic_risk_factors.append(diet_risk_factor)
        
        # Calculate overall metabolic risk
        metabolic_risk = sum(metabolic_risk_factors) / len(metabolic_risk_factors)
        metabolic_risk = min(1.0, metabolic_risk)  # Cap at 1.0
        
        # Calculate neurological risk
        # Factors: genetic risk, sleep, stress, exercise, diet
        neuro_risk_factors = []
        
        # Genetic factor (average of Alzheimer's and Parkinson's risk)
        neuro_genetic_risk = (
            neurodegenerative_risks["alzheimers"] + 
            neurodegenerative_risks["parkinsons"]
        ) / 2
        neuro_risk_factors.append(neuro_genetic_risk)
        
        # Sleep factor
        sleep_hours = lifestyle_data["sleep"]["average_hours"]
        sleep_quality = lifestyle_data["sleep"]["quality"].lower()
        
        sleep_risk_factor = 0.0
        
        if sleep_hours < 6:
            sleep_risk_factor += 0.2
        elif sleep_hours < 7:
            sleep_risk_factor += 0.1
        
        if sleep_quality == "poor":
            sleep_risk_factor += 0.1
        
        neuro_risk_factors.append(sleep_risk_factor)
        
        # Stress factor
        stress_level = lifestyle_data["stress_level"].lower()
        
        if stress_level == "very high":
            stress_risk_factor = 0.3
        elif stress_level == "high":
            stress_risk_factor = 0.2
        elif stress_level == "moderate":
            stress_risk_factor = 0.1
        else:
            stress_risk_factor = 0.0
        
        neuro_risk_factors.append(stress_risk_factor)
        
        # Exercise factor (inverse relationship - exercise is protective)
        if exercise_minutes < 30:
            exercise_risk_factor = 0.2
        elif exercise_minutes < 90:
            exercise_risk_factor = 0.1
        else:
            exercise_risk_factor = 0.0
        
        neuro_risk_factors.append(exercise_risk_factor)
        
        # Diet factor (Mediterranean diet is protective)
        diet_type = lifestyle_data["diet"]["type"].lower()
        
        if diet_type == "mediterranean":
            diet_risk_factor = -0.1  # Protective effect
        else:
            diet_risk_factor = 0.0
        
        if fruit_veg < 3:
            diet_risk_factor += 0.1
        
        neuro_risk_factors.append(max(0, diet_risk_factor))  # Ensure non-negative
        
        # Calculate overall neurological risk
        neurological_risk = sum(neuro_risk_factors) / len(neuro_risk_factors)
        neurological_risk = min(1.0, neurological_risk)  # Cap at 1.0
        
        # Calculate cancer risk
        # Use average of genetic cancer risks and adjust for lifestyle factors
        avg_cancer_genetic_risk = sum(cancer_genetic_risks.values()) / len(cancer_genetic_risks)
        
        cancer_risk_factors = []
        cancer_risk_factors.append(avg_cancer_genetic_risk)
        
        # Smoking factor
        if smoking_status == "current":
            smoking_risk_factor = 0.3
        elif smoking_status == "former":
            smoking_risk_factor = 0.1
        else:
            smoking_risk_factor = 0.0
        
        cancer_risk_factors.append(smoking_risk_factor)
        
        # Exercise factor (inverse relationship)
        if exercise_minutes < 30:
            exercise_risk_factor = 0.1
        else:
            exercise_risk_factor = 0.0
        
        cancer_risk_factors.append(exercise_risk_factor)
        
        # Diet factor
        if fruit_veg < 2:
            diet_risk_factor = 0.1
        else:
            diet_risk_factor = 0.0
        
        cancer_risk_factors.append(diet_risk_factor)
        
        # Calculate overall cancer risk
        cancer_risk = sum(cancer_risk_factors) / len(cancer_risk_factors)
        cancer_risk = min(1.0, cancer_risk)  # Cap at 1.0
        
        # Format the results
        risk_assessment = {
            "user_id": user_profile["user_id"],
            "risks": {
                "cardiovascular": {
                    "risk_level": round(cardiovascular_risk, 2),
                    "category": self._categorize_risk(cardiovascular_risk),
                    "factors": {
                        "genetic": round(cardiovascular_genetic_risk, 2),
                        "blood_pressure": round(bp_risk_factor, 2),
                        "cholesterol": round(chol_risk_factor, 2),
                        "smoking": round(smoking_risk_factor, 2),
                        "exercise": round(exercise_risk_factor, 2),
                        "bmi": round(bmi_risk_factor, 2)
                    }
                },
                "metabolic": {
                    "risk_level": round(metabolic_risk, 2),
                    "category": self._categorize_risk(metabolic_risk),
                    "factors": {
                        "genetic": round(diabetes_genetic_risk, 2),
                        "glucose": round(glucose_risk_factor, 2),
                        "bmi": round(bmi_risk_factor, 2),
                        "exercise": round(exercise_risk_factor, 2),
                        "diet": round(diet_risk_factor, 2)
                    }
                },
                "neurological": {
                    "risk_level": round(neurological_risk, 2),
                    "category": self._categorize_risk(neurological_risk),
                    "factors": {
                        "genetic": round(neuro_genetic_risk, 2),
                        "sleep": round(sleep_risk_factor, 2),
                        "stress": round(stress_risk_factor, 2),
                        "exercise": round(exercise_risk_factor, 2),
                        "diet": round(diet_risk_factor, 2)
                    }
                },
                "cancer": {
                    "risk_level": round(cancer_risk, 2),
                    "category": self._categorize_risk(cancer_risk),
                    "factors": {
                        "genetic": round(avg_cancer_genetic_risk, 2),
                        "smoking": round(smoking_risk_factor, 2),
                        "exercise": round(exercise_risk_factor, 2),
                        "diet": round(diet_risk_factor, 2)
                    }
                }
            },
            "assessed_at": datetime.now().isoformat()
        }
        
        return risk_assessment
    
    def _categorize_risk(self, risk_level: float) -> str:
        """
        Categorize numerical risk level into descriptive category.
        
        Args:
            risk_level: Numerical risk level between 0 and 1
            
        Returns:
            Risk category as string
        """
        if risk_level < 0.15:
            return "Low"
        elif risk_level < 0.35:
            return "Moderate"
        elif risk_level < 0.60:
            return "High"
        else:
            return "Very High"
    
    def generate_recommendations(self, user_data: Dict[str, Any], 
                                predictions: Dict[str, Any],
                                risks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized health and lifestyle recommendations.
        
        Args:
            user_data: Complete user dataset
            predictions: Prediction results including life expectancy
            risks: Health risk assessment results
            
        Returns:
            Dictionary containing personalized recommendations
        """
        user_profile = user_data["user_profile"]
        health_metrics = user_data["health_metrics"]
        lifestyle_data = user_data["lifestyle_data"]
        
        # Extract key metrics
        age = user_profile["age"]
        bmi = user_profile["bmi"]
        smoking_status = user_profile["smoking_status"].lower()
        blood_pressure = health_metrics["blood_pressure"]
        resting_heart_rate = health_metrics["resting_heart_rate"]
        cholesterol = health_metrics["cholesterol"]
        sleep = lifestyle_data["sleep"]
        exercise = lifestyle_data["exercise"]
        diet = lifestyle_data["diet"]
        stress_level = lifestyle_data["stress_level"].lower()
        
        # Extract risk levels
        cardiovascular_risk = risks["risks"]["cardiovascular"]["category"]
        metabolic_risk = risks["risks"]["metabolic"]["category"]
        neurological_risk = risks["risks"]["neurological"]["category"]
        cancer_risk = risks["risks"]["cancer"]["category"]
        
        # Initialize recommendations by category
        recommendations = {
            "exercise": [],
            "nutrition": [],
            "sleep": [],
            "stress_management": [],
            "health_monitoring": [],
            "lifestyle": []
        }
        
        # 1. Exercise recommendations
        if exercise["minutes_per_week"] < 30:
            recommendations["exercise"].append({
                "priority": "High",
                "recommendation": "Start with 10 minutes of moderate activity daily, gradually increasing to at least 30 minutes per day, 5 days per week.",
                "impact": "Essential for cardiovascular health, metabolic health, and longevity"
            })
        elif exercise["minutes_per_week"] < 150:
            recommendations["exercise"].append({
                "priority": "Medium",
                "recommendation": "Increase physical activity to reach at least 150 minutes of moderate exercise per week.",
                "impact": "Can reduce cardiovascular and metabolic disease risk by 20-30%"
            })
        else:
            recommendations["exercise"].append({
                "priority": "Low",
                "recommendation": "Maintain current exercise levels and consider adding strength training if not already included.",
                "impact": "Helps maintain muscle mass and metabolic health with aging"
            })
        
        # Add specific exercise types based on risk categories
        if cardiovascular_risk in ["High", "Very High"] or resting_heart_rate > 80:
            recommendations["exercise"].append({
                "priority": "High",
                "recommendation": "Include aerobic exercises like brisk walking, swimming, or cycling at least 3 times per week.",
                "impact": "Can significantly improve heart health and lower resting heart rate"
            })
        
        if age > 50 or "weight training" not in [t.lower() for t in exercise["types"]]:
            recommendations["exercise"].append({
                "priority": "Medium",
                "recommendation": "Add resistance training exercises 2-3 times per week to maintain muscle mass and bone density.",
                "impact": "Critical for maintaining functional independence with age"
            })
        
        # 2. Nutrition recommendations
        if diet["fruit_veg_servings_daily"] < 3:
            recommendations["nutrition"].append({
                "priority": "High",
                "recommendation": "Increase fruit and vegetable intake to at least 5 servings per day.",
                "impact": "Associated with reduced risk of cardiovascular disease, cancer, and all-cause mortality"
            })
        
        if diet["processed_food_frequency"] in ["often", "very frequently"]:
            recommendations["nutrition"].append({
                "priority": "High",
                "recommendation": "Reduce consumption of processed foods, especially those high in added sugars and unhealthy fats.",
                "impact": "Can significantly improve metabolic health and reduce inflammation"
            })
        
        if diet["type"].lower() != "mediterranean" and (cardiovascular_risk in ["High", "Very High"] or cancer_risk in ["High", "Very High"]):
            recommendations["nutrition"].append({
                "priority": "Medium",
                "recommendation": "Consider adopting a Mediterranean diet pattern rich in olive oil, nuts, fish, and whole grains.",
                "impact": "Strong evidence for reducing cardiovascular disease risk and certain cancers"
            })
        
        # 3. Sleep recommendations
        if sleep["average_hours"] < 7 or sleep["quality"].lower() in ["poor", "fair"]:
            recommendations["sleep"].append({
                "priority": "High",
                "recommendation": "Aim for 7-8 hours of quality sleep per night by establishing a regular sleep schedule and optimizing your sleep environment.",
                "impact": "Critical for cognitive function, immune health, and metabolic regulation"
            })
            
            if sleep["quality"].lower() == "poor":
                recommendations["sleep"].append({
                    "priority": "Medium",
                    "recommendation": "Implement good sleep hygiene practices: limit screen time before bed, keep bedroom cool and dark, avoid caffeine after noon.",
                    "impact": "Can significantly improve sleep onset and quality"
                })
        
        # 4. Stress management recommendations
        if stress_level in ["high", "very high"]:
            recommendations["stress_management"].append({
                "priority": "High",
                "recommendation": "Incorporate daily stress reduction practices such as meditation, deep breathing, or mindfulness for at least 10-15 minutes.",
                "impact": "Reduces stress hormones and improves cardiovascular and immune function"
            })
            
            recommendations["stress_management"].append({
                "priority": "Medium",
                "recommendation": "Consider limiting exposure to stressors, including reducing news consumption and setting boundaries on work hours.",
                "impact": "Helps manage chronic stress that contributes to premature aging"
            })
        
        # 5. Health monitoring recommendations
        if age > 40:
            recommendations["health_monitoring"].append({
                "priority": "Medium",
                "recommendation": "Schedule annual comprehensive health check-ups including cardiovascular assessment and appropriate cancer screenings.",
                "impact": "Early detection significantly improves treatment outcomes"
            })
        
        if bmi > 30 or metabolic_risk in ["High", "Very High"]:
            recommendations["health_monitoring"].append({
                "priority": "High",
                "recommendation": "Monitor blood glucose levels regularly and get HbA1c tested every 6 months.",
                "impact": "Helps detect prediabetes early when lifestyle interventions are most effective"
            })
        
        if blood_pressure["systolic"] > 130 or blood_pressure["diastolic"] > 85:
            recommendations["health_monitoring"].append({
                "priority": "High",
                "recommendation": "Track blood pressure weekly and work with healthcare provider to develop a management plan.",
                "impact": "Reduces risk of stroke, heart disease, and kidney problems"
            })
        
        # 6. Lifestyle recommendations
        if smoking_status == "current":
            recommendations["lifestyle"].append({
                "priority": "Very High",
                "recommendation": "Quit smoking with appropriate cessation support such as counseling, nicotine replacement, or medications.",
                "impact": "Single most effective action to improve health and longevity, adding up to 10 years of life"
            })
        
        if user_profile["alcohol_frequency"].lower() == "frequent":
            recommendations["lifestyle"].append({
                "priority": "High",
                "recommendation": "Reduce alcohol consumption to no more than 1 drink per day for women or 2 drinks per day for men.",
                "impact": "Reduces risk of liver disease, cancer, and cardiovascular problems"
            })
        
        # Format the recommendations output
        recommendations_result = {
            "user_id": user_profile["user_id"],
            "recommendations": recommendations,
            "top_priorities": self._extract_high_priority_recommendations(recommendations),
            "potential_impact": self._estimate_impact_on_life_expectancy(recommendations, predictions),
            "generated_at": datetime.now().isoformat()
        }
        
        return recommendations_result
    
    def _extract_high_priority_recommendations(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract high priority recommendations from all categories.
        
        Args:
            recommendations: Dictionary of recommendations by category
            
        Returns:
            List of high priority recommendations
        """
        high_priority = []
        
        for category, recs in recommendations.items():
            for rec in recs:
                if rec["priority"] in ["High", "Very High"]:
                    high_priority.append({
                        "category": category,
                        "recommendation": rec["recommendation"],
                        "priority": rec["priority"],
                        "impact": rec["impact"]
                    })
        
        # Sort by priority (Very High first, then High)
        high_priority.sort(key=lambda x: 0 if x["priority"] == "Very High" else 1)
        
        return high_priority
    
    def _estimate_impact_on_life_expectancy(self, recommendations: Dict[str, List[Dict[str, Any]]],
                                          predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the potential impact of following recommendations on life expectancy.
        
        Args:
            recommendations: Dictionary of recommendations by category
            predictions: Current life expectancy predictions
            
        Returns:
            Dictionary with estimated impact on life expectancy
        """
        # Count high priority recommendations
        high_priority_count = sum(1 for cat in recommendations.values() 
                                for rec in cat if rec["priority"] in ["High", "Very High"])
        
        # Estimate potential years gained based on recommendation count and priority
        potential_years_gained = min(high_priority_count * 0.8, 8.0)
        
        # Current life expectancy from predictions
        current_life_expectancy = predictions["predicted_life_expectancy"]
        
        # Calculate potential new life expectancy
        potential_life_expectancy = current_life_expectancy + potential_years_gained
        
        return {
            "current_life_expectancy": current_life_expectancy,
            "potential_life_expectancy": round(potential_life_expectancy, 1),
            "potential_years_gained": round(potential_years_gained, 1),
            "note": "Estimated impact if all high priority recommendations are followed consistently"
        }
    
    def run_complete_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a complete analysis for the user, including all predictions and recommendations.
        
        Args:
            user_data: Complete user dataset
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        try:
            # 1. Predict life expectancy
            life_expectancy = self.predict_life_expectancy(user_data)
            
            # 2. Calculate biological age
            biological_age = self.calculate_biological_age(user_data)
            
            # 3. Assess health risks
            health_risks = self.calculate_health_risks(user_data)
            
            # 4. Generate recommendations
            recommendations = self.generate_recommendations(user_data, life_expectancy, health_risks)
            
            # Combine results into comprehensive analysis
            analysis_results = {
                "user_id": user_data["user_profile"]["user_id"],
                "life_expectancy": life_expectancy,
                "biological_age": biological_age,
                "health_risks": health_risks,
                "recommendations": recommendations,
                "status": "success",
                "analysis_completed_at": datetime.now().isoformat()
            }
            
            return analysis_results
            
        except Exception as e:
            # Return error status and message
            error_results = {
                "user_id": user_data["user_profile"]["user_id"] if "user_profile" in user_data else "unknown",
                "status": "error",
                "error_message": str(e),
                "analysis_attempted_at": datetime.now().isoformat()
            }
            
            return error_results


if __name__ == "__main__":
    # Example usage
    from simulation.data_generator import DataGenerator
    
    # Generate synthetic user data
    generator = DataGenerator(seed=42)
    user_data = generator.generate_complete_user_dataset()
    
    # Initialize predictor and run analysis
    predictor = LifePredictor()
    results = predictor.run_complete_analysis(user_data)
    
    # Save results to file
    output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, f"{user_data['user_profile']['user_id']}_analysis.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Analysis complete. Results saved to file.")
