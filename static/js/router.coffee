class Router extends Backbone.Router
  routes: {
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
    questionList.render()
  
  add: ->
    console.log("add")
    questionAdd = new QuestionAdd()
      




