import os

files = [
    'app/templates/base.html',
    'app/templates/base_f/base.html',
]

new_footer = '''        <!-- Footer -->
        {% block footer %}
        <footer class="footer">
            <div class="footer-container">
                <div class="footer-main">
                    <div class="footer-brand">
                        <div class="footer-logo">
                            <span class="footer-logo-icon">🏠</span>
                            <span class="footer-logo-text">Gamerock</span>
                        </div>
                        <p class="footer-description">Building stronger communities through welfare, unity, and sustainable development. Join us in making a difference.</p>
                        <div class="footer-social">
                            <a href="mailto:info@gamerock.org" class="social-link" aria-label="Email">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/></svg>
                            </a>
                            <a href="tel:+254700000000" class="social-link" aria-label="Phone">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                            </a>
                            <a href="https://maps.google.com/?q=Gamerock Shopping Center" target="_blank" rel="noopener" class="social-link" aria-label="Location">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.4 8 12 8 12s8-6.6 8-12a8 8 0 0 0-8-8z"/><circle cx="12" cy="10" r="3"/></svg>
                            </a>
                        </div>
                    </div>
                    <div class="footer-links-grid">
                        <div class="footer-column">
                            <h6 class="footer-column-title">Quick Links</h6>
                            <ul class="footer-links">
                                <li><a href="{{ url_for('main.profile') }}">Profile</a></li>
                                <li><a href="{{ url_for('register.index') }}">Members</a></li>
                                <li><a href="{{ url_for('family.index') }}">Family</a></li>
                                <li><a href="{{ url_for('deposit.index') }}">Deposits</a></li>
                            </ul>
                        </div>
                        <div class="footer-column">
                            <h6 class="footer-column-title">Services</h6>
                            <ul class="footer-links">
                                <li><a href="{{ url_for('community.index') }}">Community Events</a></li>
                                <li><a href="{{ url_for('reports.index') }}">Reports</a></li>
                                <li><a href="{{ url_for('account.cont') }}">Contribution Accounts</a></li>
                            </ul>
                        </div>
                        <div class="footer-column">
                            <h6 class="footer-column-title">Support</h6>
                            <ul class="footer-links">
                                <li><a href="#faq">FAQ</a></li>
                                <li><a href="#about">About Us</a></li>
                                <li><a href="#contact">Contact</a></li>
                            </ul>
                        </div>
                        <div class="footer-column">
                            <h6 class="footer-column-title">Contact</h6>
                            <ul class="footer-links">
                                <li>
                                    <a href="tel:+254700000000">
                                        <span class="footer-contact-icon">
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                                        </span>
                                        +254 700 000 000
                                    </a>
                                </li>
                                <li>
                                    <a href="mailto:info@gamerock.org">
                                        <span class="footer-contact-icon">
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/></svg>
                                        </span>
                                        info@gamerock.org
                                    </a>
                                </li>
                                <li>
                                    <span class="footer-contact-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.4 8 12 8 12s8-6.6 8-12a8 8 0 0 0-8-8z"/><circle cx="12" cy="10" r="3"/></svg>
                                    </span>
                                    Nyeri, Kenya
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="footer-bottom">
                    <div class="footer-bottom-inner">
                        <p class="footer-copyright">&copy; {{ now().year }} Gamerock Welfare Association. All rights reserved.</p>
                        <div class="footer-bottom-links">
                            <a href="#privacy">Privacy Policy</a>
                            <a href="#terms">Terms of Service</a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
        {% endblock %}
'''

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = '        <!-- Footer -->\n'
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f'Footer start not found in {path}')
        continue

    # Find the end of the footer block by locating the next block or script tag
    search_area = content[start_idx:]
    end_marker = '    <!-- Bootstrap JS -->'
    end_idx = search_area.find(end_marker)
    if end_idx == -1:
        print(f'Footer end not found in {path}')
        continue

    end_idx += start_idx

    new_content = content[:start_idx] + new_footer + '\n' + content[end_idx:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated footer in {path}')
