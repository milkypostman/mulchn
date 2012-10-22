$(window).load ->
  window.setTimeout(
    -> $('.alert').fadeOut('slow', -> $(this).remove()),
    3000)


