from flask import Flask, render_template, request, jsonify
import pickle

app = Flask(__name__)

# Custom Model Wrapper
class ElectricityBillPredictor:
    def __init__(self):
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

        # Encodings
        self.city_encoding = {
            'Mumbai': 0, 'New Delhi': 1, 'Hyderabad': 2,
            'Vadodara': 3, 'Shimla': 4, 'Ratnagiri': 5
        }

        self.company_encoding = {
            'Tata Power Company Ltd.': 0,
            'Adani Power Ltd.': 1,
            'Power Grid Corp': 2,
            'NHPC': 3,
            'Jyoti Structure': 4,
            'Kalpataru Power': 5,
            'Ratnagiri Gas and Power Pvt. Ltd. (RGPPL)': 6
        }
        self.month_encoding = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }

    def train(self, df):
        from sklearn.preprocessing import StandardScaler
        required_columns = ['Fan', 'Refrigerator', 'AirConditioner', 'Television', 'Monitor', 'MotorPump',
                            'Month', 'City', 'Company', 'MonthlyHours', 'TariffRate', 'ElectricityBill']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"❌ Missing columns in dataset: {missing}")

        # Encode categorical columns
        df['City'] = df['City'].map(self.city_encoding)
        df['Company'] = df['Company'].map(self.company_encoding)
        df['Month'] = df['Month'].map(self.month_encoding)

        # Prepare features and target
        X = df[['Fan', 'Refrigerator', 'AirConditioner', 'Television', 'Monitor', 'MotorPump',
                'Month', 'City', 'Company', 'MonthlyHours', 'TariffRate']]
        y = df['ElectricityBill']

        # Scale features and train the model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, city, company, daily_hours, appliances, month_name, tariff_rate):
        try:
            monthly_hours = daily_hours * 30
            print(f"Debug - predict: daily_hours={daily_hours}, monthly_hours={monthly_hours}")  # Debug print

            # Ensure appliance names match the model's expected names
            input_features = [
                appliances.get('Fan', 0),  # Default to 0 if key missing
                appliances.get('Refrigerator', 0),
                appliances.get('AirConditioner', 0),
                appliances.get('Television', 0),
                appliances.get('Monitor', 0),
                appliances.get('MotorPump', 0),
                self.month_encoding[month_name],
                self.city_encoding[city],
                self.company_encoding[company],
                monthly_hours,
                tariff_rate
            ]

            input_scaled = self.scaler.transform([input_features])
            prediction = self.model.predict(input_scaled)
            print(f"Debug - predict: prediction={prediction[0]}")  # Debug print
            return prediction[0]

        except Exception as e:
            print(f"Prediction error: {e}")
            return None

# Load and validate the model
try:
    with open('linear_model.pkl', 'rb') as f:
        predictor = pickle.load(f)  # Load as an instance of ElectricityBillPredictor
    print(f"Model type: {type(predictor)}")  # Debug print
    if not hasattr(predictor, 'predict'):
        raise ValueError("linear_model.pkl' does not have a 'predict' method.")
except FileNotFoundError:
    raise FileNotFoundError("Model file 'linear_model.pkl' not found in project directory")
except Exception as e:
    raise Exception(f"Error loading model: {str(e)}")

# Route to serve the index.html form
@app.route('/')
def form():
    return render_template('index.html')

# Route to make predictions using the loaded model
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract form data
        def get_form_float_value(field_name, default=0):
            value = request.form.get(field_name)
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        # Collect features from the form
        fans = get_form_float_value('fans')
        refrigerator = get_form_float_value('refrigerator')
        ac = get_form_float_value('ac')
        tv = get_form_float_value('tv')
        monitor = get_form_float_value('monitor')
        pump = get_form_float_value('pump')
        month = get_form_float_value('month')
        city = request.form.get('city', 'Mumbai')  # Get city name
        company = request.form.get('company', 'Tata Power Company Ltd.')  # Get company name
        monthly_hours = get_form_float_value('hoursSlider')
        tariff_rate = get_form_float_value('tariff')

        print(f"Debug - form: monthly_hours={monthly_hours}")  # Debug print

        # Map month value to name
        month_mapping = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        month_name = month_mapping.get(int(month), 'January')

        # Prepare appliances dictionary with model-expected names
        appliances = {
            'Fan': fans,
            'Refrigerator': refrigerator,
            'AirConditioner': ac,
            'Television': tv,
            'Monitor': monitor,
            'MotorPump': pump
        }

        # Make prediction using the predictor's predict method
        daily_hours = monthly_hours / 30  # Convert to daily hours
        print(f"Debug - predict call: daily_hours={daily_hours}, monthly_hours={monthly_hours}")  # Debug print
        prediction = predictor.predict(
            city=city,
            company=company,
            daily_hours=daily_hours,
            appliances=appliances,
            month_name=month_name,
            tariff_rate=tariff_rate
        )

        if prediction is None:
            return jsonify({"error": "Prediction failed. Check server logs for details."}), 500

        # Calculate monthly bill (prediction is already in the same units as ElectricityBill, i.e., ₹)
        monthly_bill = prediction

        # Return prediction and bill
        return jsonify({
            "prediction": float(prediction),  # Monthly bill in ₹
            "monthly_bill": float(monthly_bill),  # Monthly bill in ₹
            "model_used": "linear_model.pkl"
        })
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

