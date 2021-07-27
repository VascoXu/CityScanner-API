// Highlight selected page in navbar
$(".navbar-nav .nav-link").each(function() {
    if (window.location.href == this.href) {
        $(".navbar-nav .nav-item").removeClass("active");
        $(this).addClass("active");
    }
});