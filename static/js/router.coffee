class Router extends Backbone.Router
  routes: {
    "q/:question_id": "question"
    "add": "add"
    ":hash": "root"
    "": "root"
  }

  root: (hash) ->
    # Fix for hashes in pushState and hash fragment
    if (hash && @_alreadyTriggered != hash)

      # Reset to home, pushState support automatically converts hashes
      Backbone.history.navigate("", false);

      # Trigger the default browser behavior
      location.hash = hash;

      # Set an internal flag to stop recursive looping
      @_alreadyTriggered = hash;
      return

    console.log("root")
    questionList = new QuestionList()
    if $("#json_data").html()
      questionList.reset($.parseJSON($("#json_data").html()))
    else
      questionList.fetch()
    $("#content").html(questionList.render().el)

  question: (question_id) ->
    console.log("question")
    
    model = new QuestionModel({id: question_id})
    question = new QuestionView({model: model, active: true});
    $("#content").html(question.el)

    setInterval((=> model.fetch()), 10000);
    if $("#json_data").html()
      model.set($.parseJSON($("#json_data").html()))
    else
      model.fetch()

    model.on('destroy', -> window.location = "/")

  add: ->
    console.log("add")
    questionAdd = new QuestionAdd()
      




