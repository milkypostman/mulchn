define ['jquery', 'dialog', 'bootstrap'], ($, Dialog) ->

  class LoginDialog extends Dialog

    title: "Login Required"
    content: "A valid login is required."
    primaryButtonText: "Login"

    ok: =>
      window.location.href = "/login/"
      
      
