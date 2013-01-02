var Dialog, GeoLocation, LoginDialog, QuestionAdd, QuestionCollection, QuestionItem, QuestionList, QuestionModel, Router, User, geoLocation, instance,
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

  LoginDialog.prototype.primaryButtonText = "Login";

  LoginDialog.prototype.ok = function() {
    return window.location.href = "/login/";
  };

  return LoginDialog;

})(Dialog);

Router = (function(_super) {

  __extends(Router, _super);

  function Router() {
    return Router.__super__.constructor.apply(this, arguments);
  }

  Router.prototype.routes = {
    "question/add/": "add",
    ":question/": "root",
    ":hash": "root",
    "": "root"
  };

  Router.prototype.root = function(hash) {
    var questionList;
    if (hash && !this._alreadyTriggered) {
      Backbone.history.navigate("", false);
      location.hash = hash;
      this._alreadyTriggered = true;
      return;
    }
    console.log("root");
    questionList = new QuestionList();
    questionList.reset();
    return questionList.render();
  };

  Router.prototype.add = function() {
    var questionAdd;
    console.log("add");
    return questionAdd = new QuestionAdd();
  };

  return Router;

})(Backbone.Router);

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

User.getInstance();

QuestionModel = (function(_super) {

  __extends(QuestionModel, _super);

  function QuestionModel() {
    return QuestionModel.__super__.constructor.apply(this, arguments);
  }

  QuestionModel.prototype.idAttribute = "_id";

  QuestionModel.prototype.url = function() {
    return "/v1/question/" + this.id;
  };

  QuestionModel.prototype.votes = function() {
    return _.reduce(this.get('answers'), function(t, a) {
      return t + (a.votes | 0);
    }, 0);
  };

  QuestionModel.prototype.friend_votes = function() {
    return _.reduce(this.get('answers'), function(t, a) {
      return t + (a.friend_votes | 0);
    }, 0) | 1;
  };

  return QuestionModel;

})(Backbone.Model);

QuestionCollection = (function(_super) {

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

QuestionItem = (function(_super) {

  __extends(QuestionItem, _super);

  function QuestionItem() {
    this.render = __bind(this.render, this);

    this.expand = __bind(this.expand, this);

    this.updateMap = __bind(this.updateMap, this);

    this.createMap = __bind(this.createMap, this);

    this.collapse = __bind(this.collapse, this);

    this.vote = __bind(this.vote, this);

    this.nothing = __bind(this.nothing, this);

    this["delete"] = __bind(this["delete"], this);

    this.initialize = __bind(this.initialize, this);
    return QuestionItem.__super__.constructor.apply(this, arguments);
  }

  QuestionItem.prototype.questionTmpl = _.template($("#question-template").html());

  QuestionItem.prototype.tagName = "li";

  QuestionItem.prototype.events = {
    "click .rest>.answers>.answer": "vote",
    "click .answers .delete": "delete",
    "click .rest": "nothing"
  };

  QuestionItem.prototype.active = false;

  QuestionItem.prototype.initialize = function() {
    this.model.on("change", this.render);
    return this.answerScale = d3.scale.category10();
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

  QuestionItem.prototype.nothing = function() {
    return false;
  };

  QuestionItem.prototype.vote = function(event) {
    var answer,
      _this = this;
    answer = event.currentTarget.id;
    this.model.save({
      vote: answer,
      position: geoLocation.position
    }, {
      wait: true,
      url: "/v1/question/vote/",
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

  QuestionItem.prototype.collapse = function(callback) {
    this.active = false;
    this.$el.removeClass("active");
    this.$el.children(".question .rest").slideUp(callback);
    return this.removeMap();
  };

  QuestionItem.prototype.createMap = function(us) {
    var centered, click, g, height, mapDiv, path, projection, r, radius, strokewidth, svg, width,
      _this = this;
    console.log("createMap");
    mapDiv = this.$el.find(".map");
    mapDiv.empty();
    width = mapDiv.innerWidth() * .8;
    height = width * 1 / 2;
    projection = d3.geo.albersUsa().scale(width).translate([0, 0]);
    path = d3.geo.path().projection(projection);
    svg = d3.select(mapDiv.get()[0]).append("svg").attr("width", width).style("display", "none").attr("height", height);
    g = svg.append("g").attr("transform", "translate(" + (width / 2) + "," + (height / 2) + ")").append("g").attr("id", "states");
    radius = 3;
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
      g.selectAll("path").classed("active", centered && function(d) {
        return d.id === centered;
      });
      trans = g.transition().duration(1000).attr("transform", "scale(" + k + ")translate(" + x + "," + y + ")").selectAll("path.state").style("stroke-width", "" + (strokewidth / k) + "px");
      g.selectAll("circle.dot").transition().duration(spd).attr("r", r);
      return console.log(centered);
    };
    console.log(centered);
    g.selectAll("path").data(topojson.object(us, us.objects.states).geometries).enter().append("path").style("stroke-width", "" + strokewidth + "px").classed("active", centered && function(d) {
      return d.id === centered;
    }).classed("state", true).attr("d", path).on("click", click);
    this.updateMapData = function() {
      console.log("updateMapData");
      return g.selectAll("circle").data(function() {
        return _this.model.get("geo");
      }).style("fill", function(d) {
        return _this.answerScale(d.id);
      }).attr("cx", function(d) {
        return path.centroid(d)[0];
      }).attr("cy", function(d) {
        return path.centroid(d)[1];
      }).attr("r", r).enter().append("circle").attr("class", "dot").style("fill", function(d) {
        return _this.answerScale(d.id);
      }).attr("cx", function(d) {
        return path.centroid(d)[0];
      }).attr("cy", function(d) {
        return path.centroid(d)[1];
      }).attr("r", r);
    };
    this.removeMap = function() {
      console.log("removeMap");
      $(svg[0]).slideUp(function() {
        return $(this).remove();
      });
      _this.map = void 0;
      return _this.updateMapData = void 0;
    };
    this.updateMapData();
    return svg[0];
  };

  QuestionItem.prototype.updateMap = function() {
    var mapDiv, pDiv, restDiv,
      _this = this;
    console.log("updateMap");
    if (!this.model.get("vote") || !this.model.get("geo").length > 0) {
      return;
    }
    restDiv = this.$el.children(".rest");
    mapDiv = restDiv.children(".map");
    if (this.map) {
      mapDiv.html(this.map);
      this.updateMapData();
      return;
    }
    pDiv = mapDiv.children("p");
    pDiv.html('loading map data...');
    return d3.json("/static/us.json", function(us) {
      var svg;
      _this.map = (svg = _this.createMap(us));
      return $(svg).slideDown('slow');
    });
  };

  QuestionItem.prototype.expand = function(callback) {
    this.active = true;
    this.$el.addClass("active");
    this.$el.children(".rest").slideDown(callback);
    return this.updateMap();
  };

  QuestionItem.prototype.render = function() {
    this.$el.html(this.questionTmpl({
      user: User.id,
      question: this.model,
      answerScale: this.answerScale,
      active: this.active
    }));
    if (this.active) {
      this.updateMap();
    }
    return this;
  };

  return QuestionItem;

})(Backbone.View);

QuestionList = (function(_super) {

  __extends(QuestionList, _super);

  function QuestionList() {
    this.reset = __bind(this.reset, this);

    this.render = __bind(this.render, this);

    this.addAll = __bind(this.addAll, this);

    this.append = __bind(this.append, this);

    this.prepend = __bind(this.prepend, this);

    this.remove = __bind(this.remove, this);

    this.add = __bind(this.add, this);

    this.toggleView = __bind(this.toggleView, this);

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
    return this.toggleView(event.currentTarget.id);
  };

  QuestionList.prototype.toggleView = function(targetId) {
    var view;
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
    this.collection.each(this.append);
    if (location.hash) {
      return this.toggleView(location.hash.substring(1));
    }
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

geoLocation = void 0;

$(window).ready(function() {
  var app;
  console.log("main");
  window.setTimeout(function() {
    return $('.alert').fadeOut('fast', function() {
      return $(this).remove();
    });
  }, 3000);
  geoLocation = GeoLocation.getInstance();
  app = new Router();
  return Backbone.history.start({
    pushState: true,
    hashChange: true
  });
});