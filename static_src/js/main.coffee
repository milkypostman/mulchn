require.config {
  urlArgs: "bust=" + (new Date()).getTime()
  baseUrl: "/static/js"
  
  paths: {
    bootstrap: 'lib/bootstrap.min',
    jquery: 'lib/jquery.min',
    lodash: 'lib/lodash.min',
    backbone: 'lib/backbone-min',
    }


  shim: {
    'backbone': {
      deps: ['jquery', 'lodash'],
      exports: 'Backbone',
      },
    'bootstrap' : ['jquery']
    }
  }



  
require ['jquery', 'backbone', 'router'], ($, Backbone, Router) ->
  console.log("main")
  window.setTimeout(
    -> $('.alert').fadeOut('fast', -> $(this).remove())
    3000)

  app = new Router()

  # console.log(Backbone.History);
  Backbone.history.start({pushState: true})

  {}


