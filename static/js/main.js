// Generated by CoffeeScript 1.4.0
(function() {

  require.config({
    urlArgs: "bust=" + (new Date()).getTime(),
    baseUrl: "/static/js",
    paths: {
      bootstrap: 'lib/bootstrap.min',
      jquery: 'lib/jquery.min',
      lodash: 'lib/lodash.min',
      backbone: 'lib/backbone-min'
    },
    shim: {
      'backbone': {
        deps: ['jquery', 'lodash'],
        exports: 'Backbone'
      },
      'bootstrap': ['jquery']
    }
  });

  require(['lodash', 'question/list'], function(_, QuestionList) {
    var questionList;
    questionList = new QuestionList();
    questionList.update();
    questionList.render();
    return window.setTimeout(function() {
      return $('.alert').fadeOut('fast', function() {
        return $(this).remove();
      });
    }, 3000);
  });

}).call(this);
