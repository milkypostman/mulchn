class Router extends Backbone.Router
  routes: {
    "q/:question_id": "question"
    "t/:tag_name": "tag"
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
    questionCollection = new QuestionCollection()
    questionList = new QuestionList({collection:questionCollection})

    $("#content").append(questionList.el)

    if $("#json_data").html()
      questionCollection.reset($.parseJSON($("#json_data").html()))
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
      




