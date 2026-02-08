/**
 * Post-submission success confirmation — displays ticket ID and next steps.
 */
import React from 'react';

export default function SuccessMessage({ ticketId, onSubmitAnother }) {
  return (
    <div style={{
      padding: '24px',
      border: '1px solid #c6f6d5',
      borderRadius: '8px',
      backgroundColor: '#f0fff4',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>&#10003;</div>
      <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px', color: '#276749' }}>
        Support Request Submitted
      </h2>
      <p style={{ fontSize: '14px', color: '#2f855a', marginBottom: '16px' }}>
        Your ticket has been created. Our team will respond within 30 minutes.
      </p>
      <div style={{
        display: 'inline-block',
        padding: '8px 16px',
        backgroundColor: '#fff',
        border: '1px solid #c6f6d5',
        borderRadius: '6px',
        marginBottom: '16px',
      }}>
        <span style={{ fontSize: '12px', color: '#718096' }}>Ticket ID</span>
        <p style={{ fontSize: '18px', fontWeight: 700, color: '#2d3748', margin: '4px 0 0' }}>
          {ticketId}
        </p>
      </div>
      <p style={{ fontSize: '13px', color: '#718096', marginBottom: '16px' }}>
        Save this ticket ID to check your status below.
      </p>
      {onSubmitAnother && (
        <button
          onClick={onSubmitAnother}
          style={{
            padding: '8px 20px',
            backgroundColor: '#fff',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Submit Another Request
        </button>
      )}
    </div>
  );
}
