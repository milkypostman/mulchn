class QuestionCollection extends Backbone.Collection
  model: QuestionModel

  # the type of the request (GET by default)
  type: 'GET',

  # the type of reply (jsonp by default)
  dataType: 'jsonp',

  base_url: "",

  # the URL (or base URL) for the service
  url: (page) =>
    if page
      "#{@base_url}/#{page}"
    else if @page
      "#{@base_url}/#{@page}"
    else
      "#{@base_url}/"
      

  info: => {
    'page': @page
    'perPage': @.length
    'totalPages': @totalPages
    'firstPage': 1
    'lastPage': @totalPages
    }
  
  parse: (response) =>
    @totalPages = response.numPages
    response.questions

  updateOrAdd: (collection, response) =>
    _.each(response, (ele) ->
      collection.get(ele.id).set(ele))


  update: =>
    @fetch({add:true, success: @updateOrAdd})





