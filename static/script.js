document.addEventListener('DOMContentLoaded', () => {
    const transcriptionForm = document.getElementById('transcriptionForm');
    const fileInput = document.getElementById('file');
    const apiTokenInput = document.getElementById('apiToken');
    const promptContextInput = document.getElementById('promptContext');
    const submitButton = document.getElementById('submitButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultDiv = document.getElementById('result');

    transcriptionForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const file = fileInput.files[0];
        const token = apiTokenInput.value.trim();
        const promptContext = promptContextInput.value.trim();

        if (!file) {
            resultDiv.textContent = 'Please select a file.';
            resultDiv.className = 'error';
            resultDiv.classList.remove('hidden');
            return;
        }

        if (!token) {
            resultDiv.textContent = 'Please enter your API token.';
            resultDiv.className = 'error';
            resultDiv.classList.remove('hidden');
            return;
        }

        // Show loading state
        loadingIndicator.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        submitButton.disabled = true;
        submitButton.setAttribute('aria-busy', 'true');

        const formData = new FormData();
        formData.append('file', file);
        if (promptContext) {
            formData.append('prompt_context', promptContext);
        }

        try {
            // Assuming the backend runs on http://localhost:8000
            // Adjust if your backend URL is different.
            const response = await fetch('http://localhost:8000/transcribe/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    // 'Content-Type' is not needed here for FormData;
                    // the browser sets it correctly with the boundary.
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred. Check server logs.' }));
                throw new Error(`HTTP error! status: ${response.status}, Message: ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            resultDiv.textContent = data.transcript;
            resultDiv.className = ''; // Reset class to default
        } catch (error) {
            console.error('Transcription error:', error);
            resultDiv.textContent = `Error: ${error.message}`;
            resultDiv.className = 'error';
        } finally {
            // Hide loading state
            loadingIndicator.classList.add('hidden');
            resultDiv.classList.remove('hidden');
            submitButton.disabled = false;
            submitButton.setAttribute('aria-busy', 'false');
        }
    });
});
