import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask app
superkart_api = Flask("SuperKart Sales Forecaster")

# Load the trained pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in this order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health-check route."""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: predict sales for a single product-store record sent as JSON."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    sample = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = model.predict(sample)[0]

    return jsonify({"Predicted_Sales": round(float(prediction), 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: predict sales for every row of an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file using the key 'file'"}), 400

    batch = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in batch.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(batch[FEATURES])

    # Row index -> predicted sales
    result = {str(i): round(float(p), 2) for i, p in zip(batch.index, predictions)}
    return jsonify(result)


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
