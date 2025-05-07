"""
Data Generator for AI Life Management System Simulation

This module generates synthetic health, genetic, lifestyle, and biosensor data
for testing the AI-based Life Management and Aging Preparation Decision System.

Based on patented technology by Ucaretron Inc.
"""

import numpy as np
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union


class DataGenerator:
    """
    Generates synthetic data for the AI Life Management System simulation.
    
    This class creates realistic health metrics, biosensor readings, lifestyle data,
    and genetic information that can be used to test the prediction and recommendation
    capabilities of the system.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data generator with optional random seed for reproducibility.
        
        Args:
            seed: Optional random seed for reproducible data generation
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def generate_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a synthetic user profile.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing user profile information
        """
        # Base profiles with variations
        genders = ['Male', 'Female']
        gender = random.choice(genders)
        
        age = random.randint(25, 65)
        
        # Height in cm
        if gender == 'Male':
            height = round(np.random.normal(175, 8), 1)
        else:
            height = round(np.random.normal(162, 7), 1)
        
        # Weight in kg
        weight_mean = (height - 100) + (10 if gender == 'Male' else 0)
        weight_std = weight_mean * 0.15
        weight = round(np.random.normal(weight_mean, weight_std), 1)
        
        # Calculate BMI (weight in kg / (height in m)^2)
        bmi = round(weight / ((height / 100) ** 2), 1)
        
        # Smoking status
        smoking_status = random.choices(
            ['Never', 'Former', 'Current'], 
            weights=[0.7, 0.2, 0.1], 
            k=1
        )[0]
        
        # Alcohol consumption
        alcohol_frequency = random.choices(
            ['None', 'Rare', 'Moderate', 'Frequent'], 
            weights=[0.2, 0.3, 0.4, 0.1], 
            k=1
        )[0]
        
        # Family history
        family_history = {
            "cardiovascular_disease": random.choices([True, False], weights=[0.3, 0.7], k=1)[0],
            "diabetes": random.choices([True, False], weights=[0.2, 0.8], k=1)[0],
            "cancer": random.choices([True, False], weights=[0.25, 0.75], k=1)[0],
            "neurodegenerative_disease": random.choices([True, False], weights=[0.15, 0.85], k=1)[0]
        }
        
        # Create the user profile
        user_profile = {
            "user_id": user_id,
            "gender": gender,
            "age": age,
            "height_cm": height,
            "weight_kg": weight,
            "bmi": bmi,
            "smoking_status": smoking_status,
            "alcohol_frequency": alcohol_frequency,
            "family_history": family_history,
            "created_at": datetime.now().isoformat(),
        }
        
        return user_profile
    
    def generate_health_metrics(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate synthetic health metrics based on user profile.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Dictionary containing health metrics
        """
        age = user_profile["age"]
        gender = user_profile["gender"]
        bmi = user_profile["bmi"]
        smoking = user_profile["smoking_status"]
        
        # Base values with variations based on user profile
        # Blood pressure (systolic/diastolic)
        # Age affects BP: ~+0.5 mmHg per year after 30
        age_factor = max(0, age - 30) * 0.5
        
        # BMI affects BP: ~+1 mmHg per BMI point above 25
        bmi_factor = max(0, bmi - 25)
        
        # Smoking affects BP: +5-10 mmHg for current smokers
        smoking_factor = 7 if smoking == "Current" else (3 if smoking == "Former" else 0)
        
        # Base values with factors
        systolic_base = 110 if gender == "Female" else 115
        systolic = round(np.random.normal(systolic_base + age_factor + bmi_factor + smoking_factor, 8))
        
        diastolic_base = 70 if gender == "Female" else 75
        diastolic = round(np.random.normal(diastolic_base + (age_factor / 2) + (bmi_factor / 2) + (smoking_factor / 2), 6))
        
        # Resting heart rate (bpm)
        # Lower for more physically active people
        fitness_level = random.uniform(0, 1)  # Random fitness level
        heart_rate_base = 75 - (fitness_level * 15)  # Fitter = lower resting heart rate
        heart_rate = round(np.random.normal(heart_rate_base, 5))
        
        # Total cholesterol (mg/dL)
        # Increases with age, affected by diet and genetics
        chol_age_factor = max(0, age - 20) * 0.5
        chol_bmi_factor = max(0, bmi - 25) * 2
        
        cholesterol = round(np.random.normal(170 + chol_age_factor + chol_bmi_factor, 15))
        
        # HDL cholesterol (mg/dL)
        # Higher is better, women tend to have higher HDL
        hdl_base = 50 if gender == "Female" else 40
        hdl = round(np.random.normal(hdl_base, 8))
        hdl = min(hdl, cholesterol - 50)  # Ensure HDL doesn't exceed total cholesterol
        
        # LDL cholesterol (mg/dL)
        # Lower is better
        ldl = cholesterol - hdl - round(np.random.normal(30, 5))  # Subtract HDL and estimated triglycerides/5
        ldl = max(ldl, 30)  # Ensure LDL doesn't go below 30
        
        # Fasting blood glucose (mg/dL)
        glucose_bmi_factor = max(0, bmi - 25) * 0.5
        glucose = round(np.random.normal(85 + glucose_bmi_factor, 8))
        
        # HbA1c (%)
        hba1c = round(np.random.normal(5.0 + (glucose - 85) * 0.02, 0.3), 1)
        
        # VO2 max (mL/kg/min) - measure of cardiorespiratory fitness
        # Decreases with age, higher for physically active people
        vo2max_age_factor = max(0, age - 20) * 0.3
        vo2max_base = 45 if gender == "Male" else 35
        vo2max = round(np.random.normal(vo2max_base - vo2max_age_factor + (fitness_level * 15), 5), 1)
        
        # Body fat percentage
        # Increases with BMI, varies by gender
        if gender == "Male":
            body_fat = round(np.random.normal(15 + max(0, bmi - 22) * 1.5, 3), 1)
        else:
            body_fat = round(np.random.normal(25 + max(0, bmi - 22) * 1.3, 3), 1)
        
        # Create health metrics
        health_metrics = {
            "user_id": user_profile["user_id"],
            "blood_pressure": {
                "systolic": systolic,
                "diastolic": diastolic
            },
            "resting_heart_rate": heart_rate,
            "cholesterol": {
                "total": cholesterol,
                "hdl": hdl,
                "ldl": ldl
            },
            "fasting_glucose": glucose,
            "hba1c": hba1c,
            "vo2_max": vo2max,
            "body_fat_percentage": body_fat,
            "measured_at": datetime.now().isoformat()
        }
        
        return health_metrics
    
    def generate_impedance_data(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate synthetic electrochemical impedance data from ear-insert sensors.
        This is a key technology in the Ucaretron Inc. patent.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Dictionary containing impedance data across frequency ranges
        """
        age = user_profile["age"]
        
        # Generate frequency scan data
        # Frequencies in Hz
        frequencies = [100, 200, 500, 1000, 2000, 5000, 10000, 20000]
        
        # Base impedance values that vary with frequency (impedance decreases with frequency)
        base_impedance = [1000, 900, 800, 700, 600, 500, 400, 300]
        
        # Phase angle values (different pattern across frequencies)
        base_phase = [45, 40, 35, 30, 25, 20, 15, 10]
        
        # Biological age is simulated based on chronological age with some variation
        biological_age_factor = np.random.normal(0, 5)  # Can be ±5 years typically
        biological_age = max(20, age + biological_age_factor)
        
        # Generate scan results with variations
        scan_results = []
        for i, freq in enumerate(frequencies):
            # Impedance varies with biological age
            age_impedance_factor = 1 + (biological_age - 40) / 100
            
            # Add random variations
            impedance_variation = np.random.normal(0, base_impedance[i] * 0.05)
            phase_variation = np.random.normal(0, 3)
            
            impedance = round(base_impedance[i] * age_impedance_factor + impedance_variation)
            phase = round(base_phase[i] + phase_variation, 1)
            
            scan_results.append({
                "frequency": freq,
                "impedance": impedance,
                "phase": phase
            })
        
        # Create impedance data
        impedance_data = {
            "user_id": user_profile["user_id"],
            "device_id": f"EAR-IMP-{random.randint(1000, 9999)}",
            "chronological_age": age,
            "estimated_biological_age": round(biological_age, 1),
            "frequency_scan": scan_results,
            "measured_at": datetime.now().isoformat()
        }
        
        return impedance_data
    
    def generate_lifestyle_data(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate synthetic lifestyle data for the user.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Dictionary containing lifestyle data
        """
        # Exercise habits
        exercise_frequency = random.choices(
            ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
            weights=[0.2, 0.3, 0.3, 0.15, 0.05],
            k=1
        )[0]
        
        if exercise_frequency == "Sedentary":
            exercise_minutes_per_week = random.randint(0, 30)
        elif exercise_frequency == "Light":
            exercise_minutes_per_week = random.randint(30, 90)
        elif exercise_frequency == "Moderate":
            exercise_minutes_per_week = random.randint(90, 180)
        elif exercise_frequency == "Active":
            exercise_minutes_per_week = random.randint(180, 300)
        else:  # Very Active
            exercise_minutes_per_week = random.randint(300, 600)
        
        # Exercise types
        exercise_types = ["Walking", "Running", "Cycling", "Swimming", "Weight Training", 
                          "Yoga", "Team Sports", "HIIT", "Pilates", "Dancing"]
        
        num_exercise_types = random.choices([0, 1, 2, 3, 4], weights=[0.2, 0.3, 0.3, 0.15, 0.05], k=1)[0]
        
        if num_exercise_types == 0:
            selected_exercise_types = []
        else:
            selected_exercise_types = random.sample(exercise_types, num_exercise_types)
        
        # Sleep patterns
        avg_sleep_hours = round(np.random.normal(7, 1), 1)
        sleep_quality = random.choices(
            ["Poor", "Fair", "Good", "Excellent"],
            weights=[0.1, 0.3, 0.4, 0.2],
            k=1
        )[0]
        
        # Diet information
        diet_type = random.choices(
            ["Standard", "Mediterranean", "Vegetarian", "Vegan", "Low-carb", "Pescatarian"],
            weights=[0.5, 0.15, 0.15, 0.05, 0.1, 0.05],
            k=1
        )[0]
        
        fruit_veg_servings = round(np.random.normal(3, 1.5))
        fruit_veg_servings = max(0, fruit_veg_servings)
        
        processed_food_frequency = random.choices(
            ["Rarely", "Sometimes", "Often", "Very Frequently"],
            weights=[0.1, 0.4, 0.4, 0.1],
            k=1
        )[0]
        
        # Stress levels
        stress_level = random.choices(
            ["Low", "Moderate", "High", "Very High"],
            weights=[0.1, 0.5, 0.3, 0.1],
            k=1
        )[0]
        
        # Create lifestyle data
        lifestyle_data = {
            "user_id": user_profile["user_id"],
            "exercise": {
                "frequency": exercise_frequency,
                "minutes_per_week": exercise_minutes_per_week,
                "types": selected_exercise_types
            },
            "sleep": {
                "average_hours": avg_sleep_hours,
                "quality": sleep_quality
            },
            "diet": {
                "type": diet_type,
                "fruit_veg_servings_daily": fruit_veg_servings,
                "processed_food_frequency": processed_food_frequency
            },
            "stress_level": stress_level,
            "recorded_at": datetime.now().isoformat()
        }
        
        return lifestyle_data
    
    def generate_genetic_risk_data(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate synthetic genetic risk factor data.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Dictionary containing genetic risk data
        """
        # Family history from user profile affects genetic risk
        family_history = user_profile["family_history"]
        
        # Base genetic risk factors
        risk_factors = {
            "cardiovascular_disease": random.uniform(0.05, 0.15),
            "type_2_diabetes": random.uniform(0.05, 0.15),
            "cancer": {
                "colorectal": random.uniform(0.03, 0.08),
                "breast": random.uniform(0.03, 0.08) if user_profile["gender"] == "Female" else 0.001,
                "prostate": random.uniform(0.05, 0.10) if user_profile["gender"] == "Male" else 0,
                "lung": random.uniform(0.02, 0.06),
                "skin": random.uniform(0.02, 0.07)
            },
            "neurodegenerative": {
                "alzheimers": random.uniform(0.02, 0.08),
                "parkinsons": random.uniform(0.01, 0.04)
            },
            "autoimmune": {
                "rheumatoid_arthritis": random.uniform(0.01, 0.03),
                "multiple_sclerosis": random.uniform(0.005, 0.02)
            }
        }
        
        # Adjust risk based on family history
        if family_history["cardiovascular_disease"]:
            risk_factors["cardiovascular_disease"] *= random.uniform(1.5, 2.5)
            
        if family_history["diabetes"]:
            risk_factors["type_2_diabetes"] *= random.uniform(1.5, 2.5)
            
        if family_history["cancer"]:
            # Increase all cancer risks
            for cancer_type in risk_factors["cancer"]:
                risk_factors["cancer"][cancer_type] *= random.uniform(1.3, 2.0)
                
        if family_history["neurodegenerative_disease"]:
            risk_factors["neurodegenerative"]["alzheimers"] *= random.uniform(1.5, 3.0)
            risk_factors["neurodegenerative"]["parkinsons"] *= random.uniform(1.5, 2.5)
        
        # Ensure risks are between 0 and 1
        risk_factors["cardiovascular_disease"] = min(1.0, risk_factors["cardiovascular_disease"])
        risk_factors["type_2_diabetes"] = min(1.0, risk_factors["type_2_diabetes"])
        
        for category in ["cancer", "neurodegenerative", "autoimmune"]:
            for risk_type in risk_factors[category]:
                risk_factors[category][risk_type] = min(1.0, risk_factors[category][risk_type])
        
        # Create genetic risk data
        genetic_data = {
            "user_id": user_profile["user_id"],
            "risk_factors": risk_factors,
            "analysis_method": "Simulated genetic profile analysis",
            "analyzed_at": datetime.now().isoformat()
        }
        
        return genetic_data
    
    def generate_daily_vitals(self, user_profile: Dict[str, Any], 
                             base_health_metrics: Dict[str, Any],
                             days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate synthetic daily vital signs for a given number of days.
        
        Args:
            user_profile: User profile dictionary
            base_health_metrics: Base health metrics to use as a starting point
            days: Number of days of data to generate
            
        Returns:
            List of dictionaries containing daily vital signs
        """
        daily_vitals = []
        
        # Base values from health metrics
        base_heart_rate = base_health_metrics["resting_heart_rate"]
        base_systolic = base_health_metrics["blood_pressure"]["systolic"]
        base_diastolic = base_health_metrics["blood_pressure"]["diastolic"]
        
        # Generate daily readings with realistic variations
        for i in range(days):
            # Date for this reading
            date = (datetime.now() - timedelta(days=days-i-1)).date().isoformat()
            
            # Variations for each day
            heart_rate = round(np.random.normal(base_heart_rate, 5))
            systolic = round(np.random.normal(base_systolic, 8))
            diastolic = round(np.random.normal(base_diastolic, 6))
            
            # Occasionally add more significant variations
            if random.random() < 0.1:  # 10% chance of higher BP day
                systolic += random.randint(5, 15)
                diastolic += random.randint(3, 8)
            
            if random.random() < 0.1:  # 10% chance of higher heart rate day
                heart_rate += random.randint(5, 20)
            
            # Steps count based on activity level
            activity_level = random.random()
            steps = int(np.random.normal(7000 * activity_level, 2000))
            steps = max(0, steps)
            
            # Sleep data
            sleep_hours = round(np.random.normal(7, 1.2), 1)
            sleep_hours = max(3.0, min(12.0, sleep_hours))
            
            # Create daily vitals record
            vitals = {
                "user_id": user_profile["user_id"],
                "date": date,
                "heart_rate": heart_rate,
                "blood_pressure": {
                    "systolic": systolic,
                    "diastolic": diastolic
                },
                "steps": steps,
                "sleep_hours": sleep_hours,
                "active_minutes": int(steps / 100),  # Rough estimate
            }
            
            daily_vitals.append(vitals)
        
        return daily_vitals
    
    def generate_complete_user_dataset(self, user_id: str = None) -> Dict[str, Any]:
        """
        Generate a complete dataset for a user including all data types.
        
        Args:
            user_id: Optional user ID (generated if not provided)
            
        Returns:
            Dictionary containing all user data
        """
        if user_id is None:
            user_id = f"user_{random.randint(1000, 9999)}"
        
        # Generate all data types
        user_profile = self.generate_user_profile(user_id)
        health_metrics = self.generate_health_metrics(user_profile)
        impedance_data = self.generate_impedance_data(user_profile)
        lifestyle_data = self.generate_lifestyle_data(user_profile)
        genetic_data = self.generate_genetic_risk_data(user_profile)
        daily_vitals = self.generate_daily_vitals(user_profile, health_metrics, days=30)
        
        # Combine into a complete dataset
        complete_data = {
            "user_profile": user_profile,
            "health_metrics": health_metrics,
            "impedance_data": impedance_data,
            "lifestyle_data": lifestyle_data,
            "genetic_data": genetic_data,
            "daily_vitals": daily_vitals
        }
        
        return complete_data
    
    def save_user_dataset(self, user_data: Dict[str, Any]) -> str:
        """
        Save a user dataset to a JSON file.
        
        Args:
            user_data: User dataset to save
            
        Returns:
            Path to the saved file
        """
        user_id = user_data["user_profile"]["user_id"]
        file_path = os.path.join(self.data_dir, f"{user_id}_data.json")
        
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return file_path
    
    def generate_multiple_users(self, num_users: int = 5) -> List[Dict[str, Any]]:
        """
        Generate datasets for multiple users.
        
        Args:
            num_users: Number of user datasets to generate
            
        Returns:
            List of user datasets
        """
        users_data = []
        
        for i in range(num_users):
            user_id = f"user_{i+1:04d}"
            user_data = self.generate_complete_user_dataset(user_id)
            self.save_user_dataset(user_data)
            users_data.append(user_data)
        
        return users_data


if __name__ == "__main__":
    # Example usage
    generator = DataGenerator(seed=42)
    user_data = generator.generate_complete_user_dataset()
    file_path = generator.save_user_dataset(user_data)
    print(f"Generated user data saved to: {file_path}")
    
    # Generate multiple users
    users = generator.generate_multiple_users(5)
    print(f"Generated data for {len(users)} users")
