function filterContainer(searchInput, containerId) {
    var filter = searchInput.value.trim().toUpperCase();
    var container = document.getElementById(containerId);
    
    if (!container) return;
    
    var elements = container.querySelectorAll('.member-card, .searchable-item, .list-group-item, tbody tr');
    var hasVisible = false;
    
    for (var i = 0; i < elements.length; i++) {
        var txtValue = elements[i].textContent || elements[i].innerText;
        if (filter === "" || txtValue.toUpperCase().indexOf(filter) > -1) {
            elements[i].style.display = "";
            hasVisible = true;
        } else {
            elements[i].style.display = "none";
        }
    }
    
    var emptyStates = container.querySelectorAll(':scope > .empty-state');
    for (var j = 0; j < emptyStates.length; j++) {
        emptyStates[j].style.display = hasVisible ? "none" : "";
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function initSearch() {
    var searchInputs = document.querySelectorAll('.search-box input[type="text"], input[data-target]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function() {
            var targetId = this.getAttribute('data-target');
            if (targetId) {
                filterContainer(this, targetId);
            }
        }, 150));
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
} else {
    initSearch();
}
