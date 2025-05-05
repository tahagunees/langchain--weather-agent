document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const locationInput = document.getElementById('locationInput');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const weatherInfoDiv = document.getElementById('weatherInfo');
    const recommendationsDiv = document.getElementById('recommendations');
    const errorMessageP = document.getElementById('errorMessage');

    // Add a nice placeholder animation
    animatePlaceholder();

    // Function to animate placeholder
    function animatePlaceholder() {
        const placeholders = [
            "Şehir adı girin (örn. Istanbul)",
            "Şehir adı girin (örn. Ankara)",
            "Şehir adı girin (örn. Izmir)",
            "Şehir adı girin (örn. Antalya)"
        ];
        
        let i = 0;
        setInterval(() => {
            i = (i + 1) % placeholders.length;
            locationInput.setAttribute('placeholder', placeholders[i]);
        }, 3000);
    }

    // Function to show loading state
    function showLoading() {
        loadingDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        // Smooth scroll to loading indicator
        loadingDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Add a function to highlight temperature in the text
    function highlightTemperature(text) {
        // Look for temperature patterns like "15.1°C" or "15°C"
        return text.replace(/(\d+(?:\.\d+)?°C)/g, '<span class="weather-highlight">$1</span>');
    }

    // Function to show results
    function showResults(data) {
        loadingDiv.classList.add('hidden');
        resultDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');

        // Process response and format it with better styling
        const responseText = data.response;
        
        console.log("API Response:", responseText); // Debug log
        
        if (!responseText) {
            showError("API yanıtı boş geldi. Lütfen tekrar deneyin.");
            return;
        }
        
        // Check if there's any weather information
        if (responseText.toLowerCase().includes("hava") || 
            responseText.toLowerCase().includes("sıcaklık") || 
            responseText.toLowerCase().includes("temperature")) {
            
            // Try to separate weather info from clothing recommendations
            let parts = [];
            
            if (responseText.includes("Önerilen kıyafetler:")) {
                parts = responseText.split('Önerilen kıyafetler:');
            } else if (responseText.includes("önerilen kıyafetler:")) {
                parts = responseText.split('önerilen kıyafetler:');
            } else if (responseText.includes("öneriler:")) {
                parts = responseText.split('öneriler:');
            } else if (responseText.includes("giymenizi öneririm")) {
                // Handle case like in the screenshot
                const weatherPart = responseText.split('giymenizi öneririm')[0] + "giymenizi öneririm.";
                parts = [weatherPart, responseText.replace(weatherPart, "")];
            } else {
                // If we can't find a clear separator, make an educated guess
                const lines = responseText.split('\n');
                const weatherLines = [];
                const clothingLines = [];
                
                let foundClothing = false;
                
                for (const line of lines) {
                    if (!foundClothing && 
                        (line.includes("giy") || 
                         line.includes("mont") || 
                         line.includes("kıyafet") || 
                         line.includes("gömlek") ||
                         line.includes("pantolon"))) {
                        foundClothing = true;
                    }
                    
                    if (foundClothing) {
                        clothingLines.push(line);
                    } else {
                        weatherLines.push(line);
                    }
                }
                
                parts = [weatherLines.join('\n'), clothingLines.join('\n')];
            }
            
            if (parts.length >= 2 && parts[0].trim()) {
                // Format weather info with icons based on content
                let weatherInfo = parts[0].trim();
                
                // Highlight temperature
                weatherInfo = highlightTemperature(weatherInfo);
                
                // Add weather condition icon based on text
                if (weatherInfo.toLowerCase().includes('güneşli') || weatherInfo.toLowerCase().includes('açık')) {
                    weatherInfo = '<i class="fas fa-sun fa-2x" style="color: #f39c12;"></i> ' + weatherInfo;
                } else if (weatherInfo.toLowerCase().includes('yağmur')) {
                    weatherInfo = '<i class="fas fa-cloud-rain fa-2x" style="color: #3498db;"></i> ' + weatherInfo;
                } else if (weatherInfo.toLowerCase().includes('kar')) {
                    weatherInfo = '<i class="fas fa-snowflake fa-2x" style="color: #2980b9;"></i> ' + weatherInfo;
                } else if (weatherInfo.toLowerCase().includes('bulut')) {
                    weatherInfo = '<i class="fas fa-cloud fa-2x" style="color: #95a5a6;"></i> ' + weatherInfo;
                } else {
                    weatherInfo = '<i class="fas fa-cloud-sun fa-2x" style="color: #f39c12;"></i> ' + weatherInfo;
                }
                
                weatherInfoDiv.innerHTML = weatherInfo;
                
                // Format recommendations as a list with proper styling
                const recommendations = parts[1].trim().split('\n');
                let recommendationsHTML = '<strong><i class="fas fa-clipboard-list"></i> Önerilen Kıyafetler</strong>';
                
                recommendations.forEach(rec => {
                    // Skip empty lines
                    if (rec.trim()) {
                        recommendationsHTML += `<p>${rec}</p>`;
                    }
                });
                
                recommendationsDiv.innerHTML = recommendationsHTML;
            } else {
                // If parsing fails, just display everything in the weather section
                weatherInfoDiv.innerHTML = '<i class="fas fa-info-circle"></i> ' + highlightTemperature(responseText);
                recommendationsDiv.innerHTML = '';
            }
        } else {
            // If there's no weather info, just display everything
            weatherInfoDiv.innerHTML = '<i class="fas fa-info-circle"></i> ' + responseText;
            recommendationsDiv.innerHTML = '';
        }
        
        // Smooth scroll to results
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Function to show error
    function showError(message) {
        loadingDiv.classList.add('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.remove('hidden');
        errorMessageP.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + message;
        
        // Smooth scroll to error
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Function to fetch weather and recommendations
    function getWeatherAndRecommendations(location) {
        showLoading();

        fetch('/get_recommendation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ location: location }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Bir hata oluştu');
                });
            }
            return response.json();
        })
        .then(data => {
            showResults(data);
        })
        .catch(error => {
            showError(error.message);
        });
    }

    // Event listener for search button
    searchButton.addEventListener('click', function() {
        const location = locationInput.value.trim();
        if (location) {
            getWeatherAndRecommendations(location);
        } else {
            showError('Lütfen bir konum girin');
        }
    });

    // Event listener for Enter key in the input field
    locationInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const location = locationInput.value.trim();
            if (location) {
                getWeatherAndRecommendations(location);
            } else {
                showError('Lütfen bir konum girin');
            }
        }
    });
    
    // Add a little pulse animation to the search button to draw attention
    setTimeout(() => {
        searchButton.classList.add('pulse');
        setTimeout(() => {
            searchButton.classList.remove('pulse');
        }, 1000);
    }, 1500);
}); 