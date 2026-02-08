/**
 * Client-side form validation hook — mirrors server-side Pydantic validation.
 */
import { useState, useCallback } from 'react';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const VALIDATION_RULES = {
  name: {
    required: true,
    minLength: 2,
    maxLength: 255,
    message: 'Name must be at least 2 characters',
  },
  email: {
    required: true,
    pattern: EMAIL_REGEX,
    message: 'Please enter a valid email address',
  },
  subject: {
    required: true,
    minLength: 5,
    maxLength: 500,
    message: 'Subject must be at least 5 characters',
  },
  category: {
    required: true,
    message: 'Please select a category',
  },
  message: {
    required: true,
    minLength: 10,
    message: 'Message must be at least 10 characters',
  },
};

export function useFormValidation() {
  const [errors, setErrors] = useState({});

  const validateField = useCallback((name, value) => {
    const rule = VALIDATION_RULES[name];
    if (!rule) return '';

    const val = (value || '').trim();

    if (rule.required && !val) {
      return `${name.charAt(0).toUpperCase() + name.slice(1)} is required`;
    }

    if (rule.minLength && val.length < rule.minLength) {
      return rule.message;
    }

    if (rule.maxLength && val.length > rule.maxLength) {
      return `${name.charAt(0).toUpperCase() + name.slice(1)} must be under ${rule.maxLength} characters`;
    }

    if (rule.pattern && !rule.pattern.test(val)) {
      return rule.message;
    }

    return '';
  }, []);

  const validateAll = useCallback((formData) => {
    const newErrors = {};
    let isValid = true;

    for (const [field, rule] of Object.entries(VALIDATION_RULES)) {
      const error = validateField(field, formData[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [validateField]);

  const clearError = useCallback((field) => {
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrors({});
  }, []);

  return { errors, validateField, validateAll, clearError, clearAllErrors };
}
