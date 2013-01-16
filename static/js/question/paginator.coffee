class QuestionPaginator extends Backbone.View
  tagName: "div"
  attributes: {id: "paginator", class:"paginator"}

  template: _.template($("#paginator-template").html())

  events: {
    'click a#next': 'nextPage'
    'click a#prev': 'prevPage'
    }

  nextPage: (e) =>
    e.preventDefault()
    window.app.navigate("/#{@collection.page + 1}", {trigger: true})

  prevPage: (e) =>
    e.preventDefault()
    window.app.navigate("/#{@collection.page - 1}", {trigger: true})

  initialize: () =>
    if @collection
      @collection.on("reset", @render)

  render: =>
    @$el.html(@template(@collection.info()))
    @
