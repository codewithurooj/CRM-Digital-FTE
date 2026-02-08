/**
 * Reusable form field component with label, error display, and required indicator.
 */
import React from 'react';

export default function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  onBlur,
  error,
  required = false,
  placeholder = '',
  options = null,
  rows = null,
}) {
  const inputId = `field-${name}`;
  const hasError = Boolean(error);

  const baseStyle = {
    width: '100%',
    padding: '8px 12px',
    border: `1px solid ${hasError ? '#e53e3e' : '#d1d5db'}`,
    borderRadius: '6px',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box',
  };

  const renderInput = () => {
    if (options) {
      return (
        <select
          id={inputId}
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          style={baseStyle}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${inputId}-error` : undefined}
        >
          <option value="">Select {label.toLowerCase()}...</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      );
    }

    if (rows) {
      return (
        <textarea
          id={inputId}
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          rows={rows}
          style={{ ...baseStyle, resize: 'vertical' }}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${inputId}-error` : undefined}
        />
      );
    }

    return (
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        style={baseStyle}
        aria-invalid={hasError}
        aria-describedby={hasError ? `${inputId}-error` : undefined}
      />
    );
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label htmlFor={inputId} style={{ display: 'block', marginBottom: '4px', fontWeight: 500, fontSize: '14px' }}>
        {label}
        {required && <span style={{ color: '#e53e3e', marginLeft: '4px' }}>*</span>}
      </label>
      {renderInput()}
      {hasError && (
        <p id={`${inputId}-error`} role="alert" style={{ color: '#e53e3e', fontSize: '12px', marginTop: '4px' }}>
          {error}
        </p>
      )}
    </div>
  );
}
