## Live Demo

https://nfl-analytics-zeta.vercel.app

# NFL Analytics & Game Prediction Platform

A full-stack NFL analytics application that uses historical
play-by-play data and machine learning to predict NFL game outcomes.

## Features

- NFL schedule browsing by season and week
- Machine-learning win probabilities
- Logistic Regression prediction model
- Elo ratings
- Offensive and defensive efficiency metrics
- EPA-based statistics
- Recent team form
- Rest and bye-week features
- 2026 early-season fallback using prior-season data
- React frontend
- FastAPI backend

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Polars
- nflreadpy

### Machine Learning
- scikit-learn
- Logistic Regression
- Random Forest
- XGBoost
- Voting Ensemble

## Model Evaluation

Rolling out-of-sample evaluation was performed across the
2023, 2024, and 2025 NFL seasons.

Best 2025 Logistic Regression accuracy:

63.1%

## Architecture

React
→ FastAPI
→ NFL data / feature engineering
→ saved ML model
→ prediction response

## Run Locally

Backend:

```bash
uvicorn api:app --reload