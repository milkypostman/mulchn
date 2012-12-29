class QuestionItem extends Backbone.View
  questionTmpl: _.template($("#question-template").html())

  tagName: "li"


  events: {
    "click .answer": "vote"
    "click .delete": "delete"
  }

  active: false

  initialize: =>
    @model.on("change", @render)

  delete: (event) =>
    question = $(event.currentTarget).closest(".question")
    new Dialog({
      closeButtonText: "Cancel"
      primaryButtonText: "Delete"
      title: "Delete Question?"
      content: "<p>Are you sure you want to delete the question: <blockquote>#{@model.get("question")}</blockquote></p>"
      ok: (dialog) =>
        @model.destroy({
          wait: true
          success: ->
            dialog.modal('hide')
          error: ->
            dialog.modal('hide')
          })
    }).render()
    false


  vote: (event) =>
    answer = event.currentTarget.id
    @model.save({vote: answer, position:Location.position}, {
      wait: true
      url: "/v1/question/vote/"
      error: (model, response) =>

        if response.status == 401
          model.unset("vote")
          $("##{answer}").removeClass("working")

          new LoginDialog().render()

        else if response.status == 404
          new Dialog({
            closeButtonText: "Close"
            title: "Question Missing"
            content: "<p>Selected question no longer exists.</p>"
          }).render()
          @remove(model)

        else
          new Dialog({
            closeButtonText: "Close"
            title: "Unknown Error"
            content: "<p>An unknown error has occurred.</p>"
          }).render()

    })
    $("##{answer}").addClass("working")
    false

  
  attributes: ->
    classes = ["question"]
    if @active
      classes.push("active")
    {id: @model.id, class: (c for c in classes).join(" ")}
    

  collapse: =>
    @active = false
    @$el.removeClass("active")
    @$el.children(".question-rest").slideUp()

  expand: =>
    @active = true
    @$el.addClass("active")
    @$el.children(".question-rest").slideDown()

  render: =>
    @$el.html(@questionTmpl({
      user: User.id
      question: @model
      active: @active
      }))

    @



class QuestionList extends Backbone.View
  tagName: "ul"

  attributes: {id: "questions", class:"questions slicklist"}
  
  events: {
    "click .question": "toggleQuestion"
    }


  initialize: =>
    @collection = new QuestionCollection()
    @collection.on("add", @add)
    @collection.on("reset", @addAll)
    @collection.on("remove", @remove)
    @selectedQuestion = undefined
    @childViews = {}

    setInterval(@collection.update, 10000);

  toggleQuestion: (event) =>
    targetId = event.currentTarget.id

    if @selectedQuestion
      @childViews[@selectedQuestion].collapse()

    if targetId == @selectedQuestion
      @selectedQuestion = undefined
    else
      @childViews[targetId].expand()
      @selectedQuestion = targetId


  # this is specialized to add in the proper position
  add: (model) =>
    view = new QuestionItem({model: model})
    @childViews[model.id] = view
    for ele in @$el.children(view.tagName)
      if model.id > ele.id
        return $(ele).before(view.render().el)

    @$el.append(view.render().el)

  remove: (model) =>
    if @selectedQuestion == model.id
      @selectedQuestion = undefined
    view = @childViews[model.id]
    view.$el.remove()
    delete @childViews[model.id]

  prepend: (model) =>
    view = new QuestionItem({model: model})
    @childViews[model.id] = view
    @$el.prepend(view.render().el)

  append: (model) =>
    view = new QuestionItem({model: model})
    @childViews[model.id] = view
    @$el.append(view.render().el)

  addAll: =>
    @$el.empty()
    @collection.each(@append)

  render: =>
    $("#content").html(@el)

    @

  reset: =>
    @collection.fetch()



