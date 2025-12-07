/**
 * @file This script serves as the main entry point for initializing the frontend framework.
 * It orchestrates the loading of essential modules, initializes the Alpine.js library,
 * and extends Alpine with custom directives for component lifecycle management.
 */
import * as initializer from "./initializer.js";
import * as _modals from "./modals.js";
import * as _components from "./components.js";

// initialize required elements
await initializer.initialize();

// import alpine library
await import("../vendor/alpine/alpine.min.js");

/**
 * Custom Alpine.js directive `x-destroy`.
 * Executes a JavaScript expression when the element is removed from the DOM.
 * This is useful for cleanup tasks, like removing event listeners or timers.
 */
Alpine.directive(
  "destroy",
  (el, { expression }, { evaluateLater, cleanup }) => {
    const onDestroy = evaluateLater(expression);
    cleanup(() => onDestroy());
  }
);

/**
 * Custom Alpine.js directive `x-create`.
 * Executes a JavaScript expression when the element is first initialized by Alpine.
 * This is useful for setup tasks that need to run once upon component creation.
 */
Alpine.directive("create", (_el, { expression }, { evaluateLater }) => {
  const onCreate = evaluateLater(expression);
  onCreate();
});
