// Generated by CoffeeScript 1.4.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'lodash', 'backbone', 'user', 'location', 'dialog', 'logindialog', 'question/collection', 'question/model'], function($, _, Backbone, User, Location, Dialog, LoginDialog, QuestionCollection, QuestionModel) {
    var QuestionItem, QuestionList;
    QuestionItem = (function(_super) {

      __extends(QuestionItem, _super);

      function QuestionItem() {
        this.render = __bind(this.render, this);

        this.expand = __bind(this.expand, this);

        this.collapse = __bind(this.collapse, this);

        this.vote = __bind(this.vote, this);

        this["delete"] = __bind(this["delete"], this);

        this.initialize = __bind(this.initialize, this);
        return QuestionItem.__super__.constructor.apply(this, arguments);
      }

      QuestionItem.prototype.questionTmpl = _.template($("#question-template").html());

      QuestionItem.prototype.tagName = "li";

      QuestionItem.prototype.events = {
        "click .answer": "vote",
        "click .delete": "delete"
      };

      QuestionItem.prototype.active = false;

      QuestionItem.prototype.initialize = function() {
        return this.model.on("change", this.render);
      };

      QuestionItem.prototype["delete"] = function(event) {
        var question,
          _this = this;
        question = $(event.currentTarget).closest(".question");
        new Dialog({
          closeButtonText: "Cancel",
          primaryButtonText: "Delete",
          title: "Delete Question?",
          content: "<p>Are you sure you want to delete the question: <blockquote>" + (this.model.get("question")) + "</blockquote></p>",
          ok: function(dialog) {
            return _this.model.destroy({
              wait: true,
              success: function() {
                return dialog.modal('hide');
              },
              error: function() {
                return dialog.modal('hide');
              }
            });
          }
        }).render();
        return false;
      };

      QuestionItem.prototype.vote = function(event) {
        var answer,
          _this = this;
        answer = event.currentTarget.id;
        this.model.save({
          vote: answer,
          position: Location.position
        }, {
          wait: true,
          url: "/v1/question/vote/",
          error: function(model, response) {
            if (response.status === 401) {
              model.unset("vote");
              $("#" + answer).removeClass("working");
              return new LoginDialog().render();
            } else if (response.status === 404) {
              new Dialog({
                closeButtonText: "Close",
                title: "Question Missing",
                content: "<p>Selected question no longer exists.</p>"
              }).render();
              return _this.remove(model);
            } else {
              return new Dialog({
                closeButtonText: "Close",
                title: "Unknown Error",
                content: "<p>An unknown error has occurred.</p>"
              }).render();
            }
          }
        });
        $("#" + answer).addClass("working");
        return false;
      };

      QuestionItem.prototype.attributes = function() {
        var c, classes;
        classes = ["question"];
        if (this.active) {
          classes.push("active");
        }
        return {
          id: this.model.id,
          "class": ((function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = classes.length; _i < _len; _i++) {
              c = classes[_i];
              _results.push(c);
            }
            return _results;
          })()).join(" ")
        };
      };

      QuestionItem.prototype.collapse = function() {
        this.active = false;
        this.$el.removeClass("active");
        return this.$el.children(".question-rest").slideUp();
      };

      QuestionItem.prototype.expand = function() {
        this.active = true;
        this.$el.addClass("active");
        return this.$el.children(".question-rest").slideDown();
      };

      QuestionItem.prototype.render = function() {
        this.$el.html(this.questionTmpl({
          user: User.id,
          question: this.model,
          active: this.active
        }));
        return this;
      };

      return QuestionItem;

    })(Backbone.View);
    return QuestionList = (function(_super) {

      __extends(QuestionList, _super);

      function QuestionList() {
        this.reset = __bind(this.reset, this);

        this.render = __bind(this.render, this);

        this.addAll = __bind(this.addAll, this);

        this.append = __bind(this.append, this);

        this.prepend = __bind(this.prepend, this);

        this.remove = __bind(this.remove, this);

        this.add = __bind(this.add, this);

        this.toggleQuestion = __bind(this.toggleQuestion, this);

        this.initialize = __bind(this.initialize, this);
        return QuestionList.__super__.constructor.apply(this, arguments);
      }

      QuestionList.prototype.tagName = "ul";

      QuestionList.prototype.attributes = {
        id: "questions",
        "class": "questions slicklist"
      };

      QuestionList.prototype.events = {
        "click .question": "toggleQuestion"
      };

      QuestionList.prototype.initialize = function() {
        this.collection = new QuestionCollection();
        this.collection.on("add", this.add);
        this.collection.on("reset", this.addAll);
        this.collection.on("remove", this.remove);
        this.selectedQuestion = void 0;
        this.childViews = {};
        return setInterval(this.collection.update, 10000);
      };

      QuestionList.prototype.toggleQuestion = function(event) {
        var targetId;
        targetId = event.currentTarget.id;
        if (this.selectedQuestion) {
          this.childViews[this.selectedQuestion].collapse();
        }
        if (targetId === this.selectedQuestion) {
          return this.selectedQuestion = void 0;
        } else {
          this.childViews[targetId].expand();
          return this.selectedQuestion = targetId;
        }
      };

      QuestionList.prototype.add = function(model) {
        var ele, view, _i, _len, _ref;
        view = new QuestionItem({
          model: model
        });
        this.childViews[model.id] = view;
        _ref = this.$el.children(view.tagName);
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          ele = _ref[_i];
          if (model.id > ele.id) {
            return $(ele).before(view.render().el);
          }
        }
        return this.$el.append(view.render().el);
      };

      QuestionList.prototype.remove = function(model) {
        var view;
        if (this.selectedQuestion === model.id) {
          this.selectedQuestion = void 0;
        }
        view = this.childViews[model.id];
        view.$el.remove();
        return delete this.childViews[model.id];
      };

      QuestionList.prototype.prepend = function(model) {
        var view;
        view = new QuestionItem({
          model: model
        });
        this.childViews[model.id] = view;
        return this.$el.prepend(view.render().el);
      };

      QuestionList.prototype.append = function(model) {
        var view;
        view = new QuestionItem({
          model: model
        });
        this.childViews[model.id] = view;
        return this.$el.append(view.render().el);
      };

      QuestionList.prototype.addAll = function() {
        this.$el.empty();
        return this.collection.each(this.append);
      };

      QuestionList.prototype.render = function() {
        $("#content").html(this.el);
        return this;
      };

      QuestionList.prototype.reset = function() {
        return this.collection.fetch();
      };

      return QuestionList;

    })(Backbone.View);
  });

}).call(this);
