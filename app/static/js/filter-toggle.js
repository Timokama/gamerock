// app/static/js/filter-toggle.js
// Responsive filter toggle with mobile drawer, tablet side drawer, and touch gestures
(function () {
  'use strict';

  // Configuration
  var MOBILE_BREAKPOINT = 768;
  var TABLET_BREAKPOINT = 1024;
  var SWIPE_THRESHOLD = 50;
  var SWIPE_VELOCITY_THRESHOLD = 0.3;

  // State
  var isMobile = function () { return window.innerWidth <= MOBILE_BREAKPOINT; };
  var isTablet = function () { return window.innerWidth > MOBILE_BREAKPOINT && window.innerWidth <= TABLET_BREAKPOINT; };
  var isDesktop = function () { return window.innerWidth > TABLET_BREAKPOINT; };
  // Tablet uses desktop behavior (inline filters)
  var usesDrawer = function () { return isMobile(); };

  var activePanel = null;
  var activeBackdrop = null;
  var touchStartY = 0;
  var touchStartX = 0;
  var touchStartTime = 0;
  var bodyOverflow = '';

  // Create backdrop element
  function createBackdrop() {
    var backdrop = document.createElement('div');
    backdrop.className = 'filter-backdrop';
    backdrop.setAttribute('aria-hidden', 'true');
    backdrop.addEventListener('click', closeAllFilters);
    backdrop.addEventListener('touchstart', function (e) { e.preventDefault(); }, { passive: false });
    document.body.appendChild(backdrop);
    return backdrop;
  }

  // Get or create backdrop
  function getBackdrop() {
    if (!activeBackdrop || !document.body.contains(activeBackdrop)) {
      activeBackdrop = createBackdrop();
    }
    return activeBackdrop;
  }

  // Prevent body scroll
  function lockBodyScroll() {
    bodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.body.classList.add('filter-open');
    // Store scroll position for iOS Safari
    document.body.dataset.scrollY = window.scrollY;
  }

  // Restore body scroll
  function unlockBodyScroll() {
    document.body.style.overflow = bodyOverflow;
    document.body.classList.remove('filter-open');
    if (document.body.dataset.scrollY) {
      window.scrollTo(0, parseInt(document.body.dataset.scrollY, 10));
      delete document.body.dataset.scrollY;
    }
  }

  // Open filter panel
  function openFilter(btn, panel) {
    if (!usesDrawer()) return; // Desktop/tablet don't use toggle drawer

    closeAllFilters(); // Close any other open filters

    activePanel = panel;
    var backdrop = getBackdrop();

    // Force reflow for animation
    panel.offsetHeight;

    panel.classList.add('active');
    backdrop.classList.add('active');
    btn.setAttribute('aria-expanded', 'true');

    lockBodyScroll();

    // Focus trap - focus first focusable element in panel
    setTimeout(function () {
      var focusable = panel.querySelector(
        'input, select, button, [href], [tabindex]:not([tabindex="-1"])'
      );
      if (focusable) focusable.focus({ preventScroll: true });
    }, 150);

    // Touch event listeners for swipe to close
    panel.addEventListener('touchstart', handleTouchStart, { passive: true });
    panel.addEventListener('touchmove', handleTouchMove, { passive: false });
    panel.addEventListener('touchend', handleTouchEnd, { passive: true });

    // Keyboard: ESC to close
    document.addEventListener('keydown', handleKeydown);
  }

  // Close filter panel
  function closeFilter(btn, panel) {
    if (!panel) return;

    panel.classList.remove('active');

    var backdrop = document.querySelector('.filter-backdrop');
    if (backdrop) {
      backdrop.classList.remove('active');
    }

    if (btn) {
      btn.setAttribute('aria-expanded', 'false');
    }

    // Remove touch listeners
    panel.removeEventListener('touchstart', handleTouchStart);
    panel.removeEventListener('touchmove', handleTouchMove);
    panel.removeEventListener('touchend', handleTouchEnd);

    // Remove keyboard listener if no other panels open
    if (!document.querySelector('.filter-bar-collapsible.active')) {
      document.removeEventListener('keydown', handleKeydown);
      unlockBodyScroll();
      activePanel = null;
    }
  }

  // Close all filters
  function closeAllFilters() {
    var panels = document.querySelectorAll('.filter-bar-collapsible.active');
    panels.forEach(function (panel) {
      var btnId = panel.getAttribute('aria-labelledby') || panel.id.replace('-list', '-toggle');
      var btn = document.getElementById(btnId) ||
                document.querySelector('[aria-controls="' + panel.id + '"]');
      closeFilter(btn, panel);
    });
  }

  // Keydown handler (ESC to close)
  function handleKeydown(e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
      closeAllFilters();
    }
  }

  // Touch start
  function handleTouchStart(e) {
    var touch = e.touches[0];
    touchStartY = touch.clientY;
    touchStartX = touch.clientX;
    touchStartTime = Date.now();
  }

  // Touch move - prevent body scroll, track swipe
  function handleTouchMove(e) {
    if (!activePanel) return;

    var touch = e.touches[0];
    var deltaY = touch.clientY - touchStartY;
    var deltaX = touch.clientX - touchStartX;

    // Mobile only: swipe down to close
    if (isMobile() && deltaY > 0) {
      e.preventDefault();
      var translateY = Math.min(deltaY * 0.5, 200); // Resistance
      activePanel.style.transform = 'translateY(' + translateY + 'px)';
      activePanel.style.opacity = 1 - (translateY / 400);
    }
  }

  // Touch end - decide whether to close
  function handleTouchEnd(e) {
    if (!activePanel) return;

    var touch = e.changedTouches[0];
    var deltaY = touch.clientY - touchStartY;
    var deltaX = touch.clientX - touchStartX;
    var deltaTime = Date.now() - touchStartTime;
    var velocityY = Math.abs(deltaY) / deltaTime;
    var velocityX = Math.abs(deltaX) / deltaTime;

    var shouldClose = false;

    if (isMobile()) {
      shouldClose = deltaY > SWIPE_THRESHOLD || (deltaY > 20 && velocityY > SWIPE_VELOCITY_THRESHOLD);
    }

    // Reset transform
    activePanel.style.transform = '';
    activePanel.style.opacity = '';

    if (shouldClose) {
      var btn = document.querySelector('[aria-controls="' + activePanel.id + '"]');
      closeFilter(btn, activePanel);
    }
  }

  // Initialize filter toggles
  function initFilterToggles() {
    var toggles = document.querySelectorAll('.filter-bar-toggle, .filter-toggle-btn');

    toggles.forEach(function (btn) {
      if (btn.dataset.filterToggleBound) return;
      btn.dataset.filterToggleBound = 'true';

      var panelId = btn.getAttribute('aria-controls');
      if (!panelId) return;

      var panel = document.getElementById(panelId);
      if (!panel) return;

      // Link panel to button for focus management
      panel.setAttribute('aria-labelledby', btn.id || 'filter-toggle-' + panelId);

      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        var expanded = btn.getAttribute('aria-expanded') === 'true';

        if (expanded) {
          closeFilter(btn, panel);
        } else {
          openFilter(btn, panel);
        }
      });

      // Keyboard support for toggle button
      btn.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          btn.click();
        }
      });
    });

    // Handle window resize - close filters on desktop/tablet transition
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        if (!usesDrawer()) {
          closeAllFilters();
          unlockBodyScroll();
        }
      }, 150);
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initFilterToggles();
      initFilterFormSubmit();
    });
  } else {
    initFilterToggles();
    initFilterFormSubmit();
  }

  // Auto-close filter drawer on form submission (mobile only)
  function initFilterFormSubmit() {
    var forms = document.querySelectorAll('.filter-bar-collapsible form');
    forms.forEach(function (form) {
      form.addEventListener('submit', function () {
        if (usesDrawer()) {
          closeAllFilters();
        }
      });
    });
  }

  // Expose for manual control if needed
  window.FilterToggle = {
    open: function (panelId) {
      var btn = document.querySelector('[aria-controls="' + panelId + '"]');
      var panel = document.getElementById(panelId);
      if (btn && panel) openFilter(btn, panel);
    },
    close: function (panelId) {
      var btn = document.querySelector('[aria-controls="' + panelId + '"]');
      var panel = document.getElementById(panelId);
      if (panel) closeFilter(btn, panel);
    },
    closeAll: closeAllFilters
  };
})();