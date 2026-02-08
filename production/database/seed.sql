-- =============================================================================
-- CRM Digital FTE — Seed Data
-- =============================================================================

-- Channel Configurations
INSERT INTO channel_configs (channel, is_enabled, max_response_length, tone, response_template, api_config_ref)
VALUES
('email', TRUE, 500, 'formal',
 E'Hi {{customer_name}},\n\n{{response_body}}\n\nBest regards,\nTechCorp Support Team\nsupport@techcorp.io | status.techcorp.io',
 'GMAIL_'),
('whatsapp', TRUE, 1600, 'conversational',
 '{{response_body}}',
 'TWILIO_'),
('web_form', TRUE, 300, 'semi-formal',
 E'Hi {{customer_name}},\n\n{{response_body}}\n\nYour ticket reference: {{ticket_number}}\nTrack your ticket at support.techcorp.io',
 NULL)
ON CONFLICT (channel) DO NOTHING;

-- Sample Knowledge Base entries (from product-docs.md)
INSERT INTO knowledge_base (title, content, category, source) VALUES
('Password Reset', 'To reset your password: 1) Go to techcorp.io/login 2) Click "Forgot Password" 3) Enter your email address 4) Check your inbox for a reset link (may take up to 5 minutes) 5) Click the link and set a new password. If you don''t receive the email, check your spam folder or contact support.', 'faq', 'product-docs'),
('Two-Factor Authentication Setup', 'To enable 2FA: 1) Go to Settings > Security 2) Click "Enable Two-Factor Authentication" 3) Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.) 4) Enter the 6-digit code to verify 5) Save your backup codes in a secure location. 2FA is available on Starter plans and above.', 'faq', 'product-docs'),
('API Rate Limits', 'TechCorp API rate limits by plan: Free: 100 requests/hour, Starter: 1,000 requests/hour, Professional: 10,000 requests/hour, Enterprise: 100,000 requests/hour. Rate limit headers are included in every response: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset.', 'feature', 'product-docs'),
('Data Export', 'To export your data: 1) Go to Settings > Data Management 2) Click "Export Data" 3) Select the data types (projects, contacts, files) 4) Choose format (CSV or JSON) 5) Click "Start Export" — you''ll receive an email with a download link within 24 hours. Available on Professional and Enterprise plans.', 'feature', 'product-docs'),
('Automation Setup', 'To create an automation: 1) Go to Automations in the sidebar 2) Click "New Automation" 3) Choose a trigger (new task, status change, due date, etc.) 4) Add actions (send notification, update field, create task, etc.) 5) Set conditions if needed 6) Save and enable. Available on Starter plans and above. Slack integration requires connecting your Slack workspace in Settings > Integrations.', 'feature', 'product-docs'),
('Account Access Troubleshooting', 'If you cannot access your account: 1) Clear browser cache and cookies 2) Try a different browser 3) Check if your IP is blocked (VPN users may need to whitelist) 4) Verify your account is active at techcorp.io/account-status 5) If locked out after multiple failed attempts, wait 30 minutes or use password reset. Enterprise accounts can contact their admin for SSO issues.', 'troubleshooting', 'product-docs'),
('Billing and Invoices', 'View invoices at Settings > Billing > Invoice History. Invoices are generated on the 1st of each month. Payment methods: credit card, ACH (US only), wire transfer (Enterprise). For billing questions, plan changes, or refund requests, please contact our billing team — our AI agent will connect you with the right person.', 'billing', 'product-docs'),
('Team Collaboration Features', 'TechCorp team features: Shared workspaces, real-time collaboration, @mentions, task assignments, activity feeds, and team dashboards. Free: up to 3 team members, Starter: up to 10, Professional: up to 50, Enterprise: unlimited. Invite team members from Settings > Team > Invite.', 'feature', 'product-docs'),
('File Storage and Sharing', 'TechCorp file storage limits: Free: 1 GB, Starter: 10 GB, Professional: 100 GB, Enterprise: 1 TB. Supported file types: images, documents, spreadsheets, PDFs, and archives. Share files with team members or external guests using share links with optional password protection.', 'feature', 'product-docs'),
('Integration Directory', 'TechCorp integrates with: Slack (notifications), Google Workspace (calendar, docs), Microsoft 365, Zapier (1000+ apps), GitHub, Jira, and Salesforce. Setup: Settings > Integrations > select integration > follow OAuth flow. Custom integrations available via REST API on Professional and Enterprise plans.', 'feature', 'product-docs')
ON CONFLICT DO NOTHING;
