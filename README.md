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



## Modeling 
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
