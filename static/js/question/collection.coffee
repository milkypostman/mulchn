class QuestionCollection extends Backbone.Collection
  model: QuestionModel

  # the type of the request (GET by default)
  type: 'GET',

  # the type of reply (jsonp by default)
  dataType: 'jsonp',

  # the URL (or base URL) for the service
  url: =>
    if @page
      "v1/questions?page=#{@page}"
    else
      "v1/questions"
      
    

  info: => {
    'page': @page
    'perPage': @.length
    'totalPages': @totalPages
    'firstPage': 1
    'lastPage': @totalPages
    }
  
  parse: (response) =>
    @totalPages = response.numPages
    return response.questions

  updateOrAdd: (collection, response) =>
    _.each(response, (ele) ->
      collection.get(ele.id).set(ele))


  update: =>
    @fetch({add:true, success: @updateOrAdd})





