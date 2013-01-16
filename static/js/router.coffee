class Router extends Backbone.Router
  routes: {
    "q/:question_id": "question"
    "t/:tag_name": "tag"
    "add": "add"
    ":page": "root"
    "": "root"
  }

  root: (page) ->

    console.log("root")

  
    if not page
      page = 1
    else
      page = parseInt(page)

    questionCollection = new QuestionCollection()
    questionList = new QuestionList({collection:questionCollection})
    questionPaginator = new QuestionPaginator({collection:questionCollection})
    questionCollection.page = page

    $("#content").html(questionList.el)
    $("#content").append(questionPaginator.el)

    if $("#json_data").html()

      questionCollection.reset(questionCollection.parse($.parseJSON($("#json_data").html())))
      $("#json_data").remove()
    else
      questionCollection.fetch()

  

  tag: (tag_name) ->
    console.log("tag: #{tag_name}")
    tagCollection = new QuestionCollection()
    tagCollection.url="/v1/tag/#{tag_name}"

    questionList = new QuestionList({collection: tagCollection})
    $("#content").append(questionList.el)

    if $("#json_data").html()
      tagCollection.reset($.parseJSON($("#json_data").html()))
    else
      tagCollection.fetch()


  question: (question_id) ->
    console.log("question: #{question_id}")
    
    model = new QuestionModel({id: question_id})
    question = new QuestionView({model: model, active: true});
    $("#content").append(question.el)

    setInterval((=> model.fetch()), 10000);
    if $("#json_data").html()
      model.set($.parseJSON($("#json_data").html()))
    else
      model.fetch()

    model.on('destroy', -> window.location = "/")

  add: ->
    console.log("add")
    questionAdd = new QuestionAdd()
      




