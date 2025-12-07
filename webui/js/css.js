/**
 * @file This file provides utilities for dynamically manipulating CSS rules at runtime.
 * It creates a dedicated stylesheet for adding new rules and provides functions
 * to modify existing rules across all stylesheets on the page.
 */

// Create and keep a reference to a dynamic stylesheet for runtime CSS changes
let dynamicStyleSheet;
{
  const style = document.createElement("style");
  style.appendChild(document.createTextNode(""));
  document.head.appendChild(style);
  dynamicStyleSheet = style.sheet;
}

/**
 * Dynamically adds, updates, or removes a CSS property for a given selector.
 * It searches for the selector across all stylesheets. If found, it modifies the
 * existing rule. If not found, it creates a new rule in a dedicated dynamic
 * stylesheet.
 * @param {string} selector - The CSS selector to target (e.g., '.my-class', '#my-id').
 * @param {string} property - The CSS property to modify (e.g., 'color', 'font-size').
 * @param {string | undefined} value - The new value for the property. If undefined, the property is removed.
 */
export function toggleCssProperty(selector, property, value) {
  // Get the stylesheet that contains the class
  const styleSheets = document.styleSheets;

  // Iterate through all stylesheets to find the class
  for (let i = 0; i < styleSheets.length; i++) {
    const styleSheet = styleSheets[i];
    let rules;
    try {
      rules = styleSheet.cssRules || styleSheet.rules;
    } catch (e) {
      // Skip stylesheets we cannot access due to CORS/security restrictions
      continue;
    }
    if (!rules) continue;

    for (let j = 0; j < rules.length; j++) {
      const rule = rules[j];
      if (rule.selectorText == selector) {
        _applyCssToRule(rule, property, value);
        return;
      }
    }
  }
  // If not found, add it to the dynamic stylesheet
  const ruleIndex = dynamicStyleSheet.insertRule(
    `${selector} {}`,
    dynamicStyleSheet.cssRules.length
  );
  const rule = dynamicStyleSheet.cssRules[ruleIndex];
  _applyCssToRule(rule, property, value);
}

/**
 * A helper function to apply or remove a CSS property on a given CSS rule.
 * @param {CSSStyleRule} rule - The CSS rule object to modify.
 * @param {string} property - The CSS property to set or remove.
 * @param {string | undefined} value - The value to set for the property. If undefined, the property is removed.
 * @private
 */
function _applyCssToRule(rule, property, value) {
    if (value === undefined) {
      rule.style.removeProperty(property);
    } else {
      rule.style.setProperty(property, value);
    }
  }