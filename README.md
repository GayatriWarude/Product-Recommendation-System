# Product Recommendation System

## Overview

A machine learning-based product recommendation system built with Python and Streamlit. The project analyzes product ratings and product features using clustering techniques and provides an interactive product search experience.

The Streamlit application allows users to search for products using **text or an uploaded product image** and displays relevant product results with details such as price, rating, reviews, images, and purchase links.

## Features

- Exploratory Data Analysis (EDA)
- Product feature engineering
- Product rating analysis
- K-Means clustering
- Hierarchical clustering
- DBSCAN clustering
- Text-based product search
- Image-based product search
- Interactive Streamlit interface
- Product images, prices, ratings, reviews, and purchase links

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Streamlit
- SerpApi

## Project Files

- `Product Recommendation System.ipynb` – EDA, feature engineering, clustering, and model analysis
- `app.py` – Streamlit application
- `product_features.csv` – Processed product features and clustering results
- `rating_short.csv` – Product rating dataset

## How to Run

1. Clone this repository.
2. Install the required Python libraries.
3. Add your SerpApi key to Streamlit secrets.
4. Run the application:

```bash
streamlit run app.py
