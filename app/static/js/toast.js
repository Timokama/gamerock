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
