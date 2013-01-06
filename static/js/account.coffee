class Account
  instance = null

  constructor: () ->
    if instance != null
      throw new Error("Cannot instantiate more than one #{name}, use #{name}.getInstance()")
    @initialize()

  initialize: ->
    data = $.parseJSON($("#account_id").html())
    if data
      @id = data.id
      @admin = data.admin


  @getInstance = =>
    if instance == null
      instance = new Account()

    instance

