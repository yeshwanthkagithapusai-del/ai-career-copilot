/**
 * Career progress page script
 * - Loads Chart.js data dynamically
 * - Updates charts when filters change
 * - Shows loading state and error handling
 * - Uses reusable chart utilities
 */

const progressConfig = {
    endpoint: '/progress/data/',
    defaultFilter: 'all',
    metricKeys: [
        'ats_score',
        'interview_score',
        'technical_score',
        'communication_score',
        'roadmap_progress'
    ],
    chartLabels: {
        ats_score: 'Resume ATS Score',
        interview_score: 'Interview Performance',
        technical_score: 'Technical Skills',
        communication_score: 'Communication Skills',
        roadmap_progress: 'Roadmap Progress'
    },
    chartColors: {
        ats_score: '#7C3AED',
        interview_score: '#06B6D4',
        technical_score: '#8B5CF6',
        communication_score: '#10B981',
        roadmap_progress: '#F59E0B'
    }
};

const chartState = {
    instances: {}
};

/**
 * Safe DOM lookup helper
 */
function getById(id) {
    return document.getElementById(id);
}

/**
 * Show a banner message at the top of the page.
 */
function showBanner(message, type = 'info') {
    const banner = getById('progressBanner');
    if (!banner) return;
    banner.textContent = message;
    banner.className = `progress-message visible progress-message-${type}`;
}

/**
 * Hide the top banner.
 */
function hideBanner() {
    const banner = getById('progressBanner');
    if (!banner) return;
    banner.textContent = '';
    banner.className = 'progress-message';
}

/**
 * Toggle the global loading overlay.
 */
function setLoading(visible) {
    const loader = getById('progressLoader');
    if (!loader) return;
    loader.classList.toggle('active', visible);
}

/**
 * Create or update a Chart.js instance.
 */
function createChart(canvasId, config) {
    const canvas = getById(canvasId);
    if (!canvas) return null;

    if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
    }

    const chart = new Chart(canvas, config);
    canvas._chartInstance = chart;
    return chart;
}

/**
 * Build a reusable line chart configuration.
 */
function buildLineConfig(labels, data, label, color) {
    return {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label,
                data,
                fill: true,
                borderColor: color,
                backgroundColor: `${color}22`,
                tension: 0.35,
                pointRadius: 4,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: color,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0',
                        padding: 16
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 30, 0.96)',
                    borderColor: 'rgba(124, 58, 237, 0.25)',
                    borderWidth: 1,
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    padding: 14
                }
            },
            scales: {
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    };
}

/**
 * Convert endpoint records into grouped chart data.
 */
function normalizeProgressData(records) {
    const grouped = {};
    records.forEach((record) => {
        if (!record.metric_type) return;
        if (!grouped[record.metric_type]) {
            grouped[record.metric_type] = { labels: [], values: [] };
        }
        grouped[record.metric_type].labels.push(record.date);
        grouped[record.metric_type].values.push(record.score);
    });
    return grouped;
}

/**
 * Render a single metric card chart or empty state.
 */
function renderMetricCard(metricType, groupedData) {
    const cardId = `${metricType.replace('_score', '')}Card`;
    const canvasId = `${metricType.replace('_score', '')}Chart`;
    const card = getById(cardId);
    const dataset = groupedData[metricType];

    if (!card) return;

    if (!dataset || dataset.values.length === 0) {
        card.querySelector('.chart-shell').innerHTML = `
            <div class="empty-card">
                <i class="fas fa-chart-line"></i>
                <p>No ${progressConfig.chartLabels[metricType]} data available for this time range.</p>
            </div>`;
        return;
    }

    card.querySelector('.chart-shell').innerHTML = `<canvas id="${canvasId}" aria-label="${progressConfig.chartLabels[metricType]}"></canvas>`;
    createChart(canvasId, buildLineConfig(dataset.labels, dataset.values, progressConfig.chartLabels[metricType], progressConfig.chartColors[metricType]));
}

/**
 * Render the overall multi-metric chart.
 */
function renderOverallChart(groupedData) {
    const labels = Object.values(groupedData).reduce((current, group) => {
        return group.labels.length > current.length ? group.labels : current;
    }, []);

    const datasets = Object.keys(groupedData).map((metricType) => ({
        label: progressConfig.chartLabels[metricType] || metricType,
        data: groupedData[metricType].values,
        borderColor: progressConfig.chartColors[metricType] || '#7C3AED',
        backgroundColor: `${progressConfig.chartColors[metricType] || '#7C3AED'}18`,
        fill: false,
        tension: 0.35,
        pointRadius: 3,
        borderWidth: 2
    }));

    if (datasets.length === 0) {
        showBanner('No overall progress data is available for the selected range.', 'info');
        return;
    }

    hideBanner();
    createChart('overallChart', {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'nearest', intersect: false },
            plugins: {
                legend: { labels: { color: '#e2e8f0' } },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 30, 0.96)',
                    borderColor: 'rgba(124, 58, 237, 0.25)',
                    borderWidth: 1,
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    padding: 14
                }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { beginAtZero: true, max: 100, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });
}

/**
 * Render the recent activity timeline.
 */
function renderActivityTimeline(records) {
    const timeline = getById('activityTimeline');
    if (!timeline) return;

    if (!records || records.length === 0) {
        timeline.innerHTML = `
            <div class="empty-card">
                <i class="fas fa-history"></i>
                <p>No recent activity available yet.</p>
            </div>`;
        return;
    }

    const sorted = [...records].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const items = sorted.slice(0, 6).map((record) => `
        <div class="timeline-item">
            <div class="timestamp">${record.date}</div>
            <div class="details">
                <strong>${progressConfig.chartLabels[record.metric_type] || record.metric_type}</strong>
                <small>${record.previous_score !== null && record.previous_score !== undefined ? `Score ${record.previous_score} → ${record.score}` : `Score ${record.score}`}</small>
            </div>
        </div>`);

    timeline.innerHTML = items.join('');
}

/**
 * Handle fetch failures and show fallback content.
 */
function handleFetchError(error) {
    console.error('Career progress fetch failed:', error);
    showBanner('Unable to load progress charts. Please check your connection or try again later.', 'error');

    progressConfig.metricKeys.forEach((metricType) => {
        const cardId = `${metricType.replace('_score', '')}Card`;
        const card = getById(cardId);
        if (!card) return;
        card.querySelector('.chart-shell').innerHTML = `
            <div class="error-card">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Chart unavailable.</p>
            </div>`;
    });

    const overallShell = getById('overallChart')?.closest('.chart-shell');
    if (overallShell) {
        overallShell.innerHTML = `
            <div class="error-card">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Unable to render overall progress.</p>
            </div>`;
    }

    renderActivityTimeline([]);
}

/**
 * Load progress data from the API and draw charts.
 */
function loadProgressData(filter) {
    setLoading(true);
    hideBanner();

    fetch(`${progressConfig.endpoint}?metric=overall&filter=${encodeURIComponent(filter)}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Progress API returned status ${response.status}`);
            }
            return response.json();
        })
        .then((payload) => {
            if (!payload || !Array.isArray(payload.data)) {
                throw new Error('Invalid JSON response from progress endpoint.');
            }

            const groupedData = normalizeProgressData(payload.data);
            renderOverallChart(groupedData);
            progressConfig.metricKeys.forEach((metricType) => renderMetricCard(metricType, groupedData));
            renderActivityTimeline(payload.data);

            if (payload.data.length === 0) {
                showBanner('No progress records found for the selected filter.', 'info');
            }
        })
        .catch(handleFetchError)
        .finally(() => setLoading(false));
}

/**
 * Connect filter buttons to dynamic reload behavior.
 */
function initializeFilters() {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            buttons.forEach((btn) => btn.classList.remove('active'));
            button.classList.add('active');
            loadProgressData(button.dataset.filter || progressConfig.defaultFilter);
        });
    });
}

/**
 * Initialize the page once DOM is ready.
 */
function initializeCareerProgress() {
    if (typeof Chart !== 'function') {
        showBanner('Chart.js has not loaded correctly. Refresh the page to try again.', 'error');
        return;
    }

    initializeFilters();
    loadProgressData(progressConfig.defaultFilter);
}

window.addEventListener('DOMContentLoaded', initializeCareerProgress);
