class QuestionView extends Backbone.View
  questionTmpl: _.template($("#question-template").html())

  tagName: "div"

  events: {
    "click .rest>.answers>.answer": "vote"
    "click .footer .delete": "delete"
    "click .rest": "nothing"
  }

  active: false

  constructor: (config) ->
    @active = config.active if config.active
    super config

  initialize: (config) ->
    @model.on("change", @render)
    @tagName = config.tagName if config.tagName
    _.each(config.classes, (c) => @classes.push(c))


  delete: (event) =>
    console.log("delete")
    question = $(event.currentTarget).closest(".question")
    new Dialog({
      closeButtonText: "Cancel"
      primaryButtonText: "Delete"
      title: "Delete Question?"
      content: "<p>Are you sure you want to delete the question: <blockquote>#{@model.get("text")}</blockquote></p>"
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


  nothing: (event) =>
    event.stopImmediatePropagation()


  vote: (event) =>
    answer = event.currentTarget.id

    @model.save({vote: answer, position:window.geoLocation.position}, {
      wait: true
      url: "/v1/question/vote"
      complete: =>
          $("##{answer}").removeClass("working")
      error: (model, response) =>

        if response.status == 401
          model.unset("vote")

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

  classes: ["question"]
  
  attributes: =>
    classes = @classes
    if @active
      classes.push("active")
    {id: @model.id, class: (c for c in classes).join(" ")}
    

  collapse: (callback) =>
    @$el.children(".question .rest").slideUp( (event) =>
      @active = false
      @$el.removeClass("active")
      callback(event) if callback
      )

    @removeMap() if @removeMap


  createMap: () =>
    # creates a new map element and returns it
    # element is created as a child of div.map
    # console.log("createMap")
    
    restDiv = @$el.children(".rest")
    mapDiv = restDiv.find(".map")
    if restDiv.css('display') == 'none'
      restDiv.css('visibility', 'hidden').show()
      mapDivWidth = mapDiv.innerWidth()
      restDiv.css('visibility', 'visible').hide()
    else
      mapDivWidth = mapDiv.innerWidth()
      
    width=mapDivWidth*.8
    height=width*1/2

    projection = d3.geo.albersUsa()
      .scale(width)
      .translate([0,0])

    path = d3.geo.path()
      .projection(projection);

    svg = d3.select(mapDiv.get()[0]).append("svg")
      .attr("width", width)
      .attr("height", height);


    g = svg.append("g")
      .attr("transform", "translate(#{width / 2},#{height / 2})")
      .append("g")

    g_us = g.append("g")
      .attr("id", "states");

    g_dots = g.append("g")
      .attr("id", "circles");

    radius = 4
    strokewidth = 1.5
    centered = null
    r = radius

    click = (d) =>
      x = 0
      y = 0
      k = 1
      spd = 1200

      if (d && centered != d.id) 
        centroid = path.centroid(d)

        x = -centroid[0]
        y = -centroid[1]

        bounds = path.bounds(d)

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
        spd = 600
        
        centered = d.id;
      else
        r = radius;
        centered = null;
      
      g_us.selectAll("path")
        .classed("active", centered && (d) => d.id == centered )

      trans = g.transition()
        .duration(1000)
        .attr("transform", "scale(#{k})translate(#{x},#{y})")
        .selectAll("path.state")
        .style("stroke-width", "#{strokewidth / k}px")

      g_dots.selectAll("circle")
        .transition()
        .duration(spd)
        .attr("r", r)
        

    d3.json("/static/us.json", (us) =>
      g_us.selectAll("path")
         .data(topojson.object(us, us.objects.states).geometries)
         .enter().append("path")
         .style("stroke-width", "#{strokewidth}px")
         .classed("active", centered && (d) => d.id == centered )
         .classed("state", true)
         .attr("d", path)
         .on("click", click)

  
      )

    @updateMap = =>
      # console.log("updateMap")

      g_dots.selectAll("circle")
        .data(=> @model.get("geo"))
        .attr("class", (d) => "dot color_#{d.id}")
        .attr("cx", (d) -> path.centroid(d)[0])
        .attr("cy", (d) -> path.centroid(d)[1])
        .attr("r", r)
        .enter().append("circle")
        .attr("class", (d) => "dot color_#{d.id}")
        .attr("cx", (d) -> path.centroid(d)[0])
        .attr("cy", (d) -> path.centroid(d)[1])
        .attr("r", r)


    @removeMap = =>
      # console.log("removeMap")
      $(svg[0]).slideUp(-> $(@).remove())
      @map = undefined
      @updateMap = undefined

    @updateMap()

    svg[0]

  addMap: =>
    # console.log("addMap")

    # don't add the map unless we have voted and have data
    if not @model.get("vote") or not @model.get("geo").length > 0
      return
      
    restDiv = @$el.children(".rest")
    mapDiv = restDiv.find(".map")

    if @map
      mapDiv.html(@map)
      @updateMap()
      mapDiv.prepend("<div class=\"header\"><h5>Map Data</h5></div>")
    else
      # console.log(mapDiv)
      @map = (svg = @createMap())
      mapDiv.html(@map)
      mapDiv.prepend("<div class=\"header\"><h5>Map Data</h5></div>")
  
 
  expand: (callback) =>
    @active = true
    @addMap()

    @$el.addClass("active")
    @$el.children(".rest").slideDown(callback)



  addTooltips: =>
    $(".answer .fill .label").tooltip()
    $(".followees .progress .bar").tooltip()


  render: =>
    # console.log('render')
    @$el.html(@questionTmpl({
      account: window.account
      question: @model
      active: @active
      }))


    @addTooltips()

    if @active
      @addMap()

    @




