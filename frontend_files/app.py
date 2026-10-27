import os
import requests
import pandas as pd
import streamlit as st

# Backend URL: inside the Docker network the Flask container is reachable as "backend"
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")
REFERENCE_YEAR = 2025  # same reference year used to compute Store_Age_Years during training

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("SuperKart Sales Forecasting App")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

# ---------------- Online prediction ----------------
st.subheader("Single Prediction")

col1, col2 = st.columns(2)
with col1:
    product_id_char = st.selectbox(
        "Product Family", ["FD", "NC", "DR"],
        help="FD = Food, NC = Non-Consumable, DR = Drinks",
    )
    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)

with col2:
    product_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
    store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    store_year = st.number_input("Store Establishment Year", min_value=1950, max_value=REFERENCE_YEAR, value=2009, step=1)

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar,
    "Product_Allocated_Area": product_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_city,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": int(REFERENCE_YEAR - store_year),
    "Product_Type_Category": product_category,
}

if st.button("Predict"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
        if response.status_code == 200:
            sales = response.json()["Predicted_Sales"]
            st.success(f"Predicted Product-Store Sales Total: {sales:,.2f}")
        else:
            st.error(f"Error from API ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend API: {e}")

# ---------------- Batch prediction ----------------
st.subheader("Batch Prediction")
st.write(
    "Upload a CSV with the columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, "
    "Product_MRP, Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, "
    "Store_Age_Years, Product_Type_Category"
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.dataframe(batch_df.head())

    if st.button("Predict for Batch"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")},
                timeout=60,
            )
            if response.status_code == 200:
                preds = response.json()
                batch_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(batch_df))]
                st.success("Predictions completed successfully!")
                st.dataframe(batch_df)
                st.download_button(
                    "Download predictions as CSV",
                    batch_df.to_csv(index=False).encode("utf-8"),
                    file_name="superkart_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"Error from API ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend API: {e}")
