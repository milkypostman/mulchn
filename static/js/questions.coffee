# {% block content %}
# <ul class="questions slicklist">
#   {% for question in questions %}
#   <li class="question" id="{{ question._id }}">
#     <div class="question-text">{{ question.question }}</div>
#     <ul class="answers slicklist">
#       {% for answer in question.answers %}
#       <li class="answer" id="{{ answer._id }}">
#         <i class="icon-ok"></i> {{ answer.answer }}
#       </li>
#       {% endfor %}
#     </ul>
#   </li>
#   {% endfor %}
# </ul>
# {% endblock %}

_.templateSettings = {
  interpolate: /\{\{(.+?)\}\}/g,
  evaluate: /\{\%(.+?)\%\}/g,
}
                
        


questionTmpl = _.template('
<li class="question" id="{{ question._id }}">
  <div class="question-text">{{ question.question }}</div>
  <ul class="answers slicklist">
    {{ answers }}
  </ul>
</li>')

answerTmpl = _.template('
<li class="answer {{ extra_class }}" id="{{ answer._id }}">
  <i class="icon-ok"></i> {{ answer.answer }}
  {{ percent }}
</li>')

percentTmpl = _.template('
<div class="vote-percent pull-right">{{ percent }}</div>')

questionHtml = (question) ->
  if question.user_answer_id
    totalVotes = _.reduce(question.answers
      (tot, ans) -> tot + ans.votes.length
      0)
  questionTmpl({
    question:question,
    answers:(answerTmpl({
      answer:ans
      percent: if question.user_answer_id then percentTmpl({ percent: ans.votes.length / totalVotes * 100 }) else ""
      extra_class: if question.user_answer_id == ans._id then "vote" else ""
      }) for ans in question.answers).join ''
  })

questionsHtml = (questions) ->
  (questionHtml(q) for q in questions).join ''

geoPosition = undefined

loginDialog = '<div class="modal" id="loginDialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" style="display: none;">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="loginDialogHeader">Login Required</h3>
  </div>
  <div class="modal-body">
    <p id="loginDialogBody">Voting requires a valid login.</p>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
    <button class="btn btn-primary">Login</button>
  </div>
</div>'

vote = (evt) ->
  target = evt.currentTarget

  answer = $(target)
  answer.addClass("working")
  question = answer.closest(".question")

  data = {question:question.attr("id"), answer:answer.attr("id")}

  if geoPosition
    data.latitude = geoPosition.coords.latitude
    data.longitude = geoPosition.coords.longitude
    data.accuracy = geoPosition.coords.accuracy
    data.speed = geoPosition.coords.speed
    data.geotimestamp = geoPosition.timestamp

  $.ajax({
    url: "/v1/question/vote/"
    type: "POST"
    data: data
    dataType: 'json'
    context: question
    success: (data) ->
      updateQuestion(data)
    error: (error) ->
      data = $.parseJSON(error.responseText)
      if error.status == 401
        $('#loginDialog').modal('show')
      answer.removeClass('working')
    })
    
  return false

updateQuestion = (data) ->
  if data.user_answer_id
    totalVotes = _.reduce(data.answers
      (tot, ans) -> tot + ans.votes.length
      0)

    ($("##{a._id} .vote-percent").html(a.votes.length / totalVotes * 100) for a in data.answers)
    $("##{data._id} .answer").removeClass("vote")
    $("##{data._id} .answer").removeClass("working")
    $("##{data.user_answer_id}").addClass("vote")
  

selQuestion = undefined

toggleQuestion = (evt) ->
  target = evt.currentTarget
  jtarget = $(target)
  if selQuestion == target
    jtarget.children(".answers").slideUp()
    jtarget.removeClass("active")
    selQuestion = undefined;
  else 
    if selQuestion
      selQuestion.children(".answers").slideUp()
      selQuestion.removeClass("active")
    jtarget.children(".answers").slideDown()
    jtarget.addClass("active")
    selQuestion = target
  return false

questions = '
  <ul id="questions" class="questions slicklist">
  </ul>'

$(window).load ->
  $('#content').append(questions)
  
  $.ajax({
    url: '/v1/questions/',
    success: (data) ->
      $('#questions').html(questionsHtml(data.questions))
      $('.question').click(toggleQuestion)
      $('.answer').click(vote)
    error: ->
      alert("ERROR")
    })

  $('#content').append(loginDialog)
  $('#loginDialog .btn-primary').click(-> window.location.href = "/login/")

  if navigator.geolocation
    navigator.geolocation.getCurrentPosition (position) -> geoPosition = position


        
        

