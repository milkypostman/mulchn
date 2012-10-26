define ['jquery', 'lodash', 'backbone', 'bootstrap'], ($, _, Backbone) ->

  class Dialog extends Backbone.View
    elTemplate: '<div class="modal fade hide" id="<%= prefix %>Dialog" role="dialog" aria-labelledby="<%= prefix %>Label" aria-hidden="true">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
        <h3 id="<%= prefix %>Label"><%= title %></h3>
      </div>
      <div class="modal-body">
        <%= content %>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true"><%= closeButtonText %></button>
          <% if (primaryButtonText) { %>
          <button class="btn btn-primary"><%= primaryButtonText %></button>
          <% } %>
      </div>
    </div>'

    ok: =>

    okWrap: =>
      @ok(@$el)

    title: "Title"

    content: "Content"

    closeButtonText: "Close"

    primaryButtonText: undefined

    prefix: ""

    initialize: (options) =>
      @ok = options.ok or @ok
      @title = options.title or @title
      @content = options.content or @content
      @closeButtonText = options.closeButtonText or @closeButtonText
      @primaryButtonText = options.primaryButtonText or @primaryButtonText
      @prefix = options.prefix or @prefix
      @setElement(_.template(@elTemplate, {
        prefix: @prefix,
        title: @title,
        content: @content,
        closeButtonText: @closeButtonText,
        primaryButtonText: @primaryButtonText,
        }))
      @$el.find(".btn-primary").click(@okWrap)
      @$el.on("hidden", @remove)
      @$el.on("shown", ->
        $($(".modal-footer button").first()).focus()
        )
        

    remove: =>
      @$el.remove()

    render: =>
      $("#content").append(@el)
      @$el.modal('show')


