define ['jquery', 'backbone'], ($, Backbone) ->
  class Router extends Backbone.Router
    routes: {
      "question/add/": "add"
      "": "root"
    }

    root: ->
      console.log("root")
      require ['question/list'], (QuestionList) ->
        questionList = new QuestionList()
        questionList.reset()
        questionList.render()

    add: ->
      console.log("add")
      require ['jquery'], ($) ->
        clone_answer = (selector, maxId) ->
          elem = $(selector)
          
          # clone the input field
          new_input = elem.find(":input").clone(true)
          
          # determine which number we're dealing with
          curId = parseInt(new_input.attr("id").replace(/.*-(\d{1,4})/m, "$1"))
          newId = curId + 1
          
          # possible that we double tap the button; ignore
          return curId  if curId >= maxId
          id = new_input.attr("id").replace("-" + curId, "-" + (newId))
          placeholder = new_input.attr("placeholder").replace(newId, curId + 2)
          placeholder += " (optional)"  unless placeholder.endsWith("(optional)")
          new_input.attr(
            name: id
            id: id
            placeholder: placeholder
          ).val ""
          new_element = elem.clone(true)
          new_element.html new_input
          elem.after new_element
          
          # return the id we created
          newId
      
        maxFieldId = 4
      
        String::endsWith = (suffix) ->
          @indexOf(suffix, @length - suffix.length) isnt -1
      
        newId = clone_answer(".answers-input:last", maxFieldId)
        newId = clone_answer(".answers-input:last", maxFieldId) while newId < maxFieldId





