// Common functions
document.addEventListener('DOMContentLoaded', function() {
    // Delete match handler
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this match?')) {
                e.preventDefault();
            }
        });
    });

    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const action = form.getAttribute('action');
            const method = form.getAttribute('method').toUpperCase();

            try {
                const response = await fetch(action, {
                    method: method,
                    body: JSON.stringify(Object.fromEntries(formData)),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                const result = await response.json();
                
                if (response.ok) {
                    showMessage(result.message || 'Operation successful!', 'success');
                    if (form.id === 'create-form' || form.id === 'update-form') {
                        setTimeout(() => {
                            window.location.href = '/matches';
                        }, 1500);
                    }
                } else {
                    showMessage(result.error || 'An error occurred', 'error');
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, 'error');
            }
        });
    });
});

function showMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

// Delete match via AJAX
async function deleteMatch(matchId) {
    try {
        const response = await fetch(`/delete_match/${matchId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (response.ok) {
            showMessage(result.message || 'Match deleted successfully', 'success');
            document.getElementById(`match-${matchId}`).remove();
        } else {
            showMessage(result.error || 'Error deleting match', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}