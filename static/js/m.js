var Account, Dialog, GeoLocation, LoginDialog, QuestionAdd, QuestionCollection, QuestionList, QuestionModel, QuestionPaginator, QuestionView, Router,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

QuestionAdd = (function(_super) {

  __extends(QuestionAdd, _super);

  function QuestionAdd() {
    this.initialize = __bind(this.initialize, this);

    this.clone_answer = __bind(this.clone_answer, this);
    return QuestionAdd.__super__.constructor.apply(this, arguments);
  }

  QuestionAdd.prototype.clone_answer = function(selector, maxId) {
    var curId, elem, id, newId, new_element, new_input, placeholder;
    elem = $(selector);
    new_input = elem.find(":input").clone(true);
    curId = parseInt(new_input.attr("id").replace(/.*-(\d{1,4})/m, "$1"));
    newId = curId + 1;
    if (curId >= maxId) {
      return curId;
    }
    id = new_input.attr("id").replace("-" + curId, "-" + newId);
    placeholder = new_input.attr("placeholder").replace(newId, curId + 2);
    if (!placeholder.endsWith("(optional)")) {
      placeholder += " (optional)";
    }
    new_input.attr({
      name: id,
      id: id,
      placeholder: placeholder
    }).val("");
    new_element = elem.clone(true);
    new_element.html(new_input);
    elem.after(new_element);
    return newId;
  };

  QuestionAdd.prototype.initialize = function() {
    var maxFieldId, newId, _results;
    maxFieldId = 4;
    newId = this.clone_answer(".answers-input:last", maxFieldId);
    _results = [];
    while (newId < maxFieldId) {
      _results.push(newId = this.clone_answer(".answers-input:last", maxFieldId));
    }
    return _results;
  };

  return QuestionAdd;

})(Backbone.View);

Dialog = (function(_super) {

  __extends(Dialog, _super);

  function Dialog() {
    this.render = __bind(this.render, this);

    this.remove = __bind(this.remove, this);

    this.initialize = __bind(this.initialize, this);

    this.okWrap = __bind(this.okWrap, this);

    this.ok = __bind(this.ok, this);
    return Dialog.__super__.constructor.apply(this, arguments);
  }

  Dialog.prototype.elTemplate = '<div class="modal fade hide" id="<%= prefix %>Dialog" role="dialog" aria-labelledby="<%= prefix %>Label" aria-hidden="true">\
    <div class="modal-header">\
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>\
      <h3 id="<%= prefix %>Label"><%= title %></h3>\
    </div>\
    <div class="modal-body">\
      <%= content %>\
    </div>\
    <div class="modal-footer">\
      <button class="btn btn-close" data-dismiss="modal" aria-hidden="true"><%= closeButtonText %></button>\
        <% if (primaryButtonText) { %>\
        <button class="btn btn-primary"><%= primaryButtonText %></button>\
        <% } %>\
    </div>\
  </div>';

  Dialog.prototype.ok = function() {};

  Dialog.prototype.okWrap = function() {
    return this.ok(this.$el);
  };

  Dialog.prototype.title = "Title";

  Dialog.prototype.content = "Content";

  Dialog.prototype.closeButtonText = "Close";

  Dialog.prototype.primaryButtonText = void 0;

  Dialog.prototype.prefix = "";

  Dialog.prototype.initialize = function(options) {
    if (!options) {
      options = {};
    }
    if (options.ok) {
      this.ok = options.ok;
    }
    if (options.title) {
      this.title = options.title;
    }
    if (options.content) {
      this.content = options.content;
    }
    if (options.closeButtonText) {
      this.closeButtonText = options.closeButtonText;
    }
    if (options.primaryButtonText) {
      this.primaryButtonText = options.primaryButtonText;
    }
    if (options.prefix) {
      this.prefix = options.prefix;
    }
    this.setElement(_.template(this.elTemplate, {
      prefix: this.prefix,
      title: this.title,
      content: this.content,
      closeButtonText: this.closeButtonText,
      primaryButtonText: this.primaryButtonText
    }));
    this.$el.find(".btn-primary").click(this.okWrap);
    this.$el.on("hidden", this.remove);
    if (options.highlightPrimary | this.highlightPrimary) {
      return this.$el.on("shown", function() {
        return $($(".modal-footer .btn-primary").first()).focus();
      });
    } else {
      return this.$el.on("shown", function() {
        return $($(".modal-footer .btn-close").first()).focus();
      });
    }
  };

  Dialog.prototype.remove = function() {
    return this.$el.remove();
  };

  Dialog.prototype.render = function() {
    $("#content").append(this.el);
    return this.$el.modal('show');
  };

  return Dialog;

})(Backbone.View);

GeoLocation = (function() {
  var instance,
    _this = this;

  instance = null;

  function GeoLocation() {
    if (instance !== null) {
      throw new Error("Cannot instantiate more than one " + name + ", use " + name + ".getInstance()");
    }
    this.initialize();
  }

  GeoLocation.prototype.updatePosition = function(position) {
    return this.position = position;
  };

  GeoLocation.prototype.initialize = function() {
    var _this = this;
    if (navigator.geolocation) {
      return navigator.geolocation.getCurrentPosition(function(position) {
        return _this.position = position;
      });
    }
  };

  GeoLocation.getInstance = function() {
    if (instance === null) {
      instance = new GeoLocation();
    }
    return instance;
  };

  return GeoLocation;

}).call(this);

LoginDialog = (function(_super) {

  __extends(LoginDialog, _super);

  function LoginDialog() {
    this.ok = __bind(this.ok, this);
    return LoginDialog.__super__.constructor.apply(this, arguments);
  }

  LoginDialog.prototype.title = "Login Required";

  LoginDialog.prototype.content = "A valid login is required.";

  LoginDialog.prototype.primaryButtonText = "Login via Twitter";

  LoginDialog.prototype.ok = function() {
    return window.location.href = "/login/twitter/";
  };

  return LoginDialog;

})(Dialog);

Router = (function(_super) {

  __extends(Router, _super);

  function Router() {
    return Router.__super__.constructor.apply(this, arguments);
  }

  Router.prototype.routes = {
    "q/:question_id": "question",
    "t/:tag_name": "tag",
    "add": "add",
    ":page": "root",
    "": "root"
  };

  Router.prototype.root = function(page) {
    var questionCollection, questionList, questionPaginator;
    console.log("root");
    if (page && !parseInt(page)) {
      return;
    }
    if (!page) {
      page = 1;
    } else {
      page = parseInt(page);
    }
    questionCollection = new QuestionCollection();
    questionList = new QuestionList({
      collection: questionCollection
    });
    questionPaginator = new QuestionPaginator({
      collection: questionCollection
    });
    questionCollection.page = page;
    $("#content").html(questionList.el);
    $("#content").append(questionPaginator.el);
    if ($("#json_data").html()) {
      questionCollection.reset(questionCollection.parse($.parseJSON($("#json_data").html())));
      return $("#json_data").remove();
    } else {
      return questionCollection.fetch();
    }
  };

  Router.prototype.tag = function(tag_name) {
    var page, questionList, tagCollection;
    console.log("tag: " + tag_name);
    if (!page) {
      page = 1;
    } else {
      page = parseInt(page);
    }
    tagCollection = new QuestionCollection();
    tagCollection.url = "/v1/tag/" + tag_name;
    questionList = new QuestionList({
      collection: tagCollection
    });
    tagCollection.page = page;
    $("#content").html(questionList.el);
    if ($("#json_data").html()) {
      return tagCollection.reset(tagCollection.parse($.parseJSON($("#json_data").html())));
    } else {
      return tagCollection.fetch();
    }
  };

  Router.prototype.question = function(question_id) {
    var model, question,
      _this = this;
    console.log("question: " + question_id);
    model = new QuestionModel({
      id: question_id
    });
    question = new QuestionView({
      model: model,
      active: true
    });
    $("#content").append(question.el);
    setInterval((function() {
      return model.fetch();
    }), 10000);
    if ($("#json_data").html()) {
      model.set($.parseJSON($("#json_data").html()));
    } else {
      model.fetch();
    }
    return model.on('destroy', function() {
      return window.location = "/";
    });
  };

  Router.prototype.add = function() {
    var questionAdd;
    console.log("add");
    return questionAdd = new QuestionAdd();
  };

  return Router;

})(Backbone.Router);

Account = (function() {
  var instance,
    _this = this;

  instance = null;

  function Account() {
    if (instance !== null) {
      throw new Error("Cannot instantiate more than one " + name + ", use " + name + ".getInstance()");
    }
    this.initialize();
  }

  Account.prototype.initialize = function() {
    var data;
    data = $.parseJSON($("#account_id").html());
    if (data) {
      this.id = data.id;
      return this.admin = data.admin;
    }
  };

  Account.getInstance = function() {
    if (instance === null) {
      instance = new Account();
    }
    return instance;
  };

  return Account;

}).call(this);

QuestionModel = (function(_super) {

  __extends(QuestionModel, _super);

  function QuestionModel() {
    return QuestionModel.__super__.constructor.apply(this, arguments);
  }

  QuestionModel.prototype.url = function() {
    return "/v1/question/" + this.id;
  };

  QuestionModel.prototype.votes = function() {
    return _.reduce(this.get('answers'), function(t, a) {
      return t + (a.votes || 0);
    }, 0);
  };

  QuestionModel.prototype.followee_votes = function() {
    return _.reduce(this.get('answers'), function(t, a) {
      return t + (a.followee_votes || 0);
    }, 0) || 1;
  };

  return QuestionModel;

})(Backbone.Model);

QuestionCollection = (function(_super) {

  __extends(QuestionCollection, _super);

  function QuestionCollection() {
    this.update = __bind(this.update, this);

    this.updateOrAdd = __bind(this.updateOrAdd, this);

    this.parse = __bind(this.parse, this);

    this.info = __bind(this.info, this);

    this.url = __bind(this.url, this);
    return QuestionCollection.__super__.constructor.apply(this, arguments);
  }

  QuestionCollection.prototype.model = QuestionModel;

  QuestionCollection.prototype.type = 'GET';

  QuestionCollection.prototype.dataType = 'jsonp';

  QuestionCollection.prototype.url = function() {
    if (this.page) {
      return "v1/questions?page=" + this.page;
    } else {
      return "v1/questions";
    }
  };

  QuestionCollection.prototype.info = function() {
    return {
      'page': this.page,
      'perPage': this.length,
      'totalPages': this.totalPages,
      'firstPage': 1,
      'lastPage': this.totalPages
    };
  };

  QuestionCollection.prototype.parse = function(response) {
    this.totalPages = response.numPages;
    return response.questions;
  };

  QuestionCollection.prototype.updateOrAdd = function(collection, response) {
    return _.each(response, function(ele) {
      return collection.get(ele.id).set(ele);
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

QuestionView = (function(_super) {

  __extends(QuestionView, _super);

  QuestionView.prototype.questionTmpl = _.template($("#question-template").html());

  QuestionView.prototype.tagName = "div";

  QuestionView.prototype.events = {
    "click .rest>.answers>.answer": "vote",
    "click .footer .delete": "delete",
    "click .rest": "stopPropagation"
  };

  QuestionView.prototype.active = false;

  function QuestionView(config) {
    this.render = __bind(this.render, this);

    this.addTooltips = __bind(this.addTooltips, this);

    this.expand = __bind(this.expand, this);

    this.addMap = __bind(this.addMap, this);

    this.createMap = __bind(this.createMap, this);

    this.collapse = __bind(this.collapse, this);

    this.attributes = __bind(this.attributes, this);

    this.vote = __bind(this.vote, this);

    this.stopPropagation = __bind(this.stopPropagation, this);

    this["delete"] = __bind(this["delete"], this);
    if (config.active) {
      this.active = config.active;
    }
    QuestionView.__super__.constructor.call(this, config);
  }

  QuestionView.prototype.initialize = function(config) {
    var _this = this;
    this.model.on("change", this.render);
    if (config.tagName) {
      this.tagName = config.tagName;
    }
    return _.each(config.classes, function(c) {
      return _this.classes.push(c);
    });
  };

  QuestionView.prototype["delete"] = function(event) {
    var question,
      _this = this;
    console.log("delete");
    question = $(event.currentTarget).closest(".question");
    new Dialog({
      closeButtonText: "Cancel",
      primaryButtonText: "Delete",
      title: "Delete Question?",
      content: "<p>Are you sure you want to delete the question: <blockquote>" + (this.model.get("text")) + "</blockquote></p>",
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

  QuestionView.prototype.stopPropagation = function(event) {
    return event.stopImmediatePropagation();
  };

  QuestionView.prototype.vote = function(event) {
    var answer,
      _this = this;
    answer = event.currentTarget.id;
    this.model.save({
      vote: answer,
      position: window.geoLocation.position
    }, {
      wait: true,
      url: "/v1/question/vote",
      complete: function() {
        return $("#" + answer).removeClass("working");
      },
      error: function(model, response) {
        if (response.status === 401) {
          model.unset("vote");
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

  QuestionView.prototype.classes = ["question"];

  QuestionView.prototype.attributes = function() {
    var c, classes;
    classes = this.classes;
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

  QuestionView.prototype.collapse = function(callback) {
    var _this = this;
    this.$el.children(".question .rest").slideUp(function(event) {
      _this.active = false;
      _this.$el.removeClass("active");
      if (callback) {
        return callback(event);
      }
    });
    if (this.removeMap) {
      return this.removeMap();
    }
  };

  QuestionView.prototype.createMap = function() {
    var centered, click, g, g_dots, g_us, height, mapDiv, mapDivWidth, path, projection, r, radius, restDiv, strokewidth, svg, width,
      _this = this;
    restDiv = this.$el.children(".rest");
    mapDiv = restDiv.find(".map");
    if (restDiv.css('display') === 'none') {
      restDiv.css('visibility', 'hidden').show();
      mapDivWidth = mapDiv.innerWidth();
      restDiv.css('visibility', 'visible').hide();
    } else {
      mapDivWidth = mapDiv.innerWidth();
    }
    width = mapDivWidth * .8;
    height = width * 1 / 2;
    projection = d3.geo.albersUsa().scale(width).translate([0, 0]);
    path = d3.geo.path().projection(projection);
    svg = d3.select(mapDiv.get()[0]).append("svg").attr("width", width).attr("height", height);
    g = svg.append("g").attr("transform", "translate(" + (width / 2) + "," + (height / 2) + ")").append("g");
    g_us = g.append("g").attr("id", "states");
    g_dots = g.append("g").attr("id", "circles");
    radius = 4;
    strokewidth = 1.5;
    centered = null;
    r = radius;
    click = function(d) {
      var bounds, centroid, hh, k, spd, trans, ww, x, xk, y, yk;
      x = 0;
      y = 0;
      k = 1;
      spd = 1200;
      if (d && centered !== d.id) {
        centroid = path.centroid(d);
        x = -centroid[0];
        y = -centroid[1];
        bounds = path.bounds(d);
        ww = 2 * Math.max(centroid[0] - bounds[0][0], bounds[1][0] - centroid[0]);
        hh = 2 * Math.max(centroid[1] - bounds[0][1], bounds[1][1] - centroid[1]);
        xk = width / (ww * 1.2);
        yk = height / (hh * 1.1);
        k = Math.min(xk, yk);
        r = radius / k;
        spd = 600;
        centered = d.id;
      } else {
        r = radius;
        centered = null;
      }
      g_us.selectAll("path").classed("active", centered && function(d) {
        return d.id === centered;
      });
      trans = g.transition().duration(1000).attr("transform", "scale(" + k + ")translate(" + x + "," + y + ")").selectAll("path.state").style("stroke-width", "" + (strokewidth / k) + "px");
      return g_dots.selectAll("circle").transition().duration(spd).attr("r", r);
    };
    d3.json("/static/us.json", function(us) {
      return g_us.selectAll("path").data(topojson.object(us, us.objects.states).geometries).enter().append("path").style("stroke-width", "" + strokewidth + "px").classed("active", centered && function(d) {
        return d.id === centered;
      }).classed("state", true).attr("d", path).on("click", click);
    });
    this.updateMap = function() {
      return g_dots.selectAll("circle").data(function() {
        return _this.model.get("geo");
      }).attr("class", function(d) {
        return "dot color_" + d.id;
      }).attr("cx", function(d) {
        return path.centroid(d)[0];
      }).attr("cy", function(d) {
        return path.centroid(d)[1];
      }).attr("r", r).enter().append("circle").attr("class", function(d) {
        return "dot color_" + d.id;
      }).attr("cx", function(d) {
        return path.centroid(d)[0];
      }).attr("cy", function(d) {
        return path.centroid(d)[1];
      }).attr("r", r);
    };
    this.removeMap = function() {
      $(svg[0]).slideUp(function() {
        return $(this).remove();
      });
      _this.map = void 0;
      return _this.updateMap = void 0;
    };
    this.updateMap();
    return svg[0];
  };

  QuestionView.prototype.addMap = function() {
    var mapDiv, restDiv, svg;
    if (!this.model.get("vote") || !this.model.get("geo").length > 0) {
      return;
    }
    restDiv = this.$el.children(".rest");
    mapDiv = restDiv.find(".map");
    if (this.map) {
      mapDiv.html(this.map);
      this.updateMap();
      return mapDiv.prepend("<div class=\"header\"><h5>Map Data</h5></div>");
    } else {
      this.map = (svg = this.createMap());
      mapDiv.html(this.map);
      return mapDiv.prepend("<div class=\"header\"><h5>Map Data</h5></div>");
    }
  };

  QuestionView.prototype.expand = function(callback) {
    this.active = true;
    this.addMap();
    this.$el.addClass("active");
    return this.$el.children(".rest").slideDown(callback);
  };

  QuestionView.prototype.addTooltips = function() {
    this.$(".answer .fill .label").tooltip();
    return this.$(".followees .progress .bar").tooltip();
  };

  QuestionView.prototype.render = function() {
    this.$el.html(this.questionTmpl({
      account: window.account,
      question: this.model,
      active: this.active
    }));
    this.addTooltips();
    if (this.active) {
      this.addMap();
    }
    return this;
  };

  return QuestionView;

})(Backbone.View);

QuestionList = (function(_super) {

  __extends(QuestionList, _super);

  function QuestionList() {
    this.fetch = __bind(this.fetch, this);

    this.reset = __bind(this.reset, this);

    this.render = __bind(this.render, this);

    this.addAll = __bind(this.addAll, this);

    this.append = __bind(this.append, this);

    this.prepend = __bind(this.prepend, this);

    this.remove = __bind(this.remove, this);

    this.add = __bind(this.add, this);

    this.newQuestionView = __bind(this.newQuestionView, this);

    this.toggleView = __bind(this.toggleView, this);

    this.toggleQuestion = __bind(this.toggleQuestion, this);

    this.stopPropagation = __bind(this.stopPropagation, this);

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
    if (this.collection) {
      this.collection.on("add", this.add);
      this.collection.on("reset", this.addAll);
      this.collection.on("remove", this.remove);
    }
    this.selectedQuestion = void 0;
    return this.childViews = {};
  };

  QuestionList.prototype.stopPropagation = function(event) {
    return event.stopImmediatePropagation();
  };

  QuestionList.prototype.toggleQuestion = function(event) {
    return this.toggleView(event.currentTarget);
  };

  QuestionList.prototype.toggleView = function(target) {
    var targetId, view;
    targetId = target.id;
    if (this.selectedQuestion) {
      this.childViews[this.selectedQuestion].collapse();
    }
    if (targetId === this.selectedQuestion) {
      return this.selectedQuestion = void 0;
    } else {
      view = this.childViews[targetId];
      view.expand();
      return this.selectedQuestion = targetId;
    }
  };

  QuestionList.prototype.newQuestionView = function(model) {
    return new QuestionView({
      model: model,
      tagName: "li"
    });
  };

  QuestionList.prototype.add = function(model) {
    var ele, view, _i, _len, _ref;
    view = this.newQuestionView(model);
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
    if (this.selectedQuestion === model.id.toString()) {
      this.selectedQuestion = void 0;
    }
    view = this.childViews[model.id];
    view.$el.remove();
    return delete this.childViews[model.id];
  };

  QuestionList.prototype.prepend = function(model) {
    var view;
    view = this.newQuestionView(model);
    this.childViews[model.id] = view;
    return this.$el.prepend(view.render().el);
  };

  QuestionList.prototype.append = function(model) {
    var view;
    view = this.newQuestionView(model);
    this.childViews[model.id] = view;
    return this.$el.append(view.render().el);
  };

  QuestionList.prototype.addAll = function() {
    var targetEl, targetId;
    this.render;
    this.collection.each(this.append);
    if (location.hash) {
      targetId = location.hash.substring(3);
      if ((targetEl = $("#" + targetId)[0])) {
        return this.toggleView(targetEl);
      }
    }
  };

  QuestionList.prototype.render = function() {
    this.$el.empty();
    return this;
  };

  QuestionList.prototype.reset = function(data) {
    return this.collection.reset(data);
  };

  QuestionList.prototype.fetch = function() {
    return this.collection.fetch();
  };

  return QuestionList;

})(Backbone.View);

QuestionPaginator = (function(_super) {

  __extends(QuestionPaginator, _super);

  function QuestionPaginator() {
    this.render = __bind(this.render, this);

    this.initialize = __bind(this.initialize, this);

    this.prevPage = __bind(this.prevPage, this);

    this.nextPage = __bind(this.nextPage, this);
    return QuestionPaginator.__super__.constructor.apply(this, arguments);
  }

  QuestionPaginator.prototype.tagName = "div";

  QuestionPaginator.prototype.attributes = {
    id: "paginator",
    "class": "paginator"
  };

  QuestionPaginator.prototype.template = _.template($("#paginator-template").html());

  QuestionPaginator.prototype.events = {
    'click a#next': 'nextPage',
    'click a#prev': 'prevPage'
  };

  QuestionPaginator.prototype.nextPage = function(e) {
    e.preventDefault();
    return window.app.navigate("/" + (this.collection.page + 1), {
      trigger: true
    });
  };

  QuestionPaginator.prototype.prevPage = function(e) {
    e.preventDefault();
    return window.app.navigate("/" + (this.collection.page - 1), {
      trigger: true
    });
  };

  QuestionPaginator.prototype.initialize = function() {
    if (this.collection) {
      return this.collection.on("reset", this.render);
    }
  };

  QuestionPaginator.prototype.render = function() {
    this.$el.html(this.template(this.collection.info()));
    return this;
  };

  return QuestionPaginator;

})(Backbone.View);

$(window).ready(function() {
  console.log("main");
  window.setTimeout(function() {
    return $('.alert').slideUp('fast', function() {
      return $(this).remove();
    });
  }, 3000);
  window.geoLocation = GeoLocation.getInstance();
  window.account = Account.getInstance();
  window.app = new Router();
  return Backbone.history.start({
    pushState: true,
    hashChange: true
  });
});
