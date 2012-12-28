define ['lodash', 'backbone'], (_, Backbone) ->
  class QuestionModel extends Backbone.Model
    idAttribute: "_id"

    url: ->
      "/v1/question/#{@id}"

    votes: ->
      _.reduce(@get('answers')
          (t, a) -> t + (a.votes | 0)
          0)
