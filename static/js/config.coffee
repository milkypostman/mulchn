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



  



