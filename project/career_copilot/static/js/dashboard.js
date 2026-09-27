/* ===== Career Intelligence Dashboard JavaScript ===== */

document.addEventListener('DOMContentLoaded', function() {
    // Check for skill gap data
    const scriptTag = document.getElementById('skillGapsData');
    if (scriptTag) {
        try {
            const data = JSON.parse(scriptTag.textContent);
            if (data && data.length > 0) {
                renderSkillGapChart(data);
            }
        } catch (e) {
            console.error("Error parsing chart data:", e);
        }
    }
});

function renderSkillGapChart(data) {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    const labels = data.map(item => item.skill_name);
    const currentData = data.map(item => item.current_proficiency !== null ? item.current_proficiency : null);
    const requiredData = data.map(item => item.required_proficiency !== null ? item.required_proficiency : null);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Proficiency',
                    data: currentData,
                    backgroundColor: 'rgba(139, 92, 246, 0.7)',
                    borderColor: '#8B5CF6',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Required Proficiency',
                    data: requiredData,
                    backgroundColor: 'rgba(74, 222, 128, 0.2)',
                    borderColor: '#4ade80',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94A3B8', font: { size: 12, family: 'Inter' } },
                    position: 'top',
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 16, 32, 0.95)',
                    borderColor: 'rgba(139, 92, 246, 0.3)',
                    borderWidth: 1,
                    titleColor: '#F1F5F9',
                    bodyColor: '#94A3B8',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                            } else {
                                label += 'No data/evidence';
                            }
                            return label;
                        }
                    }
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748B', font: { family: 'Inter' } },
                    title: {
                        display: true,
                        text: 'Proficiency Score',
                        color: '#64748B'
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94A3B8', font: { family: 'Inter', size: 11 } },
                },
            },
        }
    });
}
