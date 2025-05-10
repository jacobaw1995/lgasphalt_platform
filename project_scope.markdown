# LG Asphalt Project Management Platform Scope

## Project Overview
- **Company Name**: LG Asphalt
- **Website**: [www.lgasphalt.com](http://www.lgasphalt.com)
- **Goal**: Develop a free, web-based project management platform integrated into the LG Asphalt website with:
  - **Backend Access**: “PM” button for admin users (initially three users with full access), extensible for adding users with permissions.
  - **Customer Access**: “Track My Project” button for clients to view project details, schedules, updates, and photos.
  - **Objective**: Streamline project management, finance tracking, customer communication, and asphalt-specific workflows using free tools, with a modular design for future scalability.

## Branding
- **Logo Colors**: Black (#000000), Yellow (#FFC107).
- **UI Colors**:
  - Primary: Black (#000000) for text and backgrounds.
  - Secondary: Yellow (#FFC107) for highlights, buttons, accents.
  - Background: Light gray (#F5F5F5).
  - Text: Dark gray (#333333).

## Critical Workflows
1. **Project Management**:
   - Track projects (site survey to completion).
   - Gantt charts: “All Projects” and per-project task views.
   - Task assignments, statuses, scheduling.
2. **Forms**:
   - Standardized forms for estimates and site inspections (fields TBD).
3. **Customer Management**:
   - Store customer details, provide customer portal for updates.
4. **Project-Specific Finance Management**:
   - Track costs: Asphalt Materials, Labor Costs (daily rate), Equipment Rental, Fuel Cost, Hand Tools/Tools, Dump (gravel, old asphalt, dirt, etc.).
   - Track revenue: Client Payments (pre-QuickBooks).
   - User-friendly interface for entries and summaries (total costs, revenue, profit).
5. **Customer Updates**:
   - Email notifications via Gmail SMTP (no SMS).
   - Scheduler Mode: Toggle to schedule privately; toggle off to send updates.
   - Photo uploads for job progress, visible to customers.
6. **Asphalt-Specific Features**:
   - Material tracking (asphalt type, quantity, thickness).
   - Equipment management (pavers, rollers, maintenance schedules).
   - Weather integration (OpenWeatherMap API) for schedules.
   - Photo uploads for job site progress.

## User Requirements
- **Initial Users**: Three admin users (full access).
- **Future Users**: Add users via admin portal with customizable permissions (e.g., “task editor,” “finance manager”).
- **Customer Users**: Clients log in to customer portal.
- **Access Points**:
  - Backend: “PM” button on website.
  - Customer: “Track My Project” button.

## Integrations
- **Google Calendar**: Sync schedules (using `jacobaw1995@gmail.com`).
- **QuickBooks**: No integration; finance tracking in-app, extensible for future.
- **Weather API**: OpenWeatherMap (free) for forecasts.
- **Email Notifications**: Gmail SMTP for updates.

## Technical Approach
- **Framework**: Flask (Python) for modular backend.
- **Database**: SQLite (tables: users, customers, projects, tasks, equipment, photos, forms, project_finances).
- **Frontend**: Bootstrap, Frappe Gantt for Gantt charts, LG Asphalt branding.
- **Authentication**: Flask-Login with role-based permissions.
- **Finance Management**: `project_finances` table, UI for costs/revenue.
- **Notifications**: Gmail SMTP with Scheduler Mode toggle.
- **Photo Uploads**: Local storage (extensible to Cloudinary free tier).
- **Weather**: OpenWeatherMap API (free).
- **Google Calendar**: Google Calendar API (free).
- **Deployment**: Local server, deployable to Render/Heroku (free tiers).
- **Security**: Flask-Login, bcrypt, CSRF protection, environment variables.

## Constraints
- **Budget**: Free tools only.
- **Timeline**: Functional app by May 31, 2025.
- **Ease of Use**: Clear setup/management instructions.
- **Extensibility**: Modular design for future features (e.g., SMS, QuickBooks).

## Timeline (for Trello)
### Week 1: Setup and Authentication (May 1-7, 2025)
- **May 1**: Set up environment (Python 3.9+, Git, code editor; create directory).
- **May 2**: Install dependencies, test `app.py` (`pip install flask flask-login bcrypt python-dotenv requests`).
- **May 3**: Run `init_db.py`, confirm database (`crm.db`) created.
- **May 4**: Add initial admin users, test login.
- **May 5**: Add `login.html`, test login.
- **May 6**: Test `dashboard.html`.
- **May 7**: Report status to Controller.

### Week 2: Core Features (May 8-14, 2025)
- **May 8**: Add `add_customer.html`, test adding customer.
- **May 9**: Add `add_project.html`, test adding project.
- **May 10**: Add `project.html`, test project details.
- **May 11**: Add finance management UI to `project.html`, test finance entry.
- **May 12**: Add task management routes/templates, test adding tasks.
- **May 13**: Add Frappe Gantt to `dashboard.html`, test “All Projects” chart.
- **May 14**: Add Frappe Gantt to `project.html`, test per-project chart.

### Week 3: Customer Portal and Integrations (May 15-21, 2025)
- **May 15**: Add `customer_portal.html`, test customer login/view.
- **May 16**: Add photo upload routes/template, test upload.
- **May 17**: Set up Google Calendar API, test syncing.
- **May 18**: Add OpenWeatherMap API, test weather display.
- **May 19**: Add Scheduler Mode and email notifications, test email.
- **May 20**: Add equipment management routes/template, test equipment.
- **May 21**: Review progress, report to Controller.

### Week 4: Forms and Polish (May 22-28, 2025)
- **May 22**: Add placeholder form templates (estimates, site inspections).
- **May 23**: Add user management routes/template, test adding user.
- **May 24**: Apply LG Asphalt branding to all templates.
- **May 25**: Test project management (projects, tasks, finances, equipment).
- **May 26**: Test customer portal (login, project view, photos, emails).
- **May 27**: Test integrations (Google Calendar, weather).
- **May 28**: Finalize setup instructions (README.md).

### Week 5: Testing and Deployment (May 29-31, 2025)
- **May 29**: Full app testing, note bugs.
- **May 30**: Deploy to Render/Heroku.
- **May 31**: Final review, launch, report to Controller.