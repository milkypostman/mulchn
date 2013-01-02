class QuestionItem extends Backbone.View
  questionTmpl: _.template($("#question-template").html())

  tagName: "li"


  events: {
    "click .rest>.answers>.answer": "vote"
    "click .answers .delete": "delete"
    "click .rest": "nothing"
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


  nothing: => false

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
    

  collapse: (callback) =>
    @active = false
    @$el.removeClass("active")
    @$el.children(".question .rest").slideUp(callback)
    if @map
      $(@map).slideUp(-> $(@).remove())
      @map = undefined

  expand: (callback) =>
    @active = true
    @$el.addClass("active")
    rest = @$el.children(".rest")
    rest.slideDown(callback)

    if @model.get("vote")
      
      d3.json("/static/us.json", (us) =>

        div = rest.children(".map")

        width=rest.innerWidth()*.8
        height=width*2/3

        projection = d3.geo.albersUsa()
          .scale(width)
          .translate([0,0])
          # .translate([width/2, height/2]);

        path = d3.geo.path()
          .projection(projection);

        svg = d3.select(div.get()[0]).append("svg")
          .attr("width", width)
          .attr("height", height);

        g = svg.append("g")
          .attr("transform", "translate(#{width / 2},#{height / 2})")
          .append("g")
          .attr("id", "states");

        @map = svg[0]

        geo = @model.get("geo")

        centered = null

        radius = 2

        console.log(projection.scale())
        click = (d) ->
          x = 0
          y = 0
          k = 1
          r = radius

          # if (d && centered == d)
          #   projection.scale(width)
          #   projection.translate([width/2, height/2])
          # else

          #   scale = projection.scale()
          #   projection.scale(width*4)

          #   centroid = path.centroid(d)
          #   translate = projection.translate()
          #   projection.translate([
          #     translate[0] - centroid[0] + width / 2,
          #     translate[1] - centroid[1] + height / 2
          #   ])
          #   centered = d;

          # g.selectAll("path")
          #   .transition()
          #   .duration(1000)
          #   .attr("d", path)
          

          if (d && centered != d) 
            centroid = path.centroid(d)
            console.log(centroid)

            x = -centroid[0]
            y = -centroid[1]

            bounds = path.bounds(d)
            console.log(bounds)

            # upperleft.x = bounds[0][0]
            # upperleft.y = bounds[0][1]
            # bottomright.x = bounds[1][0]
            # bottomright.y = bounds[1][1]

            ww = 2*Math.max(centroid[0] - bounds[0][0], bounds[1][0] - centroid[0])
            hh = 2*Math.max(centroid[1] - bounds[0][1], bounds[1][1] - centroid[1])

            xk = width/(ww * 1.2)
            yk = height/(hh * 1.1)

            k = Math.min(xk, yk)
            r = radius / k
            
            centered = d;
          else
            centered = null;
          

          g.selectAll("path")
              .classed("active", centered && (d) -> d == centered )

          g.transition()
              .duration(1000)
              .attr("transform", "scale(#{k})translate(#{x},#{y})")
              .selectAll("path")
              .style("stroke-width", "#{1.5 / k}px")
              .selectAll("circle.dot")
              .attr("r", r)
              

        g.selectAll("path")
          .data(topojson.object(us, us.objects.states).geometries)
          .enter().append("path")
          .style("stroke-width", "1.5px")
          .attr("class", "state")
          .attr("d", path)
          .on("click", click)
        g.selectAll("rect.boxer")
          .data(topojson.object(us, us.objects.states).geometries)
          .enter().append("rect")
          .attr("class", "boxer")
          .attr("r", 5)
          .attr("x", (d) ->
            bounds = path.bounds(d)
            bounds[0][0]
            )
          .attr("y", (d) ->
            bounds = path.bounds(d)
            bounds[0][1]
            )
            
          .attr("width", (d) ->
            bounds = path.bounds(d)
            bounds[1][0] - bounds[0][0]
            )
          .attr("height", (d) ->
            bounds = path.bounds(d)
            bounds[1][1] - bounds[0][1]
            )

        g.selectAll("circle")
          .data(geo)
          .enter().append("circle")
          .attr("class", "dot")
          .attr("cx", (d) -> path.centroid(d)[0])
          .attr("cy", (d) -> path.centroid(d)[1])
          .attr("r", 2)
        )


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
    @toggleView(event.currentTarget.id)

  toggleView: (targetId) =>
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

    if location.hash
      @toggleView(location.hash.substring(1))


  render: =>
    $("#content").html(@el)

    @

  reset: =>
    @collection.fetch()



