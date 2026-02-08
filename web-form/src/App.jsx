/**
 * App entry point — renders SupportForm and StatusChecker.
 */
import React from 'react';
import SupportForm from './components/SupportForm';
import StatusChecker from './components/StatusChecker';

export default function App() {
  return (
    <div style={{ maxWidth: '700px', margin: '40px auto', padding: '0 20px', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      <header style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700 }}>TechCorp Support</h1>
        <p style={{ color: '#718096' }}>24/7 AI-powered customer support</p>
      </header>

      <section style={{ marginBottom: '32px' }}>
        <SupportForm />
      </section>

      <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '32px 0' }} />

      <section>
        <StatusChecker />
      </section>
    </div>
  );
}
