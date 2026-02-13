# eBay Intelligent Search Refinement Engine
A full-stack application that enhances eBay search results using a human-in-the-loop filtering workflow powered by TF-IDF vectorisation and cosine similarity.
Users fetch a large batch of listings, review a random sample, mark unwanted items, and the system automatically filters the remaining listings based on learned title similarity.


## Overview

eBay searches often return noisy or loosely related results.  
This project introduces a structured refinement pipeline:

1. Retrieve batched listings from the eBay Browse API.
2. Randomly sample a subset for user review.
3. Learn user preferences from accepted vs rejected listings.
4. Classify unseen listings using cosine similarity.

The system combines:
- External API integration (OAuth2)
- Data cleaning pipelines
- NLP-based feature engineering
- Vector space modelling
- Full-stack integration (FastAPI + Next.js)


# Tech Stack

## Backend
- FastAPI
- Pandas
- NumPy
- scikit-learn
- Requests
- python-dotenv

## Frontend
- Next.js (React + TypeScript)
- Tailwind CSS

## External API
- eBay Browse API
- OAuth2 Client Credentials Flow
- Marketplace: EBAY_GB
- Fixed-price listings only
---


## Backend Setup

Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows (PowerShell): .\venv\Scripts\Activate


