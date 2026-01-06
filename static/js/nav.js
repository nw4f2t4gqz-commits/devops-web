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

// Mobile menu toggle logic
(function () {
    function toggleMobileMenu(open) {
        try {
            var menu = document.getElementById('mobile-menu');
            var btn = document.getElementById('mobile-menu-button');
            if (!menu || !btn) return;
            if (open === undefined) open = menu.classList.contains('hidden');
            if (open) {
                menu.classList.remove('hidden');
                btn.setAttribute('aria-expanded', 'true');
            } else {
                menu.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            }
        } catch (e) {
            // ignore
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        try {
            var btn = document.getElementById('mobile-menu-button');
            if (!btn) return;
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                toggleMobileMenu();
            });
            // close menu when navigating via links inside it (improves mobile UX)
            var menu = document.getElementById('mobile-menu');
            if (menu) {
                menu.addEventListener('click', function (e) {
                    var target = e.target;
                    if (target && target.tagName === 'A') {
                        toggleMobileMenu(false);
                    }
                });
            }
        } catch (e) {
            // ignore
        }
    });
})();
