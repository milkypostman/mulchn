class QuestionModel extends Backbone.Model
  # idAttribute: "_id"

  url: ->
    "/v1/question/#{@id}"

  votes: ->
    _.reduce(@get('answers')
        (t, a) -> t + (a.votes or 0)
        0)

  followee_votes: ->
    _.reduce(@get('answers')
        (t, a) -> t + (a.followee_votes or 0)
        0) or 1
