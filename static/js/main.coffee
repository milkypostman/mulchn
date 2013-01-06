$(window).ready( ->
  console.log("main")
  window.setTimeout(
    -> $('.alert').fadeOut('fast', -> $(this).remove())
    3000)
  
  window.geoLocation = GeoLocation.getInstance()
  window.account = Account.getInstance()
  
  window.app = new Router()
  # console.log(Backbone.History);
  Backbone.history.start({pushState: true, hashChange: true})
  
  )


