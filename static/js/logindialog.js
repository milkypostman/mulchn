// Generated by CoffeeScript 1.4.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'backbone', 'bootstrap'], function($, Backbone) {
    var LoginDialog;
    return LoginDialog = (function(_super) {

      __extends(LoginDialog, _super);

      function LoginDialog() {
        this.render = __bind(this.render, this);

        this.remove = __bind(this.remove, this);
        return LoginDialog.__super__.constructor.apply(this, arguments);
      }

      LoginDialog.prototype.el = '<div class="modal" id="loginDialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" style="display: none;">\
      <div class="modal-header">\
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>\
        <h3 id="loginDialogHeader">Login Required</h3>\
      </div>\
      <div class="modal-body">\
        <p id="loginDialogBody">Voting requires a valid login.</p>\
      </div>\
      <div class="modal-footer">\
        <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>\
        <button class="btn btn-primary">Login</button>\
      </div>\
    </div>';

      LoginDialog.prototype.remove = function() {
        console.log("remove");
        return this.$el.remove();
      };

      LoginDialog.prototype.render = function() {
        $("#content").append(this.el);
        $('#loginDialog .btn-primary').click(function() {
          return window.location.href = "/login/";
        });
        this.$el.on("hidden", this.remove);
        return this.$el.modal('show');
      };

      return LoginDialog;

    })(Backbone.View);
  });

}).call(this);
