# TechCorp Suite — Product Documentation

## Product Overview

TechCorp Suite is an all-in-one project management and team collaboration platform. It combines task management, documentation, team messaging, and analytics into a single workspace.

**Current Version**: 4.2.1
**Last Updated**: January 2026

---

## Pricing Tiers

| Feature | Free | Starter ($9/user/mo) | Professional ($29/user/mo) | Enterprise ($79/user/mo) |
|---------|------|----------------------|---------------------------|--------------------------|
| Projects | 3 | 15 | Unlimited | Unlimited |
| Storage | 500 MB | 10 GB | 100 GB | 1 TB |
| Team Members | 5 | 20 | Unlimited | Unlimited |
| TechCorp Docs | Basic | Full | Full + Templates | Full + Templates + API |
| TechCorp Connect | Text only | Text + Voice | Text + Voice + Video | All + Recording |
| TechCorp Analytics | — | Basic dashboards | Advanced + Custom | Advanced + Export + BI |
| Integrations | 3 | 10 | All | All + Custom |
| API Access | — | Read-only | Full | Full + Webhooks |
| SSO/SAML | — | — | Google SSO | Full SAML + SCIM |
| Support | Community | Email (48h) | Email (4h) + Chat | Priority (1h) + Phone |
| Data Retention | 90 days | 1 year | 3 years | Unlimited |
| Audit Log | — | — | 90 days | Unlimited |

> **Note**: All prices are billed annually. Monthly billing adds 20%. All paid plans include a 14-day free trial.

---

## Feature Documentation

### 1. TechCorp Projects

#### Creating a Project

1. Click **+ New Project** from the sidebar
2. Choose a template or start blank:
   - **Kanban** — Best for ongoing work (support, marketing)
   - **Sprint Board** — Best for engineering teams (2-week cycles)
   - **Gantt Chart** — Best for project managers (dependencies, milestones)
   - **List View** — Best for simple task tracking
3. Name your project and invite team members
4. Set project visibility: **Private**, **Team**, or **Public**

#### Task Management

- **Create tasks**: Click "+ Add Task" or press `T` anywhere
- **Assign tasks**: Drag to a team member or use `@mention`
- **Set due dates**: Click the calendar icon or type `/due tomorrow`
- **Add labels**: Color-coded tags for categorization (e.g., Bug, Feature, Urgent)
- **Sub-tasks**: Break large tasks into checkable sub-items
- **Dependencies**: Link tasks with "blocks" or "blocked by" relationships
- **Time tracking**: Click the timer icon to track time spent on any task

#### Sprint Management (Professional+)

1. Go to **Project > Sprints**
2. Click **Create Sprint** — set start/end dates (default: 2 weeks)
3. Drag tasks from the backlog into the sprint
4. During the sprint: track velocity, view burndown chart
5. At sprint end: Review completed vs. remaining, auto-move incomplete tasks

#### Automations

| Trigger | Action | Example |
|---------|--------|---------|
| Task status changes | Send notification | "When task moves to Done, notify channel" |
| Due date approaching | Send reminder | "24 hours before due, remind assignee" |
| New task created | Auto-assign | "Bugs auto-assign to on-call engineer" |
| Label added | Move to board | "When tagged 'Urgent', move to Priority board" |

### 2. TechCorp Docs

#### Creating Documents

1. Navigate to **Docs** in the sidebar
2. Click **+ New Document**
3. Choose a template or start with a blank page
4. Documents support:
   - **Rich text** editing with Markdown shortcuts
   - **Code blocks** with syntax highlighting (50+ languages)
   - **Embedded media** — images, videos, diagrams
   - **Tables** with sorting and formulas
   - **@mentions** to link to team members, tasks, or other docs
   - **Comments and threads** for inline discussion

#### Templates (Professional+)

Pre-built templates include:
- Meeting Notes
- Product Requirements Document (PRD)
- Sprint Retrospective
- Incident Post-Mortem
- API Documentation
- Customer Research Summary

#### Version History

- **Auto-save** every 30 seconds
- **Version history** shows all edits with author attribution
- **Restore** any previous version with one click
- **Compare** two versions side-by-side (Professional+)

### 3. TechCorp Connect

#### Messaging

- **Channels**: Public and private channels for team communication
- **Direct Messages**: 1:1 or group conversations
- **Threads**: Reply to any message in a thread to keep discussions organized
- **Reactions**: Emoji reactions on any message
- **File Sharing**: Drag and drop files up to 100 MB
- **Search**: Full-text search across all messages and files

#### Video Calls (Starter+)

- **Start a call**: Click the phone icon in any channel or DM
- **Screen sharing**: Share your entire screen or a specific window
- **Recording**: Record calls and auto-generate transcripts (Enterprise)
- **Maximum participants**: Starter: 10, Professional: 50, Enterprise: 200

### 4. TechCorp Analytics (Starter+)

#### Built-in Dashboards

| Dashboard | Available On | Description |
|-----------|-------------|-------------|
| Project Overview | Starter+ | Tasks by status, assignee, label |
| Sprint Velocity | Professional+ | Story points completed per sprint |
| Burndown Chart | Professional+ | Sprint progress over time |
| Team Workload | Professional+ | Task distribution across team |
| Time Report | Professional+ | Hours logged per project/person |
| Custom Dashboard | Enterprise | Build your own with widgets |

#### Exporting Data (Enterprise)

- Export to CSV, JSON, or PDF
- Schedule recurring exports (daily, weekly, monthly)
- Connect to BI tools via API (Tableau, Power BI, Looker)

---

## Technical Specifications

### System Requirements

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| **Web Browser** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ | Latest version |
| **Desktop App** | Windows 10+, macOS 11+, Ubuntu 20.04+ | Latest OS |
| **Mobile App** | iOS 15+, Android 11+ | Latest OS |
| **Network** | 1 Mbps | 5 Mbps+ for video calls |

### API Overview

- **Base URL**: `https://api.techcorp.io/v2`
- **Authentication**: Bearer token (OAuth 2.0)
- **Rate Limits**: Starter: 100 req/min, Professional: 500 req/min, Enterprise: 2000 req/min
- **Webhooks**: Enterprise plan only — configure via Settings > Integrations > Webhooks

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects` | GET/POST | List or create projects |
| `/projects/{id}/tasks` | GET/POST | List or create tasks |
| `/tasks/{id}` | GET/PATCH/DELETE | Manage individual tasks |
| `/docs` | GET/POST | List or create documents |
| `/users/me` | GET | Current user profile |
| `/search` | POST | Full-text search across resources |

### Integrations

| Integration | Setup | Sync |
|-------------|-------|------|
| **Slack** | OAuth — Settings > Integrations | Bi-directional notifications |
| **GitHub** | OAuth — link repos to projects | Auto-create tasks from PRs/issues |
| **GitLab** | OAuth — link repos to projects | Auto-create tasks from MRs/issues |
| **Jira** | Import — one-time migration tool | One-way import |
| **Google Workspace** | OAuth — calendar + docs sync | Bi-directional |
| **Microsoft 365** | OAuth — calendar + Teams sync | Bi-directional |
| **Zapier** | API key | 500+ app connections |

---

## Frequently Asked Questions (FAQ)

### Account & Access

**Q: How do I reset my password?**
A: Click "Forgot Password" on the login page, enter your registered email, and follow the link sent to your inbox. The link expires in 1 hour. If you don't receive it, check your spam folder or contact support.

**Q: How do I enable two-factor authentication (2FA)?**
A: Go to Settings > Security > Two-Factor Authentication. You can use an authenticator app (Google Authenticator, Authy) or SMS verification. We recommend the authenticator app for better security.

**Q: Can I change my email address?**
A: Yes. Go to Settings > Account > Email. Enter your new email and confirm via the verification link. Your old email will receive a notification. If you're using SSO, contact your organization's admin.

**Q: How do I delete my account?**
A: Go to Settings > Account > Danger Zone > Delete Account. This action is irreversible. All your personal data will be removed within 30 days. Shared projects and documents will be reassigned to your team's admin.

**Q: I'm locked out of my account. What do I do?**
A: Try the password reset flow first. If your account is locked due to too many failed attempts, it auto-unlocks after 30 minutes. If you still can't access your account, contact support with your registered email — we'll verify your identity and restore access.

### Billing

**Q: How do I upgrade my plan?**
A: Go to Settings > Billing > Change Plan. Select your new tier and confirm. Upgrades take effect immediately. You'll be charged a prorated amount for the remainder of the billing cycle.

**Q: How do I cancel my subscription?**
A: Go to Settings > Billing > Cancel Subscription. Your workspace remains active until the end of the current billing period. After that, it downgrades to the Free plan (3 projects, 5 members, 500 MB storage).

**Q: Do you offer refunds?**
A: We offer a full refund within 14 days of initial purchase or upgrade. After 14 days, we do not offer refunds but you can cancel anytime. Contact our billing team for refund requests — the AI agent cannot process refunds.

**Q: Do you offer discounts for nonprofits or education?**
A: Yes! Nonprofits get 50% off any paid plan. Educational institutions (.edu) get Professional plan features at Starter pricing. Contact sales@techcorp.io with verification.

**Q: What payment methods do you accept?**
A: We accept Visa, Mastercard, American Express, and PayPal. Enterprise customers can pay via invoice (NET 30). We do not accept wire transfers for Starter or Professional plans.

### Features & Usage

**Q: What's the maximum file upload size?**
A: Free: 25 MB per file, Starter: 50 MB, Professional: 100 MB, Enterprise: 500 MB. For larger files, use our cloud storage integration (Google Drive, Dropbox, OneDrive).

**Q: Can I import projects from other tools?**
A: Yes! We support CSV import and direct import from Jira, Asana, Trello, and Monday.com. Go to Settings > Import Data. The import tool maps fields automatically and lets you review before confirming.

**Q: How many projects can I archive?**
A: Archived projects don't count toward your project limit. You can archive unlimited projects on any plan. Archived projects remain searchable and can be restored at any time.

**Q: Does TechCorp work offline?**
A: The desktop app supports limited offline mode. You can view and edit tasks and documents. Changes sync automatically when you reconnect. Video calls and messaging require an internet connection.

**Q: Can I customize the workspace branding?**
A: Enterprise plan includes custom branding: your logo, brand colors, custom domain (yourcompany.techcorp.io), and custom email templates.

---

## Troubleshooting Guide

### Common Issues

#### "Unable to connect" error
**Symptoms**: App shows "Unable to connect to TechCorp servers"
**Causes**: Network issues, firewall blocking, or service outage
**Solution**:
1. Check your internet connection
2. Visit status.techcorp.io for service status
3. Ensure your firewall allows traffic to `*.techcorp.io` on ports 443 and 8443
4. Clear browser cache and cookies
5. Try a different browser or incognito mode
6. If the issue persists, contact support with your browser version and network info

#### Slow performance
**Symptoms**: Pages take more than 3 seconds to load, actions feel sluggish
**Causes**: Large project data, browser extensions, outdated browser
**Solution**:
1. Disable browser extensions (especially ad blockers) and test again
2. Clear browser cache (Settings > Clear Browsing Data)
3. Archive old projects with 1000+ tasks
4. Update your browser to the latest version
5. Check if other tabs or apps are consuming excessive memory

#### Tasks not syncing
**Symptoms**: Changes made on one device don't appear on another
**Causes**: Sync conflict, network latency, cache issue
**Solution**:
1. Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac) to hard refresh
2. Log out and log back in
3. Check if you have multiple browser tabs open — close extras
4. Verify you're viewing the same project and sprint

#### Email notifications not arriving
**Symptoms**: Not receiving email notifications for mentions, assignments, or updates
**Solution**:
1. Check Settings > Notifications — ensure email notifications are enabled
2. Check your spam/junk folder
3. Add `notifications@techcorp.io` to your email safe senders list
4. Verify your email address is confirmed (Settings > Account)

#### Integration not working
**Symptoms**: GitHub/Slack/Google integration stopped syncing
**Solution**:
1. Go to Settings > Integrations
2. Click "Reconnect" next to the affected integration
3. Re-authorize with the third-party service
4. If the issue persists, disconnect and reconnect the integration
5. Check the integration's webhook status in Settings > Integrations > Logs

#### Can't upload files
**Symptoms**: File upload fails or hangs
**Solution**:
1. Check file size against your plan's limit (see FAQ above)
2. Ensure the file format is supported (we block `.exe`, `.bat`, `.sh` for security)
3. Try a different browser
4. If uploading many files, upload them one at a time
5. Check your storage usage in Settings > Billing > Usage

### Data & Security

#### How is my data protected?
- **Encryption at rest**: AES-256
- **Encryption in transit**: TLS 1.3
- **Data centers**: AWS US (us-east-1) and EU (eu-west-1)
- **Backups**: Automated daily backups with 30-day retention
- **Compliance**: SOC 2 Type II, GDPR compliant
- **Data residency**: Enterprise customers can choose US or EU data center

#### How do I export my data?
Go to Settings > Account > Export Data. You'll receive a ZIP file containing:
- All projects (JSON format)
- All documents (Markdown format)
- All messages (JSON format)
- All files and attachments
- User data (CSV format)

Export processing takes 1-24 hours depending on data volume. You'll receive an email when it's ready.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `T` | Create new task |
| `D` | Create new document |
| `/` | Open command palette |
| `Ctrl+K` / `Cmd+K` | Quick search |
| `Ctrl+Enter` | Submit/save current form |
| `Esc` | Close modal or panel |
| `G then P` | Go to Projects |
| `G then D` | Go to Docs |
| `G then M` | Go to Messages |
| `?` | Show all shortcuts |

---

## Status Page

Check real-time service status at: **status.techcorp.io**

### Incident Communication
- **Active incidents**: Posted on status page within 5 minutes
- **Updates**: Every 30 minutes during incidents
- **Post-mortems**: Published within 48 hours of resolution
- **Subscribe**: Get email/SMS alerts for your region
