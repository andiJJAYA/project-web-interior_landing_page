document.addEventListener('DOMContentLoaded', function() {
    var navCollapse = document.getElementById('navMenu');

    if (navCollapse) {
        var bsCollapse = new bootstrap.Collapse(navCollapse, {
            toggle: false 
        });

        var navLinks = navCollapse.querySelectorAll('.nav-link');

        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (navCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });
    }
});