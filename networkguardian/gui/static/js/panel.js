$(function () {
    // Enable Tool Tips
    $('[data-toggle="tooltip"]').tooltip();

    // Enable Toast's
    $('.toast').each(function () {
        $(this).toast("show");
    });

    // Add "clickable-row" functionality
    $(".clickable-row").click(function () {
        window.location = $(this).data("href");
    });

    // Enable DataTables
    $('#data-table').DataTable();

    // Scroll to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });

    // scroll body to 0px on click
    $('#back-to-top').each(function () {
        $(this).click(function () {
            $('#back-to-top').tooltip('hide');
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });
    });
});