document.addEventListener('DOMContentLoaded', function() {
    const tasksData = JSON.parse(document.getElementById('tasks-data').textContent);
    const ganttTasks = tasksData
        .filter(task => task.start_date && task.due_date)
        .map(task => ({
            id: String(task.id),
            name: task.title,
            start: task.start_date,
            end: task.due_date,
            progress: task.status === 'completed' ? 100 : task.status === 'in_progress' ? 50 : 0,
            dependencies: ''
        }));
    if (ganttTasks.length > 0) {
        new Gantt('#task-gantt', ganttTasks, {
            view_mode: 'Day',
            date_format: 'YYYY-MM-DD'
        });
    } else {
        document.getElementById('task-gantt').innerHTML = '<p>No tasks with valid dates to display.</p>';
    }
});