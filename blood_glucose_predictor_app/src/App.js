import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [glucose, setGlucose] = useState('');
    const [predictions, setPredictions] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const datetime = new Date();

        try {
            const response = await axios.post('http://localhost:5000/predict', { glucose, datetime });
            setPredictions(response.data);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const displayPredictions = (predictions) => {
        if (!predictions || typeof predictions !== 'object') {
            return <div>No predictions available.</div>;
        }

        // Convert the predictions object to an array of [key, value] pairs
        const predictionsArray = Object.entries(predictions);

        // Use .map() to iterate over the array
        const predictionList = predictionsArray.map(([time, value]) => (
            <li key={time}>
                In {time}: {value.Prediction.toFixed(1)} mmol/L 
                (Range: {value.Lower_Bound.toFixed(1)} - {value.Upper_Bound.toFixed(1)})
            </li>
        ));

        return (
            <div>
                <h2>Predictions</h2>
                <ul>{predictionList}</ul>
            </div>
        );
    };

    return (
        <div>
            <h1>Glucose Prediction</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="number"
                    value={glucose}
                    onChange={(e) => setGlucose(e.target.value)}
                    placeholder="Enter Glucose Level"
                    required
                />
                <button type="submit">Predict</button>
            </form>

            {predictions && displayPredictions(predictions)}
        </div>
    );
}

export default App;