# LG Asphalt Project Management Platform
A web-based platform for managing residential asphalt projects, including project tracking, customer portals, finance management, and asphalt-specific workflows.

## Week 1 Status (May 7, 2025)
Completed environment setup, authentication, and admin dashboard. Login system is functional with three admin users. Database (`crm.db`) is initialized. Ready for Week 2 customer and project features.

# Week 2 Status Report (May 7, 2025)


## Progress
- **Customer and Project Management Implemented**: Added `add_customer.html` and `add_project.html`, tested adding customers and projects to `crm.db`.  
- **Finance UI Added**: Implemented finance entry form and table in `project.html`, tested adding entries (e.g., Asphalt Materials, $500).  
- **Task Management Added**: Created `add_task.html`, tested adding tasks with assignees, dates, duration, and status.  
- **Gantt Charts Tested**: Added Frappe Gantt to `dashboard.html` for all projects and `project.html` for per-project tasks, tested display with sample data.  
- **Resolved VS Code Errors**: Moved Gantt scripts to external files (`dashboard_gantt.js`, `project_gantt.js`), confirmed functionality and cleared linting issues.  

## Next Steps
- Ready for Week 3: Customer portal and integrations (starting May 15).  

## Notes
- All Week 2 tasks (May 8-14) completed successfully.  
- Ready to proceed with customer portal (`customer_portal.html`) and integrations (Google Calendar, OpenWeatherMap, email notifications).