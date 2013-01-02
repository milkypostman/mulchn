class User
  instance = null

  constructor: () ->
    if instance != null
      throw new Error("Cannot instantiate more than one #{name}, use #{name}.getInstance()")
    @initialize()

  initialize: ->
    @id = $("#userid").html()


  @getInstance = =>
    if instance == null
      instance = new User()

    instance

