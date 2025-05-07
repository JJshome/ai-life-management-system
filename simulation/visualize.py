#!/usr/bin/env python3
"""
Visualization Module for AI Life Management System Simulation

This module provides visualization functions for displaying the results 
of the AI-based Life Management and Aging Preparation Decision System simulation.

Based on patented technology by Ucaretron Inc.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
from typing import Dict, List, Any, Optional, Union, Tuple

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('viridis')


class ResultsVisualizer:
    """
    Class for visualizing simulation results from the AI Life Management System.
    
    This class provides functions to create various types of visualizations from the
    simulation results, including life expectancy predictions, biological age comparisons,
    health risk assessments, and scenario comparison charts.
    """
    
    def __init__(self, results_dir: str = None):
        """
        Initialize the visualizer with the results directory.
        
        Args:
            results_dir: Directory containing simulation results
        """
        if results_dir is None:
            # Use default results directory
            self.results_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'simulation', 'results'
            )
        else:
            self.results_dir = results_dir
            
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'docs', 'visualizations'
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_results(self, file_path: str) -> Dict[str, Any]:
        """
        Load results from a JSON file.
        
        Args:
            file_path: Path to the results file
            
        Returns:
            Dictionary containing the loaded results
        """
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def visualize_life_expectancy(self, user_id: str, save_fig: bool = True) -> plt.Figure:
        """
        Create a visualization of life expectancy prediction for a user.
        
        Args:
            user_id: ID of the user to visualize
            save_fig: Whether to save the figure to a file
            
        Returns:
            Matplotlib Figure object
        """
        # Load analysis results
        file_path = os.path.join(self.results_dir, f"{user_id}_analysis.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Analysis results not found for user {user_id}")
            
        results = self.load_results(file_path)
        
        if results["status"] != "success":
            raise ValueError(f"Analysis failed for user {user_id}: {results.get('error_message', 'Unknown error')}")
            
        life_exp = results["life_expectancy"]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        current_age = life_exp["current_age"]
        predicted_le = life_exp["predicted_life_expectancy"]
        base_le = life_exp["base_life_expectancy"]
        conf_int = life_exp["confidence_interval"]
        factors = life_exp["factors"]
        
        # Sort factors by absolute value of impact
        factors.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Create main bar for predicted life expectancy
        ax.barh("Predicted", predicted_le, height=0.6, color='#1f77b4', alpha=0.8)
        
        # Add error bars for confidence interval
        ax.plot([conf_int[0], conf_int[1]], ["Predicted", "Predicted"], 
                color='#1f77b4', linewidth=2, marker='|', markersize=10)
        
        # Add bar for base life expectancy
        ax.barh("Base Population", base_le, height=0.6, color='#ff7f0e', alpha=0.8)
        
        # Add current age reference line
        ax.axvline(x=current_age, color='red', linestyle='--', alpha=0.7, 
                   label=f"Current Age: {current_age}")
        
        # Set labels and title
        ax.set_xlabel("Age (years)")
        ax.set_title(f"Life Expectancy Prediction for User {user_id}")
        
        # Adjust limits
        ax.set_xlim(0, max(predicted_le, base_le) * 1.1)
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True, axis='x', alpha=0.3)
        
        # Add text annotations
        ax.text(predicted_le + 1, "Predicted", f"{predicted_le} years", 
                va='center', fontweight='bold')
        ax.text(base_le + 1, "Base Population", f"{base_le} years", 
                va='center', fontweight='bold')
        
        # Create a secondary visualization for factors
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        
        # Extract factor names and values
        factor_names = [f[0] for f in factors]
        factor_values = [f[1] for f in factors]
        
        # Create color map based on positive/negative impact
        colors = ['#d62728' if v < 0 else '#2ca02c' for v in factor_values]
        
        # Create horizontal bar chart
        bars = ax2.barh(factor_names, factor_values, height=0.6, color=colors, alpha=0.8)
        
        # Add zero line
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # Set labels and title
        ax2.set_xlabel("Impact on Life Expectancy (years)")
        ax2.set_title(f"Factors Affecting Life Expectancy for User {user_id}")
        
        # Add text annotations
        for i, bar in enumerate(bars):
            width = bar.get_width()
            if width > 0:
                x_pos = width + 0.1
                ax2.text(x_pos, bar.get_y() + bar.get_height()/2, 
                        f"+{width:.1f} years", va='center')
            else:
                x_pos = width - 0.1
                ax2.text(x_pos, bar.get_y() + bar.get_height()/2, 
                        f"{width:.1f} years", va='center', ha='right')
        
        # Add grid
        ax2.grid(True, axis='x', alpha=0.3)
        
        # Adjust layout
        fig.tight_layout()
        fig2.tight_layout()
        
        # Save figures if requested
        if save_fig:
            fig.savefig(os.path.join(self.output_dir, f"{user_id}_life_expectancy.png"), dpi=300)
            fig2.savefig(os.path.join(self.output_dir, f"{user_id}_life_factors.png"), dpi=300)
        
        return fig, fig2
    
    def visualize_biological_age(self, user_id: str, save_fig: bool = True) -> plt.Figure:
        """
        Create a visualization of biological age assessment for a user.
        
        Args:
            user_id: ID of the user to visualize
            save_fig: Whether to save the figure to a file
            
        Returns:
            Matplotlib Figure object
        """
        # Load analysis results
        file_path = os.path.join(self.results_dir, f"{user_id}_analysis.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Analysis results not found for user {user_id}")
            
        results = self.load_results(file_path)
        
        if results["status"] != "success":
            raise ValueError(f"Analysis failed for user {user_id}: {results.get('error_message', 'Unknown error')}")
            
        bio_age = results["biological_age"]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        chronological_age = bio_age["chronological_age"]
        biological_age = bio_age["biological_age"]
        age_diff = bio_age["age_difference"]
        factors = bio_age["factors"]
        
        # Create bar chart
        x = ["Chronological Age", "Biological Age"]
        y = [chronological_age, biological_age]
        
        # Choose colors based on biological age (green if younger, red if older)
        if age_diff < 0:
            colors = ['#1f77b4', '#d62728']
            message = f"Biological age is {abs(age_diff):.1f} years older than chronological age"
        else:
            colors = ['#1f77b4', '#2ca02c']
            message = f"Biological age is {age_diff:.1f} years younger than chronological age"
        
        ax.bar(x, y, color=colors, alpha=0.8, width=0.6)
        
        # Add text labels on top of bars
        for i, v in enumerate(y):
            ax.text(i, v + 0.5, f"{v:.1f}", ha='center', fontweight='bold')
        
        # Set labels and title
        ax.set_ylabel("Age (years)")
        ax.set_title(f"Biological vs. Chronological Age for User {user_id}")
        
        # Add explanation text
        ax.text(0.5, -0.15, message, transform=ax.transAxes, 
                ha='center', fontsize=12, fontweight='bold')
        
        # Create pie chart for factor contributions
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        
        # Extract factor names and weights
        factor_names = list(factors.keys())
        weights = [factors[f]["weight"] for f in factor_names]
        
        # Extract adjustments (for text annotations)
        adjustments = [factors[f].get("adjustment", factors[f].get("age", 0)) for f in factor_names]
        
        # Create pie chart
        wedges, texts, autotexts = ax2.pie(
            weights, 
            labels=[f.capitalize() for f in factor_names],
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': 'w'},
            textprops={'fontsize': 12}
        )
        
        # Add a circle at the center to create a donut chart
        centre_circle = plt.Circle((0, 0), 0.5, fc='white')
        ax2.add_patch(centre_circle)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax2.axis('equal')
        
        # Add title
        ax2.set_title(f"Biological Age Factor Contributions for User {user_id}")
        
        # Create a third chart for factor adjustments
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        
        # Extract cleaned factor names and adjustments
        clean_factor_names = [name.capitalize() for name in factor_names]
        
        # Create horizontal bar chart for adjustments
        bars = ax3.barh(clean_factor_names, adjustments, height=0.6, 
                       color=['#d62728' if a > 0 else '#2ca02c' for a in adjustments], alpha=0.8)
        
        # Add zero line
        ax3.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # Set labels and title
        ax3.set_xlabel("Adjustment to Biological Age (years)")
        ax3.set_title(f"Biological Age Factor Adjustments for User {user_id}")
        
        # Add text annotations
        for i, bar in enumerate(bars):
            width = bar.get_width()
            if width > 0:
                x_pos = width + 0.1
                ax3.text(x_pos, bar.get_y() + bar.get_height()/2, 
                        f"+{width:.1f} years", va='center')
            else:
                x_pos = width - 0.1
                ax3.text(x_pos, bar.get_y() + bar.get_height()/2, 
                        f"{width:.1f} years", va='center', ha='right')
        
        # Add grid
        ax3.grid(True, axis='x', alpha=0.3)
        
        # Adjust layout
        fig.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()
        
        # Save figures if requested
        if save_fig:
            fig.savefig(os.path.join(self.output_dir, f"{user_id}_biological_age.png"), dpi=300)
            fig2.savefig(os.path.join(self.output_dir, f"{user_id}_bio_age_factors.png"), dpi=300)
            fig3.savefig(os.path.join(self.output_dir, f"{user_id}_bio_age_adjustments.png"), dpi=300)
        
        return fig, fig2, fig3
    
    def visualize_health_risks(self, user_id: str, save_fig: bool = True) -> plt.Figure:
        """
        Create a visualization of health risk assessment for a user.
        
        Args:
            user_id: ID of the user to visualize
            save_fig: Whether to save the figure to a file
            
        Returns:
            Matplotlib Figure object
        """
        # Load analysis results
        file_path = os.path.join(self.results_dir, f"{user_id}_analysis.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Analysis results not found for user {user_id}")
            
        results = self.load_results(file_path)
        
        if results["status"] != "success":
            raise ValueError(f"Analysis failed for user {user_id}: {results.get('error_message', 'Unknown error')}")
            
        health_risks = results["health_risks"]
        
        # Create radar chart figure
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        
        # Extract risk types and levels
        risk_types = list(health_risks["risks"].keys())
        risk_levels = [health_risks["risks"][rt]["risk_level"] for rt in risk_types]
        
        # Number of variables
        N = len(risk_types)
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add the risk levels for the plot
        risk_levels += risk_levels[:1]  # Close the loop
        
        # Draw one axis per variable and add labels
        plt.xticks(angles[:-1], [rt.capitalize() for rt in risk_types], size=12)
        
        # Draw risk level axis
        ax.set_rlabel_position(0)
        plt.yticks([0.2, 0.4, 0.6, 0.8], ["Low", "Moderate", "High", "Very High"], 
                   color="grey", size=10)
        plt.ylim(0, 1)
        
        # Plot data
        ax.plot(angles, risk_levels, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, risk_levels, alpha=0.25, color='#1f77b4')
        
        # Add title
        plt.title(f"Health Risk Assessment for User {user_id}", size=15, pad=20)
        
        # Create separate figures for each risk type showing factor contributions
        factor_figs = []
        
        for risk_type in risk_types:
            # Create figure for this risk type
            fig_rt, ax_rt = plt.subplots(figsize=(10, 6))
            
            # Extract factor data
            risk_data = health_risks["risks"][risk_type]
            factors = risk_data["factors"]
            
            # Sort factors by value
            factor_items = sorted(factors.items(), key=lambda x: x[1], reverse=True)
            factor_names = [item[0].capitalize() for item in factor_items]
            factor_values = [item[1] for item in factor_items]
            
            # Create bar chart
            bars = ax_rt.bar(factor_names, factor_values, width=0.6, 
                          color=plt.cm.YlOrRd(np.array(factor_values) / max(factor_values)))
            
            # Add risk level text
            risk_level = risk_data["risk_level"]
            risk_category = risk_data["category"]
            
            ax_rt.text(0.5, 0.95, f"Overall Risk: {risk_category} ({risk_level:.2f})", 
                    transform=ax_rt.transAxes, ha='center', fontsize=14, 
                    fontweight='bold', bbox=dict(facecolor='white', alpha=0.5))
            
            # Add labels
            for bar in bars:
                height = bar.get_height()
                ax_rt.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            # Set labels and title
            ax_rt.set_ylabel("Risk Factor Contribution")
            ax_rt.set_title(f"{risk_type.capitalize()} Risk Factors for User {user_id}")
            
            # Adjust x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Adjust layout
            fig_rt.tight_layout()
            
            # Save figure if requested
            if save_fig:
                fig_rt.savefig(os.path.join(self.output_dir, f"{user_id}_{risk_type}_risk.png"), dpi=300)
            
            factor_figs.append(fig_rt)
        
        # Adjust layout
        fig.tight_layout()
        
        # Save figure if requested
        if save_fig:
            fig.savefig(os.path.join(self.output_dir, f"{user_id}_health_risks.png"), dpi=300)
        
        return fig, factor_figs
    
    def visualize_scenario_comparison(self, user_id: str, scenarios: List[str], 
                                    save_fig: bool = True) -> plt.Figure:
        """
        Create a visualization comparing different intervention scenarios.
        
        Args:
            user_id: ID of the user to visualize
            scenarios: List of scenario names to compare
            save_fig: Whether to save the figure to a file
            
        Returns:
            Matplotlib Figure object
        """
        # Load baseline results
        baseline_path = os.path.join(self.results_dir, f"{user_id}_analysis.json")
        if not os.path.exists(baseline_path):
            raise FileNotFoundError(f"Baseline analysis results not found for user {user_id}")
        
        baseline = self.load_results(baseline_path)
        
        if baseline["status"] != "success":
            raise ValueError(f"Baseline analysis failed for user {user_id}")
        
        # Load scenario results
        scenario_results = []
        for scenario in scenarios:
            scenario_path = os.path.join(self.results_dir, f"{user_id}_scenario_{scenario}_analysis.json")
            if not os.path.exists(scenario_path):
                print(f"Warning: Scenario '{scenario}' results not found, skipping")
                continue
                
            results = self.load_results(scenario_path)
            
            if results["status"] != "success":
                print(f"Warning: Scenario '{scenario}' analysis failed, skipping")
                continue
                
            scenario_results.append((scenario, results))
        
        if not scenario_results:
            raise ValueError("No valid scenario results found")
        
        # Create figure for life expectancy comparison
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        scenario_names = ["Baseline"] + [s[0].replace("_", " ").title() for s in scenario_results]
        life_expectancies = [baseline["life_expectancy"]["predicted_life_expectancy"]]
        life_expectancies += [r[1]["life_expectancy"]["predicted_life_expectancy"] for r in scenario_results]
        
        # Create bar chart
        bars = ax1.bar(scenario_names, life_expectancies, width=0.6, 
                     color=plt.cm.viridis(np.linspace(0, 0.8, len(scenario_names))))
        
        # Add data labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            diff = height - life_expectancies[0] if i > 0 else 0
            
            if i == 0:
                ax1.text(i, height + 0.5, f"{height:.1f}", ha='center', fontweight='bold')
            else:
                if diff > 0:
                    ax1.text(i, height + 0.5, f"{height:.1f} (+{diff:.1f})", ha='center', fontweight='bold')
                else:
                    ax1.text(i, height + 0.5, f"{height:.1f} ({diff:.1f})", ha='center', fontweight='bold')
        
        # Set labels and title
        ax1.set_ylabel("Predicted Life Expectancy (years)")
        ax1.set_title(f"Life Expectancy Comparison for Different Scenarios - User {user_id}")
        
        # Add grid
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Adjust layout
        fig1.tight_layout()
        
        # Create figure for biological age comparison
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        bio_ages = [baseline["biological_age"]["biological_age"]]
        bio_ages += [r[1]["biological_age"]["biological_age"] for r in scenario_results]
        
        chrono_age = baseline["biological_age"]["chronological_age"]
        
        # Create bar chart
        bars = ax2.bar(scenario_names, bio_ages, width=0.6, 
                     color=plt.cm.viridis(np.linspace(0, 0.8, len(scenario_names))))
        
        # Add chronological age reference line
        ax2.axhline(y=chrono_age, color='red', linestyle='--', alpha=0.7, 
                   label=f"Chronological Age: {chrono_age}")
        
        # Add data labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            diff = bio_ages[0] - height if i > 0 else 0
            age_diff = chrono_age - height
            
            if i == 0:
                if age_diff > 0:
                    ax2.text(i, height + 0.5, f"{height:.1f} ({age_diff:.1f})", ha='center', fontweight='bold')
                else:
                    ax2.text(i, height + 0.5, f"{height:.1f} (+{abs(age_diff):.1f})", ha='center', fontweight='bold')
            else:
                if diff > 0:
                    ax2.text(i, height + 0.5, f"{height:.1f} (-{diff:.1f})", ha='center', fontweight='bold')
                else:
                    ax2.text(i, height + 0.5, f"{height:.1f} (+{abs(diff):.1f})", ha='center', fontweight='bold')
        
        # Set labels and title
        ax2.set_ylabel("Biological Age (years)")
        ax2.set_title(f"Biological Age Comparison for Different Scenarios - User {user_id}")
        
        # Add legend
        ax2.legend()
        
        # Add grid
        ax2.grid(True, axis='y', alpha=0.3)
        
        # Adjust layout
        fig2.tight_layout()
        
        # Create figure for risk comparison
        fig3, ax3 = plt.subplots(figsize=(14, 8))
        
        # Prepare data
        risk_types = list(baseline["health_risks"]["risks"].keys())
        
        scenario_labels = ["Baseline"] + [s[0].replace("_", " ").title() for s in scenario_results]
        x = np.arange(len(risk_types))
        width = 0.8 / len(scenario_labels)
        
        # Plot bars for each scenario
        for i, label in enumerate(scenario_labels):
            if i == 0:
                risk_levels = [baseline["health_risks"]["risks"][rt]["risk_level"] for rt in risk_types]
            else:
                risk_levels = [scenario_results[i-1][1]["health_risks"]["risks"][rt]["risk_level"] for rt in risk_types]
            
            offset = width * i - width * len(scenario_labels) / 2 + width / 2
            bars = ax3.bar(x + offset, risk_levels, width, label=label,
                         color=plt.cm.viridis(i / len(scenario_labels)))
        
        # Set labels and title
        ax3.set_ylabel("Risk Level")
        ax3.set_title(f"Health Risk Comparison for Different Scenarios - User {user_id}")
        ax3.set_xticks(x)
        ax3.set_xticklabels([rt.capitalize() for rt in risk_types])
        ax3.legend()
        
        # Add grid
        ax3.grid(True, axis='y', alpha=0.3)
        
        # Adjust layout
        fig3.tight_layout()
        
        # Save figures if requested
        if save_fig:
            fig1.savefig(os.path.join(self.output_dir, f"{user_id}_scenario_life_expectancy.png"), dpi=300)
            fig2.savefig(os.path.join(self.output_dir, f"{user_id}_scenario_biological_age.png"), dpi=300)
            fig3.savefig(os.path.join(self.output_dir, f"{user_id}_scenario_health_risks.png"), dpi=300)
        
        return fig1, fig2, fig3

    def generate_comprehensive_report(self, user_id: str, scenario: Optional[str] = None) -> None:
        """
        Generate a comprehensive visual report for a user.
        
        Args:
            user_id: ID of the user to generate report for
            scenario: Optional scenario to include in the report
        """
        print(f"Generating comprehensive report for user {user_id}...")
        
        # Create base visualizations
        print("Generating life expectancy visualization...")
        self.visualize_life_expectancy(user_id)
        
        print("Generating biological age visualization...")
        self.visualize_biological_age(user_id)
        
        print("Generating health risks visualization...")
        self.visualize_health_risks(user_id)
        
        # Add scenario comparison if requested
        if scenario:
            print(f"Generating scenario comparison for '{scenario}'...")
            self.visualize_scenario_comparison(user_id, [scenario])
        
        print(f"Report generation complete. Visualizations saved to {self.output_dir}")


def main():
    """Main function for visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize AI Life Management System simulation results")
    
    parser.add_argument("--user-id", type=str, required=True, help="User ID to visualize")
    parser.add_argument("--result-dir", type=str, help="Directory containing simulation results")
    parser.add_argument("--output-dir", type=str, help="Directory to save visualizations")
    parser.add_argument("--scenario", type=str, help="Scenario to visualize")
    parser.add_argument("--compare-scenarios", nargs='+', help="List of scenarios to compare")
    
    args = parser.parse_args()
    
    # Initialize visualizer
    visualizer = ResultsVisualizer(args.result_dir)
    
    if args.output_dir:
        visualizer.output_dir = args.output_dir
        os.makedirs(visualizer.output_dir, exist_ok=True)
    
    # Generate visualizations
    if args.compare_scenarios:
        print(f"Comparing scenarios: {', '.join(args.compare_scenarios)}")
        visualizer.visualize_scenario_comparison(args.user_id, args.compare_scenarios)
    elif args.scenario:
        print(f"Generating comprehensive report with scenario '{args.scenario}'...")
        visualizer.generate_comprehensive_report(args.user_id, args.scenario)
    else:
        print("Generating comprehensive report...")
        visualizer.generate_comprehensive_report(args.user_id)
    
    print("Visualization complete!")


if __name__ == "__main__":
    main()
