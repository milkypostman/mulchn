define ['jquery', 'lodash', 'backbone', 'location', 'question/collection', 'question/model'], ($, _, Backbone, Location, QuestionCollection, QuestionModel) ->

  class QuestionModelView extends Backbone.View
    questionTmpl: _.template('
      <div class="question-header">
        <span class="question-text"><%= question.get("question") %></span>
          <% if (question.get("vote")) { %>
          <div class="vote-count pull-right"><%= question.votes() %></div>
          <div class="vote-count-prefix pull-right">results:</div>
          <% } else { %>
          <div class="vote-info pull-right">no choice selected</div>
          <% } %>
      </div>
      <ul class="answers slicklist" <% if (active) { %>style="display: block;"<% } %> >
      <% for (_i=0, _answers=question.get("answers"), _len=_answers.length; _i < _len; _i++) { answer = _answers[_i];  %>
        <li class="answer <% if (answer._id == question.get("vote")) { %>vote<% } %>" id="<%= answer._id %>">
          <i class="icon-ok"></i> <%= answer.answer %>
          <div class="vote-count pull-right"><%= answer.votes | 0 %></div>
          <div class="vote-count-prefix pull-right">.</div>
          <div class="vote-percent pull-right"><%= Math.round((answer.votes | 0) / (question.votes() | 1) * 100) %>%</div>
        </li>
      <% } %>
      </ul>')

    tagName: "li"


    events: {
      "click .answer": "vote"
    }

    active: false

    initialize: =>
      @model.on("change", @render)


    vote: (event) =>
      answer = event.currentTarget.id
      @model.save({vote: answer, position:Location.position}, {
        url: "/v1/question/vote/"
        error: (model, response) ->
          @location.href = "/login/twitter/"
          model.unset("vote")
      })
      false

    
    attributes: ->
      classes = ["question"]
      if @active
        classes.push("active")
      {id: @model.id, class: (c for c in classes).join(" ")}
      

    collapse: =>
      @active = false
      @$el.removeClass("active")
      @$el.children(".answers").slideUp()

    expand: =>
      @active = true
      @$el.addClass("active")
      @$el.children(".answers").slideDown()

    render: =>
      @$el.html(@questionTmpl({
        question: @model
        active: @active
        }))
      return @


  class QuestionCollectionView extends Backbone.View
    questionTmpl: _.template('
    <li class="question" id="<%= question.id %>">
      <div class="question-header">
        <span class="question-text"><%= question.get("question") %></span>
          <% if (question.get("vote")) { %>
          <div class="vote-count pull-right"><%= question.votes() %></div>
          <div class="vote-count-prefix pull-right">results:</div>
          <% } else { %>
          <div class="vote-info pull-right">no choice selected</div>
          <% } %>
      </div>
    </div>
      <ul class="answers slicklist">
        <%= answers %>
      </ul>
    </li>')


    tagName: "ul"

    attributes: {id: "questions", class:"questions slicklist"}
    
    events: {
      "click .question": "toggleQuestion"
      }


    initialize: =>
      console.log("initialize")
      @collection = new QuestionCollection()
      @collection.on("add", @add)
      @collection.on("reset", @addAll)
      @selectedQuestion = undefined
      @childViews = {}

      
    toggleQuestion: (event) =>
      targetId = event.currentTarget.id

      if @selectedQuestion
        @childViews[@selectedQuestion].collapse()

      if targetId == @selectedQuestion
        @selectedQuestion = undefined
      else
        @childViews[targetId].expand()
        @selectedQuestion = targetId

    add: (model) =>
      view = new QuestionModelView({model: model})
      @childViews[model.id] = view
      @$el.append(view.render().el);

    addAll: =>
      @collection.each(@add)
      @render()

    render: =>
      $("#content").html(@el)



