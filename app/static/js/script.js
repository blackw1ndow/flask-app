// Закриваємо мобільне меню після натискання на пункт
document.querySelectorAll('.cv-nav-wrap .nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
        var menu = document.getElementById('mainNav');
        if (menu && menu.classList.contains('show')) {
            bootstrap.Collapse.getOrCreateInstance(menu).hide();
        }
    });
});
