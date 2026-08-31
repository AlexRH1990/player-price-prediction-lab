cat << 'EOF' > README.md
# ⚽ ML Scout: Performance-Adjusted Player Valuation

![ML Scout Interface](assets/App.jpg)

> "Trabajaremos con un dataset alojado en un bucket, este será traido de Kaggle directamente alojado en el bucket. El objetivo es realizar un análisis exploratorio de los datos del dataset (datos de rendimiento y de partidos de jugadores de futbol), para generar mediante regresiones lineales un algoritmo que prediga el precio de un jugador según sus números..."

*(Architectural Note: While the project's original premise explored linear regressions, the final solution implements an **XGBoost** engine to highly capture non-linear relationships and market anomalies in player valuations).*

---

## 🚀 Project Overview

**ML Scout** is an end-to-end, data-driven web application designed to detect financial inefficiencies in the football (soccer) transfer market. It empowers scouts and analysts to value players strictly based on their on-pitch performance (minutes played, goals, assists, and position), cutting through media hype and subjective biases. 

By feeding player statistics into a trained Machine Learning model, the application calculates a **Fair Market Value** in real-time.

---

## 🧠 Architecture & Technical Deep Dive

This project was built with a strong emphasis on separation of concerns, secure cloud processing, and scalable machine learning operations (MLOps).

### 1. Data Engineering & Cloud Pipeline (AWS S3)
To ensure environment security and avoid local storage constraints, the data pipeline was designed for cloud-native execution:
* **Direct Ingestion:** Data is fetched directly via the Kaggle API and stored securely in an **AWS S3 Bucket**.
* **In-Memory Processing:** Using `Boto3` and Pandas' `io.BytesIO`, the ETL pipeline streams gigabytes of CSV data directly into RAM. This strictly avoids downloading sensitive or massive datasets to the local disk of the compute instance.

### 2. Machine Learning Engine (XGBoost)
The exploratory data analysis (EDA) revealed that player market values do not scale linearly (e.g., the value of an elite striker with 20 goals scales exponentially compared to an average striker, while established defenders hold a strong baseline value regardless of offensive output).
* **The Pivot:** We upgraded from baseline Linear Regression to **XGBoost (Gradient Boosting)**. This tree-based ensemble method perfectly captures these complex, non-linear market dynamics and feature interactions.
* **Model Serialization:** The trained model and its one-hot encoded feature mappings are exported using `joblib`, decoupling the training environment from the production API.

### 3. Robust Backend API (FastAPI)
The backend acts as a secure bridge between the user and the ML model:
* **High-Performance Framework:** Built on **FastAPI** running on a Uvicorn ASGI server for maximum asynchronous performance.
* **Strict Data Validation:** Implemented Data Transfer Objects (DTOs) using **Pydantic**. This ensures the ML model only receives strictly typed and validated data, preventing injection attacks or processing errors.
* **CORS & Static Unification:** Configured FastAPI's `StaticFiles` to serve the frontend directly from the root path, elegantly bypassing CORS issues and unifying the deployment.

### 4. Asynchronous Frontend UI
* **Design System:** A sleek, "Dark Mode" analytical dashboard built with **Tailwind CSS** via CDN to maintain a zero-build-step frontend while ensuring a professional UX.
* **DOM Manipulation:** Vanilla asynchronous JavaScript interacts with the FastAPI endpoints via the **Fetch API**, handling loading states and dynamic DOM updates without page reloads.

---

## ⚙️ Local Execution Guide

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AlexRH1990/player-price-prediction-lab.git](https://github.com/AlexRH1990/player-price-prediction-lab.git)
   cd player-price-prediction-lab
