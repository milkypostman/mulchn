define ['jquery', 'backbone', 'bootstrap'], ($, Backbone) ->

  class LoginDialog extends Backbone.View
    loginDialog: '<div class="modal" id="loginDialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" style="display: none;">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">�</button>
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
    
    render: =>
      $("#content").append(@loginDialog)
      $('#loginDialog .btn-primary').click(-> window.location.href = "/login/")
      $("#loginDialog").modal('show')


