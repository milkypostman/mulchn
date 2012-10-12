var selAnswer;


$(window).load(function () {
    // $(".answers i").hide();
    // $(".answers").first().show();
    $(".question").click(function(obj) {
        var t = $(this);
        if (!selAnswer) {
            t.children(".answers").slideDown();
            t.addClass("active");
            selAnswer = this;
        }
        else
        {
            if (selAnswer == this) {
                t.children(".answers").slideUp();
                t.removeClass("active");
                selAnswer = undefined;
            }
            else
            {
                var sa = $(selAnswer);
                sa.children(".answers").slideUp();
                sa.removeClass("active");
                t.children(".answers").slideDown();
                t.addClass("active");
                selAnswer = this;
            }
        }
        return false;
    });
    // $(".answer").hover(function (obj) {
    //     $(this).children("i").fadeTo("fast", .5);
    //     }, function (obj) {
    //         $(this).children("i").fadeOut();
    //     });
    $(".answer").click(function (obj) {
        $(this).addClass("vote");
        return false;
    })
})
