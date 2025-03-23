
    document.addEventListener('DOMContentLoaded', function() {
        const searchForm = document.getElementById('search-form');
        const loadingElement = document.getElementById('loading');
        const resultsElement = document.getElementById('results');
        const resultsContentElement = document.getElementById('results-content');
        const errorElement = document.getElementById('error');
        const errorMessageElement = document.getElementById('error-message');
        
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Hide results and error
            resultsElement.style.display = 'none';
            errorElement.style.display = 'none';
            
            // Show loading
            loadingElement.style.display = 'block';
            
            // Get form data
            const formData = new FormData(searchForm);
            
            // Send request
            fetch('/search', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                loadingElement.style.display = 'none';
                
                if (data.error) {
                    // Show error
                    errorMessageElement.textContent = data.error;
                    errorElement.style.display = 'block';
                } else {
                    // Show results
                    resultsContentElement.textContent = data.result;
                    resultsElement.style.display = 'block';
                }
            })
            .catch(error => {
                // Hide loading
                loadingElement.style.display = 'none';
                
                // Show error
                errorMessageElement.textContent = 'An error occurred: ' + error.message;
                errorElement.style.display = 'block';
            });
        });
    });
    