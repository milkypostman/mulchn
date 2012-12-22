require ['config'], () ->
  require ['jquery'], ($) ->
    console.log("main")
    window.setTimeout(
      -> $('.alert').fadeOut('fast', -> $(this).remove())
      3000)



