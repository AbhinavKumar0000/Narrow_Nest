// Helper function to handle fetch requests with error handling
async function handleFetch(url, options, successCallback, errorMessage) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        successCallback(data);
    } catch (error) {
        console.error(errorMessage, error);
        document.getElementById('result').innerHTML = `<p>${errorMessage}</p>`;
    }
}

// Job Form Submission
document.getElementById('jobForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    handleFetch(
        '/post_job',
        { method: 'POST', body: formData },
        (data) => {
            const resultDiv = document.getElementById('result');
            if (data.linkedin_error) {
                resultDiv.innerHTML = `<p>${data.linkedin_error}</p>`;
            } else {
                resultDiv.innerHTML = `
                    <p>Job posted successfully!</p>
                    <p>Application Link: <a href="${data.application_link}">${data.application_link}</a></p>
                    ${data.linkedin_job_url ? `<p>LinkedIn Job URL: <a href="${data.linkedin_job_url}">${data.linkedin_job_url}</a></p>` : ''}
                `;
                setTimeout(() => location.reload(), 2000); // Refresh after 2 seconds
            }
        },
        'Error posting job'
    );
});

// Apply Form Submission
document.getElementById('applyForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    handleFetch(
        window.location.pathname,
        { method: 'POST', body: formData },
        (data) => {
            document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
        },
        'Error submitting application'
    );
});

// Chatbot Form Submission
document.getElementById('chatbotForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    handleFetch(
        window.location.pathname,
        { method: 'POST', body: formData },
        (data) => {
            document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
        },
        'Error submitting interview'
    );
});

// Remove Job Button
document.querySelectorAll('.remove-button').forEach(button => {
    button.addEventListener('click', function () {
        const jobId = this.getAttribute('data-job-id');
        if (confirm('Are you sure you want to remove this job?')) {
            handleFetch(
                `/delete_job/${jobId}`,
                { method: 'POST' },
                (data) => {
                    alert(data.message);
                    this.closest('.job-card').remove(); // Remove the job card from the UI
                },
                'Error removing job'
            );
        }
    });
});