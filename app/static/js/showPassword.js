var eyeShowSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
var eyeHideSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.88 9.88 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';

function togglePassword(inputId, toggleId) {
    var input = document.getElementById(inputId);
    var toggle = document.getElementById(toggleId);
    
    if (!input || !toggle) return;
    
    var isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    
    toggle.innerHTML = isPassword ? eyeHideSvg : eyeShowSvg;
    toggle.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
    toggle.setAttribute('aria-pressed', isPassword ? 'true' : 'false');
    toggle.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
    toggle.classList.toggle('active', isPassword);
    
    if (isPassword) {
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('inputmode', 'text');
    } else {
        input.removeAttribute('autocomplete');
        input.removeAttribute('inputmode');
    }
}

function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            var inputId = this.getAttribute('data-input-id');
            togglePassword(inputId, this.id);
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordToggles);
} else {
    initPasswordToggles();
}
