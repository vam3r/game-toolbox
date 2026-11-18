/*
 * Blooket toolbox: answer-highlighting helper
 *
 * Save this file as a bookmarklet or paste it into a browser console on a
 * game page you control. Correct answers are only highlighted when explicitly
 * supplied by the page or by window.__GAME_CORRECT_ANSWERS__.
 */
(function () {
  "use strict";

  var STYLE_ID = "game-toolbox-answer-highlight";
  var existing = document.getElementById(STYLE_ID);
  if (existing) existing.remove();

  var style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent =
    "[data-game-toolbox-correct='true']{outline:3px solid #22c55e!important;" +
    "box-shadow:0 0 12px rgba(34,197,94,.75)!important;" +
    "background:rgba(34,197,94,.16)!important}";
  document.head.appendChild(style);

  function isCorrectElement(element) {
    if (element.dataset.correct === "true" ||
        element.getAttribute("aria-correct") === "true" ||
        element.classList.contains("correct-answer")) {
      return true;
    }

    var configured = window.__GAME_CORRECT_ANSWERS__;
    if (!Array.isArray(configured) || !element.textContent) return false;
    var text = element.textContent.trim().toLowerCase();
    return configured.some(function (answer) {
      return typeof answer === "string" &&
        answer.trim().toLowerCase() === text;
    });
  }

  function scan() {
    var candidates = document.querySelectorAll(
      "[data-correct], [aria-correct], .answer, .answer-option, button"
    );
    candidates.forEach(function (element) {
      if (isCorrectElement(element)) {
        element.dataset.gameToolboxCorrect = "true";
      } else {
        delete element.dataset.gameToolboxCorrect;
      }
    });
  }

  if (window.__gameToolboxAnswerObserver__) {
    window.__gameToolboxAnswerObserver__.disconnect();
  }
  window.__gameToolboxAnswerObserver__ =
    new MutationObserver(function () { scan(); });
  window.__gameToolboxAnswerObserver__.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
  });
  scan();
})();
