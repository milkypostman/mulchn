$(window).ready( ->
  console.log("main")
  $('.messages').slideDown()
  window.setTimeout(
    -> $('.messages').slideUp(-> $(this).remove())
    3000)
  
  window.geoLocation = GeoLocation.getInstance()
  window.account = Account.getInstance()
  
  window.app = new Router()
  Backbone.history.start({pushState: true, hashChange: true})
  
  )


