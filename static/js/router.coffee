class Router extends Backbone.Router
  routes: {
    "question/add/": "add"
    "": "root"
  }

  root: ->
    console.log("root")
    questionList = new QuestionList()
    questionList.reset()
    questionList.render()

  add: ->
    console.log("add")
    questionAdd = new QuestionAdd()
      




