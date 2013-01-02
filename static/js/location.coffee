instance = null

class Location
  constructor: () ->
    if instance != null
      throw new Error("Cannot instantiate more than one #{name}, use #{name}.getInstance()")
    @initialize()

  updatePosition: (position) ->
    @position = position

  initialize: ->
    if navigator.geolocation
      navigator.geolocation.getCurrentPosition((position) => @position = position)

  @getInstance = =>
    if instance == null
      instance = new Location()

    instance

Location = Location.getInstance()
