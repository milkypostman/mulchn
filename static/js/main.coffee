$(window).ready( ->
  console.log("main")
  window.setTimeout(
    -> $('.alert').fadeOut('fast', -> $(this).remove())
    3000)
  
  
  app = new Router()
  # console.log(Backbone.History);
  Backbone.history.start({pushState: true, hashChange: true})
  
  )


