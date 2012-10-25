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

  
require ['lodash', 'question/list'], (_, QuestionList) ->
  questionList = new QuestionList()
  questionList.update()
  questionList.render()


  window.setTimeout(
    -> $('.alert').fadeOut('fast', -> $(this).remove())
    3000)



