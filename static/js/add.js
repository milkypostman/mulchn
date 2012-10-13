
$(window).load(function () {
    console.log("load function");
    $('#qform').submit(function () {
        console.log($('#category').val() + "/");
        $(".help-inline").remove();
        $(".error").removeClass("error");

        $.ajax({
            url: "/question/",
            data: $(this).serialize(),
            type: "PUT",
            success: function(data) {
                console.log(data);
            },
            error: function(error) {
                ejson = $.parseJSON(error.responseText);
                $.each(ejson, function(id, errlist) {
                    widget = $("#" + id);
                    errorul = "<ul class='help-inline'>";
                    for(var i=0; i < errlist.length; i++)
                    {
                        errorul += "<li>" + errlist[i] + "</li>";
                    }
                    errorul += "</ul>";
                    widget.before(errorul);
                    widget.parent().addClass("error");
                    console.log(widget.parent("div"));

                });
            }
        });

        return false;
    });
})
