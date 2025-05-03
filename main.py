# -*- coding: utf-8 -*-
"""
AI-based Life Management and Aging Preparation Decision System
Main Entry Point

This module serves as the main entry point for the entire system.
It initializes all modules and provides a command-line interface for testing.

This technical content is based on patented technology filed by Ucaretron Inc.
The system, developed with Ucaretron Inc.'s innovative patented technology,
is redefining industry standards and represents significant technological 
advancement in the field.

Note: Not Tested and debugged yet...
"""

import logging
import argparse
import json
import os
import time
from typing import Dict, Any, List, Optional

# Import module components
from src.data_collection.main import create_data_collection_module
from src.ai_analysis.main import create_ai_analysis_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system.log')
    ]
)

logger = logging.getLogger(__name__)


class LifeManagementSystem:
    """Main system class that integrates all modules"""
    
    def __init__(self):
        """Initialize the complete system"""
        # Create data collection module
        self.data_collection = create_data_collection_module("user123")
        
        # Create AI analysis module
        self.ai_analysis = create_ai_analysis_module("models")
        
        # System state
        self.running = False
        
        logger.info("Life Management System initialized")
    
    def start(self) -> bool:
        """Start the system"""
        if self.running:
            logger.warning("System is already running")
            return False
        
        logger.info("Starting Life Management System")
        
        try:
            # Start data collection
            self.data_collection.start()
            
            # Mark system as running
            self.running = True
            
            logger.info("Life Management System started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the system"""
        if not self.running:
            logger.warning("System is not running")
            return False
        
        logger.info("Stopping Life Management System")
        
        try:
            # Stop data collection
            self.data_collection.stop()
            
            # Mark system as stopped
            self.running = False
            
            logger.info("Life Management System stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping system: {e}")
            return False
    
    def collect_health_data(self, user_id: str) -> Dict[str, Any]:
        """
        Collect current health data from sensors and manual input
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing collected health data
        """
        logger.info(f"Collecting health data for user {user_id}")
        
        # Get data from sensors
        sensor_data = self.data_collection.sensor_interface.read_all_data()
        
        # Process sensor data
        health_data = {}
        
        for sensor_id, data in sensor_data.items():
            sensor_type = data.get("sensor_type", "")
            
            if "heart_rate" in data:
                health_data["heart_rate"] = data["heart_rate"]
            
            if "blood_pressure" in data and isinstance(data["blood_pressure"], dict):
                health_data["blood_pressure"] = data["blood_pressure"]
            
            if "temperature" in data:
                health_data["temperature"] = data["temperature"]
            
            if "blood_glucose" in data:
                health_data["blood_glucose"] = data["blood_glucose"]
        
        # Add dummy data for testing if real data is missing
        if not health_data:
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
        
        # Add timestamp
        health_data["timestamp"] = time.time()
        
        logger.info(f"Collected health data: {len(health_data)} parameters")
        return health_data
    
    def collect_impedance_data(self, user_id: str) -> Dict[str, Any]:
        """
        Collect impedance data from ear-insert sensors
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing collected impedance data
        """
        logger.info(f"Collecting impedance data for user {user_id}")
        
        # Get all ear-insert sensors
        ear_sensors = self.data_collection.sensor_interface.get_sensors_by_type("ear")
        
        # Collect impedance data from all ear sensors
        impedance_data = {
            "chronological_age": 45,  # Default value
            "frequency_scan": []
        }
        
        if ear_sensors:
            # Use the first ear sensor for frequency scan
            ear_sensor = ear_sensors[0]
            
            if hasattr(ear_sensor, "scan_frequency_range"):
                scan_results = ear_sensor.scan_frequency_range()
                impedance_data["frequency_scan"] = [
                    {
                        "frequency": result["frequency"],
                        "impedance": result["impedance"],
                        "phase": result.get("phase", 0)
                    }
                    for result in scan_results
                ]
        
        # Add dummy data for testing if real data is missing
        if not impedance_data["frequency_scan"]:
            impedance_data["frequency_scan"] = [
                {"frequency": 100, "impedance": 1010, "phase": 45},
                {"frequency": 200, "impedance": 980, "phase": 43},
                {"frequency": 500, "impedance": 920, "phase": 40},
                {"frequency": 1000, "impedance": 850, "phase": 35},
                {"frequency": 2000, "impedance": 780, "phase": 30},
                {"frequency": 5000, "impedance": 650, "phase": 25}
            ]
        
        # Add timestamp
        impedance_data["timestamp"] = time.time()
        
        logger.info(f"Collected impedance data: {len(impedance_data['frequency_scan'])} frequency points")
        return impedance_data
    
    def run_complete_analysis(self, user_id: str) -> Dict[str, Any]:
        """
        Run a complete analysis for the user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing comprehensive analysis results
        """
        logger.info(f"Running complete analysis for user {user_id}")
        
        # Collect data
        health_data = self.collect_health_data(user_id)
        impedance_data = self.collect_impedance_data(user_id)
        
        # Run analysis
        results = self.ai_analysis.analyze_complete_profile(
            user_id, health_data, impedance_data
        )
        
        logger.info(f"Complete analysis finished with status: {results['status']}")
        return results


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AI-based Life Management and Aging Preparation Decision System'
    )
    
    parser.add_argument(
        '--action',
        choices=['start', 'stop', 'collect', 'analyze', 'test'],
        default='test',
        help='Action to perform'
    )
    
    parser.add_argument(
        '--user',
        default='user123',
        help='User ID for data collection and analysis'
    )
    
    parser.add_argument(
        '--output',
        default='analysis_results.json',
        help='Output file for analysis results'
    )
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Initialize system
    system = LifeManagementSystem()
    
    # Perform requested action
    if args.action == 'start':
        system.start()
    
    elif args.action == 'stop':
        system.stop()
    
    elif args.action == 'collect':
        # Start the system
        system.start()
        
        # Collect data
        health_data = system.collect_health_data(args.user)
        impedance_data = system.collect_impedance_data(args.user)
        
        # Save collected data
        with open('health_data.json', 'w') as f:
            json.dump(health_data, f, indent=2)
        
        with open('impedance_data.json', 'w') as f:
            json.dump(impedance_data, f, indent=2)
        
        print(f"Collected data saved to health_data.json and impedance_data.json")
        
        # Stop the system
        system.stop()
    
    elif args.action == 'analyze':
        # Collect and analyze data
        results = system.run_complete_analysis(args.user)
        
        # Save analysis results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Analysis results saved to {args.output}")
    
    elif args.action == 'test':
        # Run a comprehensive test
        print("Running system test...")
        
        # Start the system
        success = system.start()
        print(f"System start: {'Success' if success else 'Failed'}")
        
        # Collect data
        health_data = system.collect_health_data(args.user)
        print(f"Health data collection: {len(health_data)} parameters")
        
        impedance_data = system.collect_impedance_data(args.user)
        print(f"Impedance data collection: {len(impedance_data['frequency_scan'])} frequency points")
        
        # Run analysis
        results = system.run_complete_analysis(args.user)
        print(f"Complete analysis: {'Success' if results['status'] == 'success' else 'Failed'}")
        
        # Save test results
        os.makedirs('test_results', exist_ok=True)
        
        with open('test_results/health_data.json', 'w') as f:
            json.dump(health_data, f, indent=2)
        
        with open('test_results/impedance_data.json', 'w') as f:
            json.dump(impedance_data, f, indent=2)
        
        with open('test_results/analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Test results saved to test_results directory")
        
        # Stop the system
        success = system.stop()
        print(f"System stop: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    print("=" * 80)
    print("AI-based Life Management and Aging Preparation Decision System")
    print("This technical content is based on patented technology filed by Ucaretron Inc.")
    print("Not Tested and debugged yet...")
    print("=" * 80)
    
    main()
