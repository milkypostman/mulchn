// Generated by CoffeeScript 1.4.0
(function() {

  define(['jquery'], function($) {
    var User, instance;
    instance = null;
    User = (function() {
      var _this = this;

      function User() {
        if (instance !== null) {
          throw new Error("Cannot instantiate more than one " + name + ", use " + name + ".getInstance()");
        }
        this.initialize();
      }

      User.prototype.initialize = function() {
        return this.id = $("#userid").html();
      };

      User.getInstance = function() {
        if (instance === null) {
          instance = new User();
        }
        return instance;
      };

      return User;

    }).call(this);
    return User.getInstance();
  });

}).call(this);