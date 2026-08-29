/**
 * Gamerock Welfare - Reports Charts
 * Offline-capable SVG charting library with interactive features
 */

const ReportsCharts = (function() {
    'use strict';

    const colors = {
        primary: '#667eea',
        primaryDark: '#764ba2',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
        purple: '#8b5cf6',
        pink: '#ec4899',
        teal: '#14b8a6',
        slate: '#64748b'
    };

    const colorPalette = [
        colors.primary, colors.success, colors.warning, colors.danger,
        colors.info, colors.purple, colors.pink, colors.teal, colors.slate
    ];

    function formatCurrency(value) {
        return 'Ksh. ' + value.toLocaleString('en-KE');
    }

    function createSVGElement(tag, attrs) {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
        return el;
    }

    function clearContainer(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }

    /**
     * Create a bar chart with animations and tooltips
     */
    function createBarChart(containerId, data, options = {}) {
        clearContainer(containerId);
        const container = document.getElementById(containerId);
        if (!container) return;

        const labels = Object.keys(data);
        const values = Object.values(data);
        const maxValue = Math.max(...values, 1);
        const chartHeight = options.height || 300;
        const chartWidth = options.width || container.clientWidth || 600;
        const padding = { top: 40, right: 20, bottom: 80, left: 60 };
        const barWidth = Math.max(20, (chartWidth - padding.left - padding.right) / labels.length * 0.7);
        const barGap = (chartWidth - padding.left - padding.right) / labels.length * 0.3;

        const svg = createSVGElement('svg', {
            width: '100%',
            height: chartHeight,
            viewBox: `0 0 ${chartWidth} ${chartHeight}`,
            preserveAspectRatio: 'xMidYMid meet'
        });

        // Add gradient definitions
        const defs = createSVGElement('defs', {});
        const gradient = createSVGElement('linearGradient', {
            id: `barGradient-${containerId}`,
            x1: '0%',
            y1: '0%',
            x2: '0%',
            y2: '100%'
        });
        const stop1 = createSVGElement('stop', { offset: '0%', 'stop-color': colors.primary, 'stop-opacity': '0.9' });
        const stop2 = createSVGElement('stop', { offset: '100%', 'stop-color': colors.primaryDark, 'stop-opacity': '0.7' });
        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.appendChild(defs);

        // Draw grid lines
        const gridGroup = createSVGElement('g', { class: 'chart-grid' });
        const gridLines = 5;
        for (let i = 0; i <= gridLines; i++) {
            const y = padding.top + (chartHeight - padding.top - padding.bottom) * (i / gridLines);
            const line = createSVGElement('line', {
                x1: padding.left,
                y1: y,
                x2: chartWidth - padding.right,
                y2: y,
                stroke: '#e2e8f0',
                'stroke-width': '1',
                'stroke-dasharray': '4,4',
                'opacity': '0.5'
            });
            gridGroup.appendChild(line);

            // Y-axis labels
            const value = maxValue - (maxValue * i / gridLines);
            const text = createSVGElement('text', {
                x: padding.left - 10,
                y: y + 4,
                'text-anchor': 'end',
                'font-size': '11',
                'fill': '#64748b',
                'font-weight': '500'
            });
            text.textContent = formatCurrency(Math.round(value));
            gridGroup.appendChild(text);
        }
        svg.appendChild(gridGroup);

        // Draw bars
        const barsGroup = createSVGElement('g', { class: 'chart-bars' });
        labels.forEach((label, index) => {
            const barHeight = (values[index] / maxValue) * (chartHeight - padding.top - padding.bottom);
            const x = padding.left + index * ((chartWidth - padding.left - padding.right) / labels.length) + barGap / 2;
            const y = chartHeight - padding.bottom - barHeight;

            const bar = createSVGElement('rect', {
                x: x,
                y: chartHeight - padding.bottom,
                width: barWidth,
                height: 0,
                fill: `url(#barGradient-${containerId})`,
                rx: '6',
                ry: '6',
                class: 'chart-bar',
                'data-value': values[index],
                'data-label': label,
                style: 'cursor: pointer; transition: all 0.3s ease;'
            });

            // Animate bar
            setTimeout(() => {
                bar.setAttribute('y', y);
                bar.setAttribute('height', barHeight);
            }, index * 50);

            // Hover effects
            bar.addEventListener('mouseenter', function(e) {
                this.setAttribute('fill', colors.primary);
                this.setAttribute('filter', 'brightness(1.1)');
                showTooltip(e, `${label}: ${formatCurrency(values[index])}`);
            });

            bar.addEventListener('mouseleave', function() {
                this.setAttribute('fill', `url(#barGradient-${containerId})`);
                this.removeAttribute('filter');
                hideTooltip();
            });

            barsGroup.appendChild(bar);

            // X-axis labels
            const labelText = createSVGElement('text', {
                x: x + barWidth / 2,
                y: chartHeight - padding.bottom + 20,
                'text-anchor': 'middle',
                'font-size': '10',
                'fill': '#64748b',
                'font-weight': '500',
                transform: `rotate(-15, ${x + barWidth / 2}, ${chartHeight - padding.bottom + 20})`
            });
            labelText.textContent = label.length > 10 ? label.substring(0, 10) + '...' : label;
            barsGroup.appendChild(labelText);
        });

        svg.appendChild(barsGroup);
        container.appendChild(svg);

        // Add tooltip element
        if (!document.getElementById('chart-tooltip')) {
            const tooltip = document.createElement('div');
            tooltip.id = 'chart-tooltip';
            tooltip.className = 'chart-tooltip';
            tooltip.style.cssText = `
                position: fixed;
                padding: 8px 12px;
                background: rgba(15, 23, 42, 0.95);
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                pointer-events: none;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: none;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            `;
            document.body.appendChild(tooltip);
        }
    }

    /**
     * Create a line chart for time series data
     */
    function createLineChart(containerId, data, options = {}) {
        clearContainer(containerId);
        const container = document.getElementById(containerId);
        if (!container) return;

        const labels = Object.keys(data);
        const values = Object.values(data);
        const maxValue = Math.max(...values, 1);
        const chartHeight = options.height || 300;
        const chartWidth = options.width || container.clientWidth || 600;
        const padding = { top: 40, right: 20, bottom: 60, left: 60 };

        const svg = createSVGElement('svg', {
            width: '100%',
            height: chartHeight,
            viewBox: `0 0 ${chartWidth} ${chartHeight}`,
            preserveAspectRatio: 'xMidYMid meet'
        });

        // Add gradient for area under line
        const defs = createSVGElement('defs', {});
        const areaGradient = createSVGElement('linearGradient', {
            id: `areaGradient-${containerId}`,
            x1: '0%',
            y1: '0%',
            x2: '0%',
            y2: '100%'
        });
        const stop1 = createSVGElement('stop', { offset: '0%', 'stop-color': colors.primary, 'stop-opacity': '0.3' });
        const stop2 = createSVGElement('stop', { offset: '100%', 'stop-color': colors.primary, 'stop-opacity': '0.05' });
        areaGradient.appendChild(stop1);
        areaGradient.appendChild(stop2);
        defs.appendChild(areaGradient);
        svg.appendChild(defs);

        // Grid
        const gridGroup = createSVGElement('g', { class: 'chart-grid' });
        const gridLines = 5;
        for (let i = 0; i <= gridLines; i++) {
            const y = padding.top + (chartHeight - padding.top - padding.bottom) * (i / gridLines);
            const line = createSVGElement('line', {
                x1: padding.left,
                y1: y,
                x2: chartWidth - padding.right,
                y2: y,
                stroke: '#e2e8f0',
                'stroke-width': '1',
                'stroke-dasharray': '4,4',
                'opacity': '0.5'
            });
            gridGroup.appendChild(line);

            const value = maxValue - (maxValue * i / gridLines);
            const text = createSVGElement('text', {
                x: padding.left - 10,
                y: y + 4,
                'text-anchor': 'end',
                'font-size': '11',
                'fill': '#64748b',
                'font-weight': '500'
            });
            text.textContent = formatCurrency(Math.round(value));
            gridGroup.appendChild(text);
        }
        svg.appendChild(gridGroup);

        if (labels.length === 0) {
            const noData = createSVGElement('text', {
                x: chartWidth / 2,
                y: chartHeight / 2,
                'text-anchor': 'middle',
                'font-size': '14',
                'fill': '#94a3b8'
            });
            noData.textContent = 'No data available';
            svg.appendChild(noData);
            container.appendChild(svg);
            return;
        }

        const points = labels.map((label, index) => {
            const x = padding.left + (index / (labels.length - 1 || 1)) * (chartWidth - padding.left - padding.right);
            const y = chartHeight - padding.bottom - (values[index] / maxValue) * (chartHeight - padding.top - padding.bottom);
            return { x, y, label, value: values[index] };
        });

        // Area under line
        const areaPath = createSVGElement('path', {
            d: `M ${points[0].x} ${chartHeight - padding.bottom} ` +
               points.map(p => `L ${p.x} ${p.y}`).join(' ') +
               ` L ${points[points.length - 1].x} ${chartHeight - padding.bottom} Z`,
            fill: `url(#areaGradient-${containerId})`,
            stroke: 'none'
        });
        svg.appendChild(areaPath);

        // Line path
        const linePath = createSVGElement('path', {
            d: 'M ' + points.map(p => `${p.x} ${p.y}`).join(' L '),
            fill: 'none',
            stroke: colors.primary,
            'stroke-width': '3',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round',
            'stroke-dasharray': '1000',
            'stroke-dashoffset': '1000'
        });

        // Animate line
        setTimeout(() => {
            linePath.style.transition = 'stroke-dashoffset 1.5s ease-out';
            linePath.setAttribute('stroke-dashoffset', '0');
        }, 100);
        svg.appendChild(linePath);

        // Data points
        const pointsGroup = createSVGElement('g', { class: 'chart-points' });
        points.forEach((point, index) => {
            const circle = createSVGElement('circle', {
                cx: point.x,
                cy: point.y,
                r: 6,
                fill: 'white',
                stroke: colors.primary,
                'stroke-width': '3',
                style: 'cursor: pointer; transition: all 0.2s ease;'
            });

            circle.addEventListener('mouseenter', function(e) {
                this.setAttribute('r', 9);
                this.setAttribute('fill', colors.primary);
                showTooltip(e, `${point.label}: ${formatCurrency(point.value)}`);
            });

            circle.addEventListener('mouseleave', function() {
                this.setAttribute('r', 6);
                this.setAttribute('fill', 'white');
                hideTooltip();
            });

            pointsGroup.appendChild(circle);

            // X-axis labels
            if (index % Math.ceil(labels.length / 6) === 0) {
                const labelText = createSVGElement('text', {
                    x: point.x,
                    y: chartHeight - padding.bottom + 20,
                    'text-anchor': 'middle',
                    'font-size': '10',
                    'fill': '#64748b',
                    'font-weight': '500'
                });
                labelText.textContent = point.label;
                pointsGroup.appendChild(labelText);
            }
        });
        svg.appendChild(pointsGroup);
        container.appendChild(svg);
    }

    /**
     * Create a doughnut chart for payment type breakdown
     */
    function createDoughnutChart(containerId, data, options = {}) {
        clearContainer(containerId);
        const container = document.getElementById(containerId);
        if (!container) return;

        const labels = Object.keys(data);
        const values = Object.values(data);
        const total = values.reduce((a, b) => a + b, 0);
        const size = options.size || 280;
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = size / 2 - 20;
        const innerRadius = radius * 0.6;

        const svg = createSVGElement('svg', {
            width: size,
            height: size,
            viewBox: `0 0 ${size} ${size}`,
            style: 'display: block; margin: 0 auto;'
        });

        let currentAngle = -90;
        const paths = [];

        labels.forEach((label, index) => {
            const sliceAngle = (values[index] / total) * 360;
            const startAngle = currentAngle;
            const endAngle = currentAngle + sliceAngle;

            const startRad = (startAngle * Math.PI) / 180;
            const endRad = (endAngle * Math.PI) / 180;

            const x1 = centerX + radius * Math.cos(startRad);
            const y1 = centerY + radius * Math.sin(startRad);
            const x2 = centerX + radius * Math.cos(endRad);
            const y2 = centerY + radius * Math.sin(endRad);

            const ix1 = centerX + innerRadius * Math.cos(startRad);
            const iy1 = centerY + innerRadius * Math.sin(startRad);
            const ix2 = centerX + innerRadius * Math.cos(endRad);
            const iy2 = centerY + innerRadius * Math.sin(endRad);

            const largeArc = sliceAngle > 180 ? 1 : 0;

            const pathData = [
                `M ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`,
                `L ${ix2} ${iy2}`,
                `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${ix1} ${iy1}`,
                'Z'
            ].join(' ');

            const path = createSVGElement('path', {
                d: pathData,
                fill: colorPalette[index % colorPalette.length],
                stroke: 'white',
                'stroke-width': '2',
                style: 'cursor: pointer; transition: all 0.3s ease; transform-origin: center;'
            });

            path.addEventListener('mouseenter', function(e) {
                this.style.transform = 'scale(1.05)';
                this.style.filter = 'brightness(1.1)';
                const percentage = ((values[index] / total) * 100).toFixed(1);
                showTooltip(e, `${label}: ${formatCurrency(values[index])} (${percentage}%)`);
            });

            path.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.filter = 'none';
                hideTooltip();
            });

            svg.appendChild(path);
            currentAngle = endAngle;
        });

        // Center text
        const centerText = createSVGElement('text', {
            x: centerX,
            y: centerY - 5,
            'text-anchor': 'middle',
            'font-size': '18',
            'font-weight': '700',
            fill: colors.primary
        });
        centerText.textContent = formatCurrency(total);
        svg.appendChild(centerText);

        const centerLabel = createSVGElement('text', {
            x: centerX,
            y: centerY + 15,
            'text-anchor': 'middle',
            'font-size': '11',
            'fill': '#64748b',
            'font-weight': '500'
        });
        centerLabel.textContent = 'Total';
        svg.appendChild(centerLabel);

        container.appendChild(svg);

        // Legend
        const legend = document.createElement('div');
        legend.className = 'chart-legend';
        legend.style.cssText = `
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            margin-top: 1.5rem;
            padding: 0 1rem;
        `;

        labels.forEach((label, index) => {
            const percentage = ((values[index] / total) * 100).toFixed(1);
            const item = document.createElement('div');
            item.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.85rem;
                color: #475569;
                font-weight: 500;
            `;
            item.innerHTML = `
                <span style="width: 12px; height: 12px; border-radius: 3px; background: ${colorPalette[index % colorPalette.length]}; flex-shrink: 0;"></span>
                <span>${label}</span>
                <span style="font-weight: 700; color: #0f172a;">${percentage}%</span>
            `;
            legend.appendChild(item);
        });

        container.appendChild(legend);
    }

    /**
     * Create a horizontal bar chart for rankings
     */
    function createHorizontalBarChart(containerId, data, options = {}) {
        clearContainer(containerId);
        const container = document.getElementById(containerId);
        if (!container) return;

        const labels = Object.keys(data);
        const values = Object.values(data);
        const maxValue = Math.max(...values, 1);
        const chartHeight = options.height || Math.max(300, labels.length * 40 + 40);
        const chartWidth = container.clientWidth || 600;
        const padding = { top: 20, right: 100, bottom: 20, left: 120 };

        const svg = createSVGElement('svg', {
            width: '100%',
            height: chartHeight,
            viewBox: `0 0 ${chartWidth} ${chartHeight}`,
            preserveAspectRatio: 'xMidYMid meet'
        });

        const barHeight = Math.min(30, (chartHeight - padding.top - padding.bottom) / labels.length - 8);

        labels.forEach((label, index) => {
            const y = padding.top + index * ((chartHeight - padding.top - padding.bottom) / labels.length) + 4;
            const barWidth = (values[index] / maxValue) * (chartWidth - padding.left - padding.right);

            // Label
            const labelText = createSVGElement('text', {
                x: padding.left - 10,
                y: y + barHeight / 2 + 4,
                'text-anchor': 'end',
                'font-size': '12',
                'fill': '#0f172a',
                'font-weight': '600'
            });
            labelText.textContent = label.length > 20 ? label.substring(0, 20) + '...' : label;
            svg.appendChild(labelText);

            // Bar background
            const bgRect = createSVGElement('rect', {
                x: padding.left,
                y: y,
                width: chartWidth - padding.left - padding.right,
                height: barHeight,
                fill: '#f1f5f9',
                rx: '6',
                ry: '6'
            });
            svg.appendChild(bgRect);

            // Bar fill
            const bar = createSVGElement('rect', {
                x: padding.left,
                y: y,
                width: 0,
                height: barHeight,
                fill: colorPalette[index % colorPalette.length],
                rx: '6',
                ry: '6',
                style: 'cursor: pointer; transition: all 0.3s ease;'
            });

            setTimeout(() => {
                bar.setAttribute('width', barWidth);
            }, index * 80);

            bar.addEventListener('mouseenter', function(e) {
                this.style.filter = 'brightness(1.15)';
                showTooltip(e, `${label}: ${formatCurrency(values[index])}`);
            });

            bar.addEventListener('mouseleave', function() {
                this.style.filter = 'none';
                hideTooltip();
            });

            svg.appendChild(bar);

            // Value
            const valueText = createSVGElement('text', {
                x: padding.left + barWidth + 8,
                y: y + barHeight / 2 + 4,
                'font-size': '12',
                'font-weight': '700',
                fill: '#0f172a'
            });
            valueText.textContent = formatCurrency(values[index]);
            svg.appendChild(valueText);
        });

        container.appendChild(svg);
    }

    function showTooltip(e, text) {
        const tooltip = document.getElementById('chart-tooltip');
        if (!tooltip) return;
        tooltip.textContent = text;
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 10) + 'px';
        tooltip.style.top = (e.clientY - 30) + 'px';
    }

    function hideTooltip() {
        const tooltip = document.getElementById('chart-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    /**
     * Initialize all charts on the page
     */
    async function initCharts() {
        try {
            const response = await fetch('/reports/chart-data?' + new URLSearchParams(window.location.search));
            if (!response.ok) throw new Error('Failed to load chart data');
            const data = await response.json();

            // Create trend chart
            if (data.monthly && Object.keys(data.monthly).length > 0) {
                createLineChart('contribution-trend-chart', data.monthly, { height: 300 });
            } else {
                document.getElementById('contribution-trend-chart').innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #94a3b8;">
                        <i class="bi bi-graph-up" style="font-size: 3rem; opacity: 0.5;"></i>
                        <p style="margin-top: 1rem;">No trend data available</p>
                    </div>
                `;
            }

            // Create payment type doughnut
            if (data.payment_types && Object.keys(data.payment_types).length > 0) {
                createDoughnutChart('payment-type-chart', data.payment_types, { size: 280 });
            } else {
                document.getElementById('payment-type-chart').innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #94a3b8;">
                        <i class="bi bi-credit-card" style="font-size: 3rem; opacity: 0.5;"></i>
                        <p style="margin-top: 1rem;">No payment data available</p>
                    </div>
                `;
            }

            // Create top members chart
            if (data.top_members && Object.keys(data.top_members).length > 0) {
                createHorizontalBarChart('top-members-chart', data.top_members, { height: Math.max(300, Object.keys(data.top_members).length * 40 + 40) });
            } else {
                document.getElementById('top-members-chart').innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #94a3b8;">
                        <i class="bi bi-people" style="font-size: 3rem; opacity: 0.5;"></i>
                        <p style="margin-top: 1rem;">No member data available</p>
                    </div>
                `;
            }

            // Create event contributions chart
            if (data.events && Object.keys(data.events).length > 0) {
                createBarChart('event-contributions-chart', data.events, { height: 300 });
            } else {
                document.getElementById('event-contributions-chart').innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #94a3b8;">
                        <i class="bi bi-calendar-event" style="font-size: 3rem; opacity: 0.5;"></i>
                        <p style="margin-top: 1rem;">No event data available</p>
                    </div>
                `;
            }

            // Update average contribution card dynamically
            if (typeof data.average !== 'undefined') {
                const avgEl = document.getElementById('avg-amount-value');
                if (avgEl) {
                    avgEl.textContent = 'Ksh. ' + data.average.toLocaleString('en-KE');
                }
            }

        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCharts);
    } else {
        initCharts();
    }

    return {
        initCharts,
        createBarChart,
        createLineChart,
        createDoughnutChart,
        createHorizontalBarChart
    };
})();
