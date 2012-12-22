require ['config', 'main'], () ->
  require ['question/list'], (QuestionList) ->
    questionList = new QuestionList()
    questionList.reset()
    questionList.render()

