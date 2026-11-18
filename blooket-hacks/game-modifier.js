/*
 * Local visual and parameter helper.
 * This script only changes an in-memory configuration and CSS on the current
 * page. It is not a network or account modification tool.
 */
(function () {
  "use strict";

  var state = {
    scale: 1,
    contrast: false,
  };

  var STYLE_ID = "game-toolbox-local-modifier";
  var style = document.getElementById(STYLE_ID) || document.createElement("style");
  style.id = STYLE_ID;
  document.head.appendChild(style);

  function apply() {
    style.textContent =
      "body{transform:scale(" + state.scale + ");transform-origin:top left!important;" +
      (state.contrast ? "filter:contrast(1.35)!important;" : "") + "}";
  }

  window.GameModifier = {
    setScale: function (value) {
      var scale = Number(value);
      if (!Number.isFinite(scale) || scale < 0.5 || scale > 2) {
        throw new RangeError("Scale must be a number between 0.5 and 2.");
      }
      state.scale = scale;
      apply();
      return state;
    },
    setContrast: function (enabled) {
      state.contrast = Boolean(enabled);
      apply();
      return state;
    },
    reset: function () {
      state.scale = 1;
      state.contrast = false;
      apply();
      return state;
    },
    getState: function () {
      return Object.assign({}, state);
    },
  };

  apply();
})();
