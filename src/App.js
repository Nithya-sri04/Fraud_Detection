import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    step: '',
    type: '',
    amount: '',
    oldbalance_org: '',
    newbalance_orig: '',
    oldbalance_dest: '',
    newbalance_dest: '',
    name_orig: '',
    name_dest: '',
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation Check: Ensure all fields are filled
    const requiredFields = [
      'step',
      'type',
      'amount',
      'oldbalance_org',
      'newbalance_orig',
      'oldbalance_dest',
      'newbalance_dest',
      'name_orig',
      'name_dest',
    ];

    for (const field of requiredFields) {
      if (!formData[field]) {
        alert(`Please fill in the ${field} field.`);
        return;
      }
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/predict', formData);
      setPrediction(response.data.prediction);
    } catch (error) {
      alert('Error while predicting fraud. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Fraud Detection System</h1>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <h2>Enter Transaction Details</h2>
          <div className="form-group">
            <label>Step:</label>
            <input
              type="number"
              name="step"
              value={formData.step}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Type:</label>
            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              required
            >
              <option value="">Select</option>
              <option value="CASH_OUT">CASH_OUT</option>
              <option value="TRANSFER">TRANSFER</option>
            </select>
          </div>
          <div className="form-group">
            <label>Amount:</label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Old Balance (Org):</label>
            <input
              type="number"
              name="oldbalance_org"
              value={formData.oldbalance_org}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>New Balance (Orig):</label>
            <input
              type="number"
              name="newbalance_orig"
              value={formData.newbalance_orig}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Old Balance (Dest):</label>
            <input
              type="number"
              name="oldbalance_dest"
              value={formData.oldbalance_dest}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>New Balance (Dest):</label>
            <input
              type="number"
              name="newbalance_dest"
              value={formData.newbalance_dest}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Name Orig:</label>
            <input
              type="text"
              name="name_orig"
              value={formData.name_orig}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Name Dest:</label>
            <input
              type="text"
              name="name_dest"
              value={formData.name_dest}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" className="btn" disabled={loading}>
          {loading ? <div className="spinner"></div> : 'Predict Fraud'}
          </button>

          <button
            type="button"
            className="btn clear"
            onClick={() =>
              setFormData({
                step: '',
                type: '',
                amount: '',
                oldbalance_org: '',
                newbalance_orig: '',
                oldbalance_dest: '',
                newbalance_dest: '',
                name_orig: '',
                name_dest: '',
              })
            }
          >
            Clear Form
          </button>
        </form>
      </div>
  {prediction !== null && (
  <div className="result">
    <h2>Transaction Details</h2>
    <table>
      <tbody>
        {Object.entries(formData).map(([key, value]) => (
          <tr key={key}>
            <td>{key}</td>
            <td>{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
    <h3>
      Prediction: <strong>{prediction ? 'Fraudulent' : 'Not Fraudulent'}</strong>
    </h3>
  </div>
)}

    </div>
  );
}

export default App;
