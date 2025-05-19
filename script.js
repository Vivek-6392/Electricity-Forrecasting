//document.getElementById('predictBtn').addEventListener('click', async () => {
//    // Show loading indicator
//    const loadingIndicator = document.getElementById('loadingIndicator');
//    loadingIndicator.style.display = 'block';
//
//    // Collect form data
//    const formData = new FormData();
//    formData.append('fans', document.getElementById('fans').value);
//    formData.append('refrigerator', document.getElementById('refrigerator').value);
//    formData.append('ac', document.getElementById('ac').value);
//    formData.append('tv', document.getElementById('tv').value);
//    formData.append('monitor', document.getElementById('monitor').value);
//    formData.append('pump', document.getElementById('pump').value);
//    formData.append('month', document.getElementById('month').value);
//    formData.append('city', document.getElementById('city').value);
//    formData.append('company', document.getElementById('company').value);
//    formData.append('hoursSlider', document.getElementById('hoursSlider').value);
//    formData.append('tariff', document.getElementById('tariff').value);
//
//    try {
//        // Send form data to /predict endpoint
//        const response = await fetch('/predict', {
//            method: 'POST',
//            body: formData
//        });
//        const result = await response.json();
//
//        // Hide loading indicator
//        loadingIndicator.style.display = 'none';
//
//        if (result.error) {
//            alert('Error: ' + result.error);
//            return;
//        }
//
//        // Update UI with prediction results
//        document.getElementById('kwh-result').textContent = `${result.prediction.toFixed(2)/tariff}`;
//        document.getElementById('billResult').textContent = `₹${result.monthly_bill.toFixed(2)}`;
//        document.getElementById('modelInfo').textContent = `Prediction based on ${result.model_used}`;
//
//        // Populate consumption breakdown (placeholder)
//        const breakdownList = document.getElementById('breakdownList');
//        breakdownList.innerHTML = `
//            <p>Fans: ${(result.prediction * 0.3).toFixed(2)} Rs</p>
//            <p>Air Conditioners: ${(result.prediction * 0.4).toFixed(2)} Rs</p>
//            <p>Refrigerators: ${(result.prediction * 0.2).toFixed(2)} Rs</p>
//            <p>Others: ${(result.prediction * 0.1).toFixed(2)} Rs</p>
//        `;
//
//        // Populate recommendations (placeholder)
//        const recommendationsList = document.getElementById('recommendationsList');
//        recommendationsList.innerHTML = `
//            <p>Consider using energy-efficient appliances to reduce consumption.</p>
//            <p>Turn off devices when not in use.</p>
//            <p>Optimize air conditioner usage during peak hours.</p>
//        `;
//    } catch (error) {
//        // Hide loading indicator and show error
//        loadingIndicator.style.display = 'none';
//        alert('Error: ' + error.message);
//    }
//});

document.getElementById('predictBtn').addEventListener('click', async () => {
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.style.display = 'block';

    // Collect form data
    const fans = document.getElementById('fans').value;
    const refrigerator = document.getElementById('refrigerator').value;
    const ac = document.getElementById('ac').value;
    const tv = document.getElementById('tv').value;
    const monitor = document.getElementById('monitor').value;
    const pump = document.getElementById('pump').value;
    const month = document.getElementById('month').value;
    const city = document.getElementById('city').value;
    const company = document.getElementById('company').value;
    const hoursSlider = document.getElementById('hoursSlider').value;
    const tariff = parseFloat(document.getElementById('tariff').value); // <--- parse to number!

    const formData = new FormData();
    formData.append('fans', fans);
    formData.append('refrigerator', refrigerator);
    formData.append('ac', ac);
    formData.append('tv', tv);
    formData.append('monitor', monitor);
    formData.append('pump', pump);
    formData.append('month', month);
    formData.append('city', city);
    formData.append('company', company);
    formData.append('hoursSlider', hoursSlider);
    formData.append('tariff', tariff);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        loadingIndicator.style.display = 'none';

        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }

        // Fix: result.prediction is a number, use it directly
        document.getElementById('kwh-result').textContent = (result.prediction / tariff).toFixed(2);
        document.getElementById('billResult').textContent = `₹${result.monthly_bill.toFixed(2)}`;
        document.getElementById('modelInfo').textContent = `Prediction based on ${result.model_used}`;

        const breakdownList = document.getElementById('breakdownList');
        breakdownList.innerHTML = `
            <p>Fans: ₹${(result.prediction * 0.3).toFixed(2)}</p>
            <p>Air Conditioners: ₹${(result.prediction * 0.4).toFixed(2)}</p>
            <p>Refrigerators: ₹${(result.prediction * 0.2).toFixed(2)}</p>
            <p>Others: ₹${(result.prediction * 0.1).toFixed(2)}</p>
        `;

        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = `
            <p>Consider using energy-efficient appliances to reduce consumption.</p>
            <p>Turn off devices when not in use.</p>
            <p>Optimize air conditioner usage during peak hours.</p>
        `;
    } catch (error) {
        loadingIndicator.style.display = 'none';
        alert('Error: ' + error.message);
    }
});
