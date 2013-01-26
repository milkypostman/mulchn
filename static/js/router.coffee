class Router extends Backbone.Router
  routes: {
    "q/:question_id": "question"
    "t/:tag_name": "tag"
    "t/:tag_name/:page": "tag"
    "u/:username/unanswered": "user_unanswered"
    "u/:username/unanswered/:page": "user_unanswered"
    "add": "add"
    "new/:page": "new"
    "new": "new"
    ":page": "questions"
    "": "questions"
  }

  questionsList: (page, base_url) ->
    if not page
      page = 1
    else
      page = parseInt(page)

    console.log("questions:#{page}")

    questionCollection = new QuestionCollection()
    questionCollection.base_url = base_url
    
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


  user_unanswered: (username, page) ->
    document.title = "#{username} unanswered : Mulchn"

    # if page is present but not an integer, ignore this page
    if page and not parseInt(page)
      return

    @questionsList(page, "/u/#{username}/unanswered")  

  
  questions: (page) ->
    document.title = "questions feed : Mulchn"

    # if page is present but not an integer, ignore this page
    if page and not parseInt(page)
      return

    @questionsList(page, '')  

  

  tag: (tag_name, page) ->
    console.log("tag: #{tag_name}")
    document.title = "#{tag_name} : Mulchn"

    @questionsList(page, "/t/#{tag_name}")  


  new: (page) ->
    console.log("new: #{page}")

    document.title = "newest : Mulchn"
    @questionsList(page, '/new')  


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
    document.title = "create question : Mulchn"
    questionAdd = new QuestionAdd()
      




