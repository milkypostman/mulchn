define ->
  instance = null
  
  class Location
    constructor: () ->
      if instance != null
        throw new Error("Cannot instantiate more than one #{name}, use #{name}.getInstance()")
      @initialize()

    updatePosition: (position) ->
      @position = position

    initialize: ->
      _this = @
      if navigator.geolocation
        navigator.geolocation.getCurrentPosition((position) -> _this.position = position)

    @getInstance = =>
      if instance == null
        instance = new Location()

      instance

  Location.getInstance()
  