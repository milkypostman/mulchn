define ['jquery', 'lodash', 'backbone', 'question/model'], ($, _, Backbone, QuestionModel) ->
  class QuestionCollection extends Backbone.Collection
    model: QuestionModel
    url: '/v1/questions/'
    initialize: ->
      console.log("collection initialize")



