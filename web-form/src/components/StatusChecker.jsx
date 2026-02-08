/**
 * Ticket status checker — input ticket ID, fetch and display status.
 */
import React, { useState } from 'react';
import { getTicketStatus } from '../services/api';

export default function StatusChecker() {
  const [ticketId, setTicketId] = useState('');
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCheck = async (e) => {
    e.preventDefault();
    const trimmed = ticketId.trim();
    if (!trimmed) {
      setError('Please enter a ticket ID');
      return;
    }

    setLoading(true);
    setError('');
    setTicket(null);

    try {
      const data = await getTicketStatus(trimmed);
      setTicket(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch ticket status');
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    open: '#3182ce',
    processing: '#d69e2e',
    resolved: '#38a169',
    escalated: '#e53e3e',
    closed: '#718096',
  };

  return (
    <div style={{ padding: '24px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#fff' }}>
      <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px' }}>Check Ticket Status</h3>

      <form onSubmit={handleCheck} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <input
          type="text"
          value={ticketId}
          onChange={(e) => { setTicketId(e.target.value); setError(''); }}
          placeholder="Enter ticket ID (e.g., TKT-0001)"
          style={{
            flex: 1,
            padding: '8px 12px',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            fontSize: '14px',
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3182ce',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'Checking...' : 'Check'}
        </button>
      </form>

      {error && (
        <p role="alert" style={{ color: '#e53e3e', fontSize: '13px', marginBottom: '12px' }}>{error}</p>
      )}

      {ticket && (
        <div style={{ padding: '16px', backgroundColor: '#f7fafc', borderRadius: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <strong>{ticket.ticket_id}</strong>
            <span style={{
              padding: '2px 10px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 600,
              color: '#fff',
              backgroundColor: statusColors[ticket.status] || '#718096',
            }}>
              {ticket.status}
            </span>
          </div>
          <p style={{ fontSize: '14px', marginBottom: '4px' }}><strong>Subject:</strong> {ticket.subject}</p>
          <p style={{ fontSize: '13px', color: '#718096', marginBottom: '4px' }}>
            Category: {ticket.category} | Priority: {ticket.priority} | Channel: {ticket.source_channel}
          </p>
          {ticket.responses && ticket.responses.length > 0 && (
            <div style={{ marginTop: '12px', borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
              <p style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>Responses:</p>
              {ticket.responses.map((r, i) => (
                <div key={i} style={{ padding: '8px', backgroundColor: '#fff', borderRadius: '4px', marginBottom: '8px', fontSize: '13px' }}>
                  <p>{r.content}</p>
                  <p style={{ color: '#a0aec0', fontSize: '11px', marginTop: '4px' }}>
                    {new Date(r.created_at).toLocaleString()} via {r.channel}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
