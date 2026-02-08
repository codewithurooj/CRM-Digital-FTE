/**
 * Main web support form component — React/Next.js.
 * Fields: name, email, subject, category, priority, message.
 * Client-side validation matching server-side Pydantic validation.
 */
import React, { useState } from 'react';
import FormField from './FormField';
import SuccessMessage from './SuccessMessage';
import { useFormValidation } from '../hooks/useFormValidation';
import { submitForm } from '../services/api';

const CATEGORIES = [
  { value: 'account_access', label: 'Account Access' },
  { value: 'billing', label: 'Billing' },
  { value: 'technical', label: 'Technical Issue' },
  { value: 'how_to', label: 'How-To Question' },
  { value: 'feature_request', label: 'Feature Request' },
  { value: 'complaint', label: 'Complaint' },
];

const PRIORITIES = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
];

const INITIAL_FORM = {
  name: '',
  email: '',
  subject: '',
  category: '',
  priority: 'medium',
  message: '',
};

export default function SupportForm() {
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [ticketId, setTicketId] = useState(null);
  const { errors, validateAll, validateField, clearError } = useFormValidation();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    clearError(name);
    setSubmitError('');
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    const error = validateField(name, value);
    if (error) {
      // error is set via validateAll, we use individual validation for UX
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');

    if (!validateAll(formData)) {
      return;
    }

    setSubmitting(true);

    try {
      const result = await submitForm(formData);
      setTicketId(result.ticket_id);
    } catch (err) {
      setSubmitError(err.message || 'Failed to submit form. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitAnother = () => {
    setFormData(INITIAL_FORM);
    setTicketId(null);
    setSubmitError('');
  };

  if (ticketId) {
    return <SuccessMessage ticketId={ticketId} onSubmitAnother={handleSubmitAnother} />;
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '4px' }}>
        TechCorp Support
      </h2>
      <p style={{ fontSize: '14px', color: '#718096', marginBottom: '24px' }}>
        How can we help? Fill out the form below and our team will get back to you within 30 minutes.
      </p>

      <form onSubmit={handleSubmit} noValidate>
        <FormField
          label="Name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.name}
          required
          placeholder="Your full name"
        />

        <FormField
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.email}
          required
          placeholder="you@example.com"
        />

        <FormField
          label="Subject"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.subject}
          required
          placeholder="Brief description of your issue"
        />

        <FormField
          label="Category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.category}
          required
          options={CATEGORIES}
        />

        <FormField
          label="Priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.priority}
          options={PRIORITIES}
        />

        <FormField
          label="Message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.message}
          required
          placeholder="Describe your issue in detail..."
          rows={5}
        />

        {submitError && (
          <p role="alert" style={{ color: '#e53e3e', fontSize: '13px', marginBottom: '12px' }}>
            {submitError}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: submitting ? '#a0aec0' : '#3182ce',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: submitting ? 'not-allowed' : 'pointer',
          }}
        >
          {submitting ? 'Submitting...' : 'Submit Support Request'}
        </button>
      </form>
    </div>
  );
}
