function showToast(message, category) {
  var toastConfig = {
    'success': {'icon': 'bi-check-circle-fill', 'color': '#10b981', 'bg': 'rgba(16, 185, 129, 0.1)', 'border': 'rgba(16, 185, 129, 0.2)'},
    'error': {'icon': 'bi-x-circle-fill', 'color': '#ef4444', 'bg': 'rgba(239, 68, 68, 0.1)', 'border': 'rgba(239, 68, 68, 0.2)'},
    'danger': {'icon': 'bi-x-circle-fill', 'color': '#ef4444', 'bg': 'rgba(239, 68, 68, 0.1)', 'border': 'rgba(239, 68, 68, 0.2)'},
    'warning': {'icon': 'bi-exclamation-triangle-fill', 'color': '#f59e0b', 'bg': 'rgba(245, 158, 11, 0.1)', 'border': 'rgba(245, 158, 11, 0.2)'},
    'info': {'icon': 'bi-info-circle-fill', 'color': '#3b82f6', 'bg': 'rgba(59, 130, 246, 0.1)', 'border': 'rgba(59, 130, 246, 0.2)'}
  }.get(category, {'icon': 'bi-info-circle-fill', 'color': '#6b7280', 'bg': 'rgba(107, 114, 128, 0.1)', 'border': 'rgba(107, 114, 128, 0.2)'});

  var toast = document.createElement('div');
  toast.className = 'toast-item';
  toast.setAttribute('role', 'alert');
  toast.setAttribute('data-toast-category', category);
  toast.style.setProperty('--toast-color', toastConfig.color);
  toast.style.setProperty('--toast-bg', toastConfig.bg);
  toast.style.setProperty('--toast-border', toastConfig.border);
  toast.innerHTML = '<div class="toast-icon"><i class="bi ' + toastConfig.icon + '"></i></div>' +
    '<div class="toast-content"><div class="toast-message">' + message + '</div></div>' +
    '<button type="button" class="toast-close" aria-label="Close notification" onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>';

  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }
  container.appendChild(toast);

  var duration = category === 'error' || category === 'danger' ? 8000 : 5000;
  setTimeout(function() {
    toast.classList.add('removing');
    setTimeout(function() {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 350);
  }, duration);
}

function initToasts() {
  var toasts = document.querySelectorAll('.toast-item');
  toasts.forEach(function(toast) {
    var duration = 5000;
    var category = toast.getAttribute('data-toast-category');
    
    if (category === 'error' || category === 'danger') {
      duration = 8000;
    }
    
    setTimeout(function() {
      toast.classList.add('removing');
      setTimeout(function() {
        if (toast.parentElement) {
          toast.remove();
        }
      }, 350);
    }, duration);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initToasts);
} else {
  initToasts();
}
