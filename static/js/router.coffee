class Router extends Backbone.Router
  routes: {
    "question/:question_id/": "question"
    "question/add/": "add"
    ":question/": "root"
    ":hash": "root"
    "": "root"
  }

  root: (hash) ->
    # Fix for hashes in pushState and hash fragment
    if (hash && !@_alreadyTriggered)

      # Reset to home, pushState support automatically converts hashes
      Backbone.history.navigate("", false);

      # Trigger the default browser behavior
      location.hash = hash;

      # Set an internal flag to stop recursive looping
      @_alreadyTriggered = true;
      return

    console.log("root")
    questionList = new QuestionList()
    questionList.reset()
    $("#content").html(questionList.render().el)

  question: (question_id) ->
    model = new QuestionModel({id: question_id})
    question = new QuestionView({model: model, active: true});
    setInterval((=> model.fetch()), 10000);
    model.fetch()
    $("#content").html(question.el)
    console.log(question)

  add: ->
    console.log("add")
    questionAdd = new QuestionAdd()
      




