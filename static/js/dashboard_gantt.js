document.addEventListener('DOMContentLoaded', function() {
    const projectData = JSON.parse(document.getElementById('project-data').textContent);
    const ganttTasks = projectData
        .filter(project => project.start_date && project.end_date)
        .map(project => ({
            id: String(project.id),
            name: project.name,
            start: project.start_date,
            end: project.end_date,
            progress: project.status === 'completed' ? 100 : project.status === 'in_progress' ? 50 : 0,
            dependencies: ''
        }));
    if (ganttTasks.length > 0) {
        new Gantt('#gantt', ganttTasks, {
            view_mode: 'Month',
            date_format: 'YYYY-MM-DD'
        });
    } else {
        document.getElementById('gantt').innerHTML = '<p>No projects with valid dates to display.</p>';
    }
});