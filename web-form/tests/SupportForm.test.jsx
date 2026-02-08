/**
 * React component tests for SupportForm — renders, validates, submits, shows states.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SupportForm from '../src/components/SupportForm';

// Mock the API module
jest.mock('../src/services/api', () => ({
  submitForm: jest.fn(),
  getTicketStatus: jest.fn(),
}));

const { submitForm } = require('../src/services/api');

describe('SupportForm', () => {
  beforeEach(() => {
    submitForm.mockReset();
  });

  test('renders all form fields', () => {
    render(<SupportForm />);

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/subject/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty required fields', async () => {
    render(<SupportForm />);

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getAllByRole('alert').length).toBeGreaterThan(0);
    });
  });

  test('validates email format', async () => {
    render(<SupportForm />);

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { name: 'email', value: 'not-an-email' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/valid email/i)).toBeInTheDocument();
    });
  });

  test('validates name minimum length', async () => {
    render(<SupportForm />);

    const nameInput = screen.getByLabelText(/name/i);
    fireEvent.change(nameInput, { target: { name: 'name', value: 'A' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/at least 2/i)).toBeInTheDocument();
    });
  });

  test('submits successfully and shows ticket ID', async () => {
    submitForm.mockResolvedValue({
      ticket_id: 'TKT-0001',
      status: 'received',
      message: 'Support request received',
      created_at: '2026-02-08T00:00:00Z',
    });

    render(<SupportForm />);

    fireEvent.change(screen.getByLabelText(/name/i), { target: { name: 'name', value: 'Lisa Chen' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { name: 'email', value: 'lisa@example.com' } });
    fireEvent.change(screen.getByLabelText(/subject/i), { target: { name: 'subject', value: 'How to set up automations?' } });
    fireEvent.change(screen.getByLabelText(/category/i), { target: { name: 'category', value: 'how_to' } });
    fireEvent.change(screen.getByLabelText(/message/i), { target: { name: 'message', value: 'I need help setting up an automation workflow for my project.' } });

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText('TKT-0001')).toBeInTheDocument();
    });
  });

  test('shows loading state during submission', async () => {
    submitForm.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<SupportForm />);

    fireEvent.change(screen.getByLabelText(/name/i), { target: { name: 'name', value: 'Lisa Chen' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { name: 'email', value: 'lisa@example.com' } });
    fireEvent.change(screen.getByLabelText(/subject/i), { target: { name: 'subject', value: 'How to set up automations?' } });
    fireEvent.change(screen.getByLabelText(/category/i), { target: { name: 'category', value: 'how_to' } });
    fireEvent.change(screen.getByLabelText(/message/i), { target: { name: 'message', value: 'I need help setting up an automation workflow for my project.' } });

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/submitting/i)).toBeInTheDocument();
    });
  });

  test('shows error on submission failure', async () => {
    submitForm.mockRejectedValue(new Error('Server error'));

    render(<SupportForm />);

    fireEvent.change(screen.getByLabelText(/name/i), { target: { name: 'name', value: 'Lisa Chen' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { name: 'email', value: 'lisa@example.com' } });
    fireEvent.change(screen.getByLabelText(/subject/i), { target: { name: 'subject', value: 'How to set up automations?' } });
    fireEvent.change(screen.getByLabelText(/category/i), { target: { name: 'category', value: 'how_to' } });
    fireEvent.change(screen.getByLabelText(/message/i), { target: { name: 'message', value: 'I need help setting up an automation workflow for my project.' } });

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/server error/i)).toBeInTheDocument();
    });
  });
});
