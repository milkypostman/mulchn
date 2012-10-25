require.config {
  urlArgs: "bust=" + (new Date()).getTime()
  baseUrl: "/static/js"
  
  paths: {
    jquery: 'lib/jquery.min',
    lodash: 'lib/lodash.min',
    backbone: 'lib/backbone-min',
    }


  shim: {
    'backbone': {
      deps: ['jquery', 'lodash'],
      exports: 'Backbone'
      }
    }
  }

  
require ['lodash', 'question/collectionview'], (_, QuestionCollectionView) ->
  questionCollectionView = new QuestionCollectionView()
  questionCollectionView.collection.fetch()


  window.setTimeout(
    -> $('.alert').fadeOut('fast', -> $(this).remove())
    3000)



