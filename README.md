# Insurity-Telematics-Project
Telematics-based auto insurance prototype with simulated driving data, feature extraction, and risk scoring.

## Project Overview

This project demonstrates how telematics technology can be integrated into auto insurance to enable usage-based insurance (UBI) models like Pay-As-You-Drive (PAYD) and Pay-How-You-Drive (PHYD), offering fairer and more personalized premium calculations.

### Key Features

- **Realistic Telematics Simulation**: Generates GPS, speed, acceleration, and braking data
- **Comprehensive Feature Extraction**: Extracts 50+ driving behavior features
- **Data Quality Validation**: Ensures data integrity and identifies issues
- **Risk Scoring**: Calculates composite risk scores based on driving behavior
- **Scalable Architecture**: Designed for production deployment

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telematics    │    │   Feature        │    │   Risk Scoring  │
│   Simulator     │───▶│   Extraction     │───▶│   & Pricing     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Raw Data      │    │   Processed      │    │   Insurance     │
│   (CSV/JSON)    │    │   Features       │    │   Premiums      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Project Structure

```
├── src/                    # Source code
│   ├── telematics_simulator.py    # Data simulation engine
│   ├── feature_extraction.py      # Feature extraction pipeline
│   └── data_validation.py         # Data quality validation
├── models/                 # AI models and weights
├── docs/                   # Documentation and research notes
├── bin/                    # Executable scripts
│   ├── run_sim.sh         # Run telematics simulation
│   ├── extract_features.sh # Run feature extraction
│   └── run_demo.sh        # Complete demo pipeline
├── data/                   # Sample data and outputs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```



## Risk Score Modeling 
```
                ┌───────────────┐
                │   Input Data  │
                │  (X features) │
                └───────┬───────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │ Preprocessing Step      │
            │ - OneHotEncode vehicle  │
            │   type (for sklearn)    │
            │ - Pass numeric features │
            └─────────┬───────────────┘
                      │
                      ▼
       ┌───────────────┬───────────────┬───────────────┐
       │               │               │               │
       ▼               ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ RandomForest│ │ XGBoost     │ │ Gradient    │ │ CatBoost    │
│ Regressor   │ │ Regressor   │ │ Boosting    │ │ Regressor   │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │ Base Model Predictions  │
          │ (predictions from RF,   │
          │  XGBoost, GradientBoost,│
          │  CatBoost)              │
          └─────────┬───────────────┘
                    │
                    ▼
          ┌─────────────────────────┐
          │ Final Estimator: Ridge  │
          │ Regression combines     │
          │ base predictions        │
          └─────────┬───────────────┘
                    │
                    ▼
               ┌───────────────┐
               │ Final Output  │
               │ Predicted     │
               │ enhanced_risk │
               │ score (ŷ)     │
               └───────────────┘
```

## Combined Model
```
┌───────────────────────────────┐
│         Raw Driver Data       │
│  - Trip counts                │
│  - Average & total miles      │
│  - Average speed              │
│  - Harsh braking/acceleration │
│  - Night driving %            │
│  - Vehicle type & age         │
│  - Prior claims / violations  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Data Preparation        │
│  - Feature selection          │
│      * Keep behavior/risk vars│
│      * Remove non-predictive  |
│         IDs                   |
│  - Target: enhanced_risk_score│
│  - Identify categorical vs    │
│    numeric                    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Preprocessing          │
│  - Convert categorical →      │
│    numeric                    │
│      * One-hot encoding (RF,  │
│        XGB, GB)               │
│      * CatBoost handles       │
│        categories natively    │
│  - Numeric features: passed   │
│    as-is                      │
│  - Aim:                       │
│      avoid data leakage &     │
│      ensure model interprets  │
│      inputs correctly         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           Modeling            │
│  - CatBoost                   │
│  - RandomForest               │
│  - XGBoost                    │
│  - GradientBoosting (sklearn) │
│  - Stacking Ensemble          │
│      * Combines RF, XGB, GB   │
│      * Linear model as final  │
│        estimator              │
│  - Goal:                      │
│      reduce bias/variance &   │
│      maximize predictive      │
│      accuracy                 │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Cross-Validation & Evaluation │
│  - 5-fold CV for robust       │
│    performance                │
│  - Metrics: MAE, RMSE, R²     │
│  - Findings: Stacking Ensemble│
│    best                       │
│  - Ensures generalization &   │
│    avoids overfitting         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Hold-Out Test Evaluation    │
│  - Train models on full train │
│    set                        │
│  - Evaluate on unseen test set│
│  - Stacking Ensemble confirms │
│    high performance(R² ~ 0.95)│
│  - Validates reliability for  │
│    real-world predictions     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Risk Score Prediction   │
│  - Output: enhanced_risk_score│
│    (numeric)                  │
│  - Interpretation:            │
│      * High score → higher    │
│        likelihood of claims   │
│      * Low score → safer      │
│        driver, lower premium  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│     Premium Calculation       │
│  1. Normalize risk:           │
│      normalized_risk =        │
│      predicted_risk_score /   │
│      max_risk_score           │
│  2. Scaling factor:           │
│      scaling_factor = 1 +     │
│      0.5 * normalized_risk    │
│  3. Annual premium:           │
│      premium_annual = base_   │
│      premium * scaling_factor │
│  4. Monthly premium:          │
│      premium_monthly =        │
│      premium_annual / 12      │
│  - Base premium anchored in   │
│    industry average           │
│  - Ensures premiums           │
│    proportional to ri         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           Outputs             │
│  - Predicted risk score       │
│  - Annual premium             │
│  - Monthly premium            │
│                               │
│  Business Impact:             │
│  - Fair, data-driven pricing  │
│  - Rewards safe driving       │
│  - Penalizes risky behavior   │
│  - Transparent & interpretable│
└───────────────────────────────┘
```
