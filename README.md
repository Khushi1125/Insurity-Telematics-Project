# Telematics Risk Scoring and Premium Pricing

This project builds a telematics-based risk scoring model and premium pricing system. It processes trip data (e.g., harsh braking, acceleration, speed, night trips, claims, and vehicle type) to generate a risk score (0–100) and estimate insurance premium costs. The results are visualized in interactive Streamlit dashboards.

---
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


## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Khushi1125/Insurity-Telematics-Project.git
   cd Insurity-Telematics-Project
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   
   venv\Scripts\activate     
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Dashboards

1. Navigate into the dashboard folder:
   ```bash
   cd dashboard
   ```

2. Run the desired dashboard file:
   ```bash
   python3 -m streamlit run "file_name.py"
   ```

   Example:
   ```bash
   python3 -m streamlit run "Admin.py"
   ```

3. Open the provided local URL in your browser to interact with the dashboard.

---

## Evaluation Process

# Combined model structure 
```
                ┌───────────────────────────┐
                │       Raw Driver Data     │
                │ Trips, miles, speed       │
                │ Harsh events, night %     │
                │ Vehicle type, claims      │
                └───────────────┬───────────┘
                                │
                                ▼
         ┌──────────────────────┴──────────────────────┐
         │                                             │
┌───────────────────────────┐             ┌───────────────────────────┐
│     Data Preparation      │             │       Preprocessing       │
│ - Select risk features    │             │ - Encode categories       │
│ - Drop IDs                │             │ - Numeric passthrough     │
│ - Target: risk score      │             │ - Prevent leakage         │
└───────────────┬───────────┘             └───────────────┬───────────┘
                │                                         │
                └────────────────────┬────────────────────┘
                                     ▼
                         ┌───────────────────────────┐
                         │         Modeling          │
                         │ CatBoost, RF, XGB, GB     │
                         │ Stacking Ensemble (final) │
                         └───────────────┬───────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
      ┌───────────────────────────┐               ┌───────────────────────────┐
      │ Cross-Validation (5-fold) │               │   Hold-Out Test Results   │
      │ MAE, RMSE, R²             │               │ R² ≈ 0.95 (Stacking best) │
      │ Confirms generalization   │               │ Confirms reliability      │
      └───────────────┬───────────┘               └───────────────┬───────────┘
                      │                                           │
                      └──────────────────────┬────────────────────┘
                                             ▼
                               ┌───────────────────────────┐
                               │   Risk Score Prediction   │
                               │ Numeric score → High/Low  │
                               │ Links to premium pricing  │
                               └───────────────┬───────────┘
                                               │
                                               ▼
                               ┌───────────────────────────┐
                               │   Premium Calculation     │
                               │ Normalize → Scale (+50%)  │
                               │ Annual = base * factor    │
                               │ Monthly = annual / 12     │
                               └───────────────┬───────────┘
                                               │
                                               ▼
                               ┌───────────────────────────┐
                               │          Outputs          │
                               │ Risk score + premiums     │
                               │ Business impact: fair,    │
                               │ data-driven pricing       │
                               └───────────────────────────┘
```

# The project uses three main components:

1. **Enhanced Risk Score Formula**
   - Factors: harsh braking, harsh acceleration, speeding, night driving, claims history, and vehicle type.  
   - Each factor is normalized to 0–1 and weighted according to its impact on accident likelihood.  
   - Vehicle type adds fixed points, normalized to align with other features.  
   - Final risk score is bounded between 0–100.

2. **Claims Weighted Score**
   - Accounts for past claims by type and severity.  
   - Weighted more heavily than other features because claims history is the strongest predictor of future risk.

3. **Premium Cost Formula**
   - Base premium reflects current industry pricing.  
   - Risk score acts as a multiplier to adjust premiums fairly.  
   - Example: Safer drivers pay closer to the base, higher-risk drivers pay proportionally more.  

Together, these formulas ensure a fair, data-driven pricing structure that balances safety incentives with actuarial soundness.



