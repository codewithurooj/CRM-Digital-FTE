/**
 * API client for CRM Digital FTE web support form.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Submit a support form.
 * @param {Object} formData - { name, email, subject, category, priority, message }
 * @returns {Promise<Object>} - { ticket_id, status, message, created_at }
 */
export async function submitForm(formData) {
  const response = await fetch(`${API_BASE_URL}/support/form`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Submission failed' }));
    throw new Error(error.detail || error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get ticket status by ticket ID.
 * @param {string} ticketId - Ticket number (e.g., TKT-0001)
 * @returns {Promise<Object>} - { ticket_id, status, category, priority, subject, responses }
 */
export async function getTicketStatus(ticketId) {
  const response = await fetch(`${API_BASE_URL}/tickets/${encodeURIComponent(ticketId)}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Ticket not found');
    }
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch ticket' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
