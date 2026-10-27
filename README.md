# SuperKart Sales Forecasting

Flask API backend + Streamlit frontend, each in its own Docker container, connected through a Docker network.

- `backend_files/` – Flask REST API (`/v1/predict`, `/v1/predictbatch`) serving the trained model on port 7860
- `frontend_files/` – Streamlit UI on port 8501

## Run in GitHub Codespaces
```bash
cd backend_files && docker build -t superkart-backend .
cd ../frontend_files && docker build -t superkart-frontend .
docker network create superkart-network
docker run -d --name backend --network superkart-network -p 7860:7860 superkart-backend
docker run -d --name frontend --network superkart-network -p 8501:8501 superkart-frontend
```
Set ports 7860 and 8501 to **Public** in the Ports tab.
