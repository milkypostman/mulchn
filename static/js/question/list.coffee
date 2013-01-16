class QuestionList extends Backbone.View
  tagName: "ul"

  attributes: {id: "questions", class:"questions slicklist"}
  
  events: {
    "click .question": "toggleQuestion"
    "click .question a": "stopPropagation"
    }

  initialize: () =>
    if @collection
      @collection.on("add", @add)
      @collection.on("reset", @addAll)
      @collection.on("remove", @remove)
    @selectedQuestion = undefined
    @childViews = {}


  stopPropagation: (event) =>
    event.stopImmediatePropagation()

  toggleQuestion: (event) =>
    @toggleView(event.currentTarget)

  toggleView: (target) =>
    targetId = target.id
    if @selectedQuestion
      # @childViews[@selectedQuestion].collapse(=> $('html, body').animate({scrollTop: @originalPosition}, 400))
      @childViews[@selectedQuestion].collapse()

    if targetId == @selectedQuestion
      @selectedQuestion = undefined
    else
      view = @childViews[targetId]
      # @originalPosition = $('html, body').scrollTop()
      # view.expand(=> $('html, body').animate({scrollTop: view.$el.offset().top - 50}, 100))
      view.expand()
      @selectedQuestion = targetId

  newQuestionView: (model) =>
    return new QuestionView({model: model, tagName: "li"})

  # this is specialized to add in the proper position
  add: (model) =>
    view = @newQuestionView(model)
    @childViews[model.id] = view
    for ele in @$el.children(view.tagName)
      if model.id > ele.id
        return $(ele).before(view.render().el)

    @$el.append(view.render().el)

  remove: (model) =>
    if @selectedQuestion == model.id.toString()
      @selectedQuestion = undefined
    # console.log("remove: #{@selectedQuestion}")
    view = @childViews[model.id]
    view.$el.remove()
    delete @childViews[model.id]

  prepend: (model) =>
    view = @newQuestionView(model)
    @childViews[model.id] = view
    @$el.prepend(view.render().el)

  append: (model) =>
    view = @newQuestionView(model)
    @childViews[model.id] = view
    @$el.append(view.render().el)

  addAll: =>
    @$el.empty()
    @collection.each(@append)

    if location.hash
      targetId = location.hash.substring(1)
      @toggleView($("##{targetId}")[0])


  render: =>
    @

  reset: (data) =>
    @collection.reset(data)

  fetch: =>
    @collection.fetch()



