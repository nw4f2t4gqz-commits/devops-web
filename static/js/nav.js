// nav.js: add active class for hash-based anchors (e.g. /#services)
(function () {
    function markServices() {
        try {
            const servicesLink = document.getElementById('nav-services');
            const homeLink = document.getElementById('nav-home');
            if (!servicesLink) return;
            // If the URL has #services, mark it active and remove active state from home
            if (window.location.hash === '#services') {
                servicesLink.classList.add('font-bold', 'text-blue-300');
                servicesLink.setAttribute('aria-current', 'page');
                if (homeLink) {
                    homeLink.classList.remove('font-bold', 'text-blue-300');
                    homeLink.removeAttribute('aria-current');
                }
            } else {
                // remove services highlight; leave server-side active states alone
                servicesLink.classList.remove('font-bold', 'text-blue-300');
                servicesLink.removeAttribute('aria-current');
            }
        } catch (e) {
            // ignore
        }
    }

    window.addEventListener('hashchange', markServices);
    document.addEventListener('DOMContentLoaded', markServices);
})();
