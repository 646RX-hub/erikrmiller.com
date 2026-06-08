/* ============================================================
   E.R.M. site navigation — single source of truth (behavior)
   Extracted verbatim from the homepage nav JS:
     - sticky ("stuck") header on scroll
     - mobile hamburger open/close + Escape + body scroll lock
   Idempotent: clones the hamburger before binding so it cannot
   double-bind if a legacy inline copy is also present on a page.
   ============================================================ */
(function () {
  function init() {
    var nav = document.getElementById('nav');
    if (nav) {
      var onScroll = function () { nav.classList.toggle('stuck', window.scrollY > 60); };
      window.addEventListener('scroll', onScroll);
      onScroll();
    }

    var hamburger = document.getElementById('navHamburger');
    var mobileNav = document.getElementById('mobileNav');
    if (hamburger && mobileNav) {
      // Drop any previously-bound listeners (e.g. legacy inline nav script) to avoid double-toggling.
      var fresh = hamburger.cloneNode(true);
      hamburger.parentNode.replaceChild(fresh, hamburger);
      hamburger = fresh;

      function closeMobileNav() {
        mobileNav.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.setAttribute('aria-label', 'Open navigation menu');
        document.body.style.overflow = '';
      }
      window.closeMobileNav = closeMobileNav;

      hamburger.addEventListener('click', function () {
        var isOpen = mobileNav.classList.toggle('open');
        hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        hamburger.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
        document.body.style.overflow = isOpen ? 'hidden' : '';
      });

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && mobileNav.classList.contains('open')) closeMobileNav();
      });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
