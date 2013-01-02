class LoginDialog extends Dialog

  title: "Login Required"
  content: "A valid login is required."
  primaryButtonText: "Login via Twitter"

  ok: =>
    window.location.href = "/login/twitter/"
      
      
