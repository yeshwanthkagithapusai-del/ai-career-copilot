/* ===== Dashboard JavaScript ===== */

document.addEventListener('DOMContentLoaded', function() {
    // Fetch progress data and render chart
    fetch('/progress/data/?metric=overall&filter=all')
        .then(response => response.json())
        .then(data => {
            if (data.data && data.data.length > 0) {
                renderProgressChart(data.data);
            }
        })
        .catch(err => console.error('Error fetching progress:', err));
});

function renderProgressChart(data) {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    // Group by metric type
    const metrics = {};
    data.forEach(function(item) {
        if (!metrics[item.metric_type]) {
            metrics[item.metric_type] = { labels: [], scores: [] };
        }
        metrics[item.metric_type].labels.push(item.date);
        metrics[item.metric_type].scores.push(item.score);
    });
    
    const colors = {
        'ats_score': '#7C3AED',
        'test_score': '#2563EB',
        'interview_score': '#06B6D4',
        'technical_score': '#8B5CF6',
        'communication_score': '#10B981',
        'roadmap_progress': '#F59E0B',
    };
    
    const labels = {};
    const datasets = [];
    
    Object.keys(metrics).forEach(function(key) {
        const color = colors[key] || '#8B5CF6';
        const labelMap = {
            'ats_score': 'Resume ATS Score',
            'test_score': 'Test Score',
            'interview_score': 'Interview Score',
            'technical_score': 'Technical Score',
            'communication_score': 'Communication Score',
            'roadmap_progress': 'Roadmap Progress',
        };
        
        datasets.push({
            label: labelMap[key] || key,
            data: metrics[key].scores,
            borderColor: color,
            backgroundColor: color + '20',
            fill: true,
            tension: 0.4,
            pointRadius: 5,
            pointHoverRadius: 8,
            pointBackgroundColor: color,
            pointBorderColor: '#050816',
            pointBorderWidth: 2,
        });
    });
    
    // Use the longest label set
    let longestLabels = [];
    Object.values(metrics).forEach(function(m) {
        if (m.labels.length > longestLabels.length) {
            longestLabels = m.labels;
        }
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: longestLabels,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94A3B8', font: { size: 12, family: 'Inter' } },
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 16, 32, 0.95)',
                    borderColor: 'rgba(139, 92, 246, 0.3)',
                    borderWidth: 1,
                    titleColor: '#F1F5F9',
                    bodyColor: '#94A3B8',
                    padding: 12,
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(139, 92, 246, 0.1)' },
                    ticks: { color: '#64748B', font: { family: 'Inter' } },
                },
                x: {
                    grid: { color: 'rgba(139, 92, 246, 0.1)' },
                    ticks: { color: '#64748B', font: { family: 'Inter' } },
                },
            },
        },
    });
}
