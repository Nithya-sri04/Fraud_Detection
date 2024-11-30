import joblib
import pandas as pd
from fraud.fraud import Fraud
from flask import Flask, request, Response, jsonify

# Loading the model
model = joblib.load('./models/model_cycle1.joblib')
print(model.feature_names_in_) 

# Initialize the Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Fraud Detection API!"

@app.route('/fraud/predict', methods=['POST'])
def fraud_predict():
    try:
        test_json = request.get_json()  # Get the JSON data from the request
        
        if test_json:  # Check if there is data in the request
            if isinstance(test_json, dict):  # Unique example
                test_raw = pd.DataFrame(test_json, index=[0])
            else:  # Multiple examples
                test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())
            
            # Instantiate the Fraud class
            pipeline = Fraud()
            
            # Data cleaning
            df1 = pipeline.data_cleaning(test_raw)
            
            # Feature engineering
            df2 = pipeline.feature_engineering(df1)
            
            # Data preparation
            df3 = pipeline.data_preparation(df2)
            
            # Get predictions
            df_response = pipeline.get_prediction(model, test_raw, df3)
            
            # Return the response in JSON format
            return Response(df_response, status=200, mimetype='application/json')
        
        else:
            # Return an error message if no data is provided
            return jsonify({"error": "No data provided"}), 400
            
    except Exception as e:
        # Handle any errors that occur during prediction
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred during prediction", "message": str(e)}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)  # Running the Flask app on port 5000
