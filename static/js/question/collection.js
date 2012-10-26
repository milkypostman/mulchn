// Generated by CoffeeScript 1.4.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'lodash', 'backbone', 'question/model'], function($, _, Backbone, QuestionModel) {
    var QuestionCollection;
    return QuestionCollection = (function(_super) {

      __extends(QuestionCollection, _super);

      function QuestionCollection() {
        this.update = __bind(this.update, this);

        this.updateOrAdd = __bind(this.updateOrAdd, this);
        return QuestionCollection.__super__.constructor.apply(this, arguments);
      }

      QuestionCollection.prototype.model = QuestionModel;

      QuestionCollection.prototype.url = '/v1/questions/';

      QuestionCollection.prototype.updateOrAdd = function(collection, response) {
        return _.each(response, function(ele) {
          return collection.get(ele._id).set(ele);
        });
      };

      QuestionCollection.prototype.update = function() {
        return this.fetch({
          add: true,
          success: this.updateOrAdd
        });
      };

      return QuestionCollection;

    })(Backbone.Collection);
  });

}).call(this);
