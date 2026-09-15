# Product Recommendation System

## Overview

This project is a Machine Learning-based Product Recommendation System developed using product ratings, feature engineering, and clustering techniques. The project analyzes product ratings and creates product clusters. It also provides text-based and image-based product search through an interactive Streamlit application.

## 🚀 Live Demo

[Click here to try the Product Recommendation System](https://appuct-recommendation-system-5pzsamwv2fdm3kjrn4ojgm.streamlit.app/)

## Features

- Product rating analysis
- Exploratory Data Analysis (EDA)
- Product feature engineering
- K-Means clustering
- Hierarchical clustering
- DBSCAN clustering
- Text-based product search
- Image-based product search
- Product price, rating, and review details
- Product images
- Direct purchase links
- Interactive Streamlit web application

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- SerpApi
- Pillow
- Matplotlib
- Seaborn

## Machine Learning Models Used

| Model | Score | Purpose |
|---|---:|---|
| K-Means | 0.648 | Product clustering |
| Hierarchical Clustering | 0.657 | Product clustering |
| DBSCAN | 0.934 | Product clustering |

## Model Selection

K-Means clustering was selected for the final recommendation system because it provides practical and interpretable product groups based on product ratings and rating counts.

## Project Workflow

- Data Loading
- Data Cleaning
- Exploratory Data Analysis (EDA)
- Feature Engineering
- Product Feature Creation
- Clustering
- Model Comparison
- Product Search Integration
- Streamlit Deployment

## Application

The Streamlit application allows users to:

- Search for products using text
- Upload a product image
- Find visually similar products
- View product images
- View product prices
- View ratings and reviews
- Visit product purchase links

## Project Files

- `app.py` – Streamlit application
- `Product Recommendation System.ipynb` – Machine learning and data analysis
- `rating_short.csv` – Product rating dataset
- `product_features.csv` – Processed product features
- `requirements.txt` – Required Python libraries
- `.gitignore` – Files excluded from GitHub

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/GayatriWarude/Product-Recommendation-System
