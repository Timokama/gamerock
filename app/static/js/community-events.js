(function () {
    'use strict';

    // ===== Countdown Timer =====
    class CountdownTimer {
        constructor(element, targetDate) {
            this.element = element;
            this.target = new Date(targetDate);
            this.interval = null;
            this.start();
        }

        start() {
            this.update();
            this.interval = setInterval(() => this.update(), 1000);
        }

        update() {
            const now = new Date();
            const diff = this.target - now;
            if (diff <= 0) {
                this.element.textContent = 'Event started';
                clearInterval(this.interval);
                return;
            }
            const days = Math.floor(diff / 86400000);
            const hours = Math.floor((diff % 86400000) / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            this.element.innerHTML = `<i class="bi bi-clock"></i> ${days}d ${hours}h ${minutes}m ${seconds}s`;
        }

        stop() {
            if (this.interval) clearInterval(this.interval);
        }
    }

    // ===== Contribution Thermometer =====
    function initThermometers() {
        document.querySelectorAll('.event-thermometer').forEach(el => {
            const goal = parseFloat(el.dataset.goal) || 0;
            const current = parseFloat(el.dataset.current) || 0;
            const percentage = goal > 0 ? Math.min((current / goal) * 100, 100) : 0;
            const fill = el.querySelector('.thermometer-fill');
            const label = el.querySelector('.thermometer-label');
            if (fill) fill.style.width = percentage + '%';
            if (label) label.textContent = `Ksh. ${current.toLocaleString('en-KE')} / ${goal.toLocaleString('en-KE')}`;
        });
    }

    // ===== Bookmark Manager =====
    const BookmarkManager = {
        KEY: 'gamerock_event_bookmarks',

        get() {
            try {
                return JSON.parse(localStorage.getItem(this.KEY)) || [];
            } catch (e) {
                return [];
            }
        },

        save(bookmarks) {
            localStorage.setItem(this.KEY, JSON.stringify(bookmarks));
        },

        toggle(eventId) {
            const bookmarks = this.get();
            const index = bookmarks.indexOf(eventId);
            if (index > -1) {
                bookmarks.splice(index, 1);
                this.save(bookmarks);
                return false;
            } else {
                bookmarks.push(eventId);
                this.save(bookmarks);
                return true;
            }
        },

        has(eventId) {
            return this.get().includes(eventId);
        }
    };

    // ===== Filter Persistence =====
    const FilterPersistence = {
        KEY: 'gamerock_event_filters',

        save(filters) {
            try {
                sessionStorage.setItem(this.KEY, JSON.stringify(filters));
            } catch (e) {
                // ignore
            }
        },

        get() {
            try {
                return JSON.parse(sessionStorage.getItem(this.KEY)) || {};
            } catch (e) {
                return {};
            }
        },

        clear() {
            sessionStorage.removeItem(this.KEY);
        }
    };

    // ===== Activity Feed =====
    async function loadActivityFeed(eventId) {
        const container = document.getElementById('activityFeedList');
        if (!container) return;

        try {
            const response = await fetch(`/community/${eventId}/stats`);
            if (!response.ok) throw new Error('Failed to load activity');
            const data = await response.json();

            const members = Object.entries(data.top_members || {}).slice(0, 5);
            if (!members.length) {
                container.innerHTML = `
                    <div class="activity-feed-empty">
                        <i class="bi bi-inbox"></i>
                        <p>No contributions yet. Be the first to contribute!</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = members.map(([name, amount]) => `
                <div class="activity-feed-item">
                    <div class="activity-feed-avatar">
                        <i class="bi bi-person"></i>
                    </div>
                    <div class="activity-feed-content">
                        <div class="activity-feed-name">${escapeHtml(name)}</div>
                        <div class="activity-feed-amount">Ksh. ${amount.toLocaleString('en-KE')}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading activity feed:', error);
        }
    }

    // ===== Quick Contribute =====
    function initQuickContribute() {
        const form = document.getElementById('quickContributeForm');
        if (!form) return;

        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const eventId = document.getElementById('quickContributeEventId').value;
            const amount = document.getElementById('quickContributeAmount').value;
            const paymentType = document.getElementById('quickContributePaymentType').value;
            const feedback = document.getElementById('quickContributeFeedback');

            if (!eventId || !amount || !paymentType) {
                feedback.innerHTML = `<div class="alert alert-danger">Please fill all fields.</div>`;
                return;
            }

            const formData = new FormData();
            formData.append('amount', amount);
            formData.append('payment_type', paymentType);

            try {
                const response = await fetch(`/community/${eventId}/contribute`, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const result = await response.json();

                if (result.success) {
                    feedback.innerHTML = `<div class="alert alert-success">${escapeHtml(result.message)}</div>`;
                    form.reset();
                    document.getElementById('quickContributeAmount').value = '';
                    document.getElementById('quickContributePaymentType').value = '';
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(document.getElementById('quickContributeModal')).hide();
                        location.reload();
                    }, 1200);
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${escapeHtml(result.message || 'Error')}</div>`;
                }
            } catch (error) {
                feedback.innerHTML = `<div class="alert alert-danger">Network error. Please try again.</div>`;
            }
        });
    }

    // ===== Share Button =====
    function initShareButton(button, eventId, eventName) {
        button.addEventListener('click', async () => {
            const url = `${window.location.origin}/community/contribute/${encodeURIComponent(eventName)}`;
            const text = `Check out this community event: ${eventName}`;

            if (navigator.share) {
                try {
                    await navigator.share({ title: eventName, text, url });
                } catch (err) {
                    // user cancelled
                }
            } else {
                try {
                    await navigator.clipboard.writeText(url);
                    const original = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    setTimeout(() => button.innerHTML = original, 2000);
                } catch (err) {
                    window.open(`https://wa.me/254745908682?text=${encodeURIComponent(text + ' ' + url)}`, '_blank');
                }
            }
        });
    }

    // ===== Helpers =====
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ===== Public API =====
    window.GamerockCommunity = {
        CountdownTimer,
        initThermometers,
        BookmarkManager,
        FilterPersistence,
        loadActivityFeed,
        initQuickContribute,
        initShareButton,
        escapeHtml
    };
})();