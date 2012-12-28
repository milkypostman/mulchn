define ['jquery', 'lodash', 'backbone', 'question/model'], ($, _, Backbone, QuestionModel) ->
  class QuestionCollection extends Backbone.Collection
    model: QuestionModel
    url: '/v1/questions/'

    updateOrAdd: (collection, response) =>
      _.each(response, (ele) ->
        collection.get(ele._id).set(ele))


    update: =>
      @fetch({add:true, success: @updateOrAdd})





