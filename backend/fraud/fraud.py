import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  

class Fraud:
    def __init__(self):
        # Load the trained models
        self.minmaxscaler = joblib.load('./parameters/minmaxscaler_cycle1.joblib')
        self.onehotencoder = joblib.load('./parameters/onehotencoder_cycle1.joblib')
        
        # Column name mapping for consistency
        self.column_mapping = {
            'newbalanceOrig': 'new_balance_orig',
            'oldbalanceOrg': 'old_balance_org',
            'nameOrig': 'name_orig',
            'nameDest': 'name_dest',
            'newbalanceDest': 'new_balance_dest',
            'oldbalanceDest': 'old_balance_dest'
        }

    def data_cleaning(self, df1):
        # Rename the columns using the mapping for consistency
        df1 = df1.rename(columns=self.column_mapping)
        
        # Debugging: Print the columns after renaming
        print("Columns after renaming:", df1.columns)
        return df1

    def feature_engineering(self, df2):
        # Ensure all required columns are present
        required_columns = [
            'new_balance_orig', 'old_balance_org', 'new_balance_dest', 
            'old_balance_dest', 'name_orig', 'name_dest'
        ]
        for col in required_columns:
            if col not in df2.columns:
                df2[col] = 0  # Assign default value for missing columns

        # Feature engineering transformations
        df2['diff_new_old_balance'] = df2['new_balance_orig'] - df2['old_balance_org']
        df2['diff_new_old_destiny'] = df2['new_balance_dest'] - df2['old_balance_dest']
        df2['name_orig'] = df2['name_orig'].apply(lambda i: i[0] if isinstance(i, str) else '')
        df2['name_dest'] = df2['name_dest'].apply(lambda i: i[0] if isinstance(i, str) else '')

        # Drop unnecessary columns if they exist
        df2 = df2.drop(columns=['step_weeks', 'step_days'], axis=1, errors='ignore')

        # Debugging: Print the columns after feature engineering
        print("Data after feature engineering:", df2.columns)
        return df2

    def data_preparation(self, df3):
        # Apply OneHotEncoder transformation
        df3 = self.onehotencoder.transform(df3)
        
        # Rescaling numerical features
        num_columns = ['amount', 'old_balance_org', 'new_balance_orig', 
                    'old_balance_dest', 'new_balance_dest', 
                    'diff_new_old_balance', 'diff_new_old_destiny']
        df3[num_columns] = self.minmaxscaler.transform(df3[num_columns])
        
        # Final columns expected by the model
        final_columns_selected = ['step', 'old_balance_org', 'new_balance_orig', 
                                'new_balance_dest', 'diff_new_old_balance', 
                                'diff_new_old_destiny', 'type_TRANSFER']
        
        # Drop any extra columns and keep only the expected ones
        df3 = df3[final_columns_selected]
        
        # Debugging: Print the shape and columns of the final dataset
        print("Final data shape:", df3.shape)
        print("Final data columns:", df3.columns.tolist())
        
        return df3

    def get_prediction(self, model, original_data, test_data):
        # Validate test data dimensions
        print("Test data shape before prediction:", test_data.shape)
        
        # Get model predictions
        try:
            pred = model.predict(test_data)
            original_data['prediction'] = pred
            return original_data.to_json(orient="records", date_format="iso")
        except Exception as e:
            # Debugging: Log detailed error information
            print("Error during prediction:", str(e))
            return {"error": "An error occurred during prediction", "message": str(e)}



# API Endpoint to handle fraud prediction requests
@app.route('/fraud/predict', methods=['POST'])
def predict_fraud():
    try:
        # Parse input data
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        df = pd.DataFrame(input_data)
        fraud_detector = Fraud()

        # Data pipeline: cleaning, feature engineering, and preparation
        df_cleaned = fraud_detector.data_cleaning(df)
        df_features = fraud_detector.feature_engineering(df_cleaned)
        df_prepared = fraud_detector.data_preparation(df_features)

        # Load the trained model
        model = joblib.load('./parameters/fraud_model.joblib')

        # Get predictions
        return fraud_detector.get_prediction(model, df, df_prepared)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


# Run the application (for local testing)
if __name__ == '__main__':
    app.run(debug=True)
