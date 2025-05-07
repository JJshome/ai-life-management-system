# AI Life Management System Simulation

This directory contains the simulation components for the AI-based Life Management and Aging Preparation Decision System. The simulation allows you to generate synthetic user data, analyze it using the system's AI models, and evaluate the effectiveness of various lifestyle intervention scenarios.

## Features

- Generate realistic synthetic user profiles with health metrics, lifestyle data, genetic information, and biosensor readings
- Predict life expectancy and biological age based on comprehensive data analysis
- Calculate health risk factors across multiple domains (cardiovascular, metabolic, neurological, cancer)
- Generate personalized recommendations for health optimization
- Simulate various intervention scenarios to see their impact on predicted outcomes
- Generate summary reports for cohort analysis

## How to Use

### Basic Usage

```bash
# Run a simulation for a single user
python -m simulation.run_simulation

# Run simulations for multiple users
python -m simulation.run_simulation --users 10

# Run a scenario simulation for a specific user
python -m simulation.run_simulation --user-id user_0001 --scenario improved_diet
```

### Command Line Arguments

- `--users`: Number of users to simulate (default: 1)
- `--user-id`: Specific user ID to use (generates random ID if not provided)
- `--scenario`: Scenario to simulate (options: improved_diet, exercise_program, stress_reduction, sleep_optimization, quit_smoking, optimal_lifestyle)
- `--seed`: Random seed for reproducibility
- `--output-dir`: Directory to save results (default: simulation/results)

### Available Scenarios

1. **improved_diet**: Simulates the effect of adopting a Mediterranean diet, increasing fruit and vegetable intake, and reducing processed food consumption
2. **exercise_program**: Simulates the effect of increasing physical activity, adding more diverse exercise types, and achieving fitness improvements
3. **stress_reduction**: Simulates the effect of implementing stress management practices and reducing stress levels
4. **sleep_optimization**: Simulates the effect of optimizing sleep duration and quality
5. **quit_smoking**: Simulates the effect of quitting smoking (only applies to current smokers)
6. **optimal_lifestyle**: Combines all positive interventions for maximum health optimization

## Directory Structure

- `data_generator.py`: Generates synthetic user data
- `predictor.py`: Implements the AI-based prediction and recommendation algorithms
- `run_simulation.py`: Main simulation runner script
- `data/`: Directory for storing generated data
- `results/`: Directory for storing analysis results

## Output Files

The simulation produces the following output files in the `results/` directory:

- `user_XXXX_data.json`: Raw user data for user XXXX
- `user_XXXX_analysis.json`: Analysis results for user XXXX
- `user_XXXX_scenario_YYYY_analysis.json`: Analysis results for user XXXX under scenario YYYY
- `simulation_summary.json`: Summary report for multi-user simulations

## Example: Comparing Intervention Scenarios

To evaluate the potential impact of different lifestyle interventions:

```bash
# Generate a user
python -m simulation.run_simulation --user-id test_user

# Run different scenarios
python -m simulation.run_simulation --user-id test_user --scenario improved_diet
python -m simulation.run_simulation --user-id test_user --scenario exercise_program
python -m simulation.run_simulation --user-id test_user --scenario stress_reduction
python -m simulation.run_simulation --user-id test_user --scenario optimal_lifestyle

# Compare the results in the generated JSON files
```

## Technical Implementation

The simulation is based on patented technology by Ucaretron Inc., including:

- Frequency-scanning impedance technology from ear-insert biosensors
- Advanced AI algorithms for predictive analysis
- Comprehensive data integration from multiple sources
- Personalized intervention modeling

Note: This simulation demonstrates the core concepts of the technology but uses synthetic data for demonstration purposes.
