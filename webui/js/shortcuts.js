import { store as chatsStore } from "/components/sidebar/chats/chats-store.js";
import { callJsonApi } from "/js/api.js";
import * as modals from "/js/modals.js";
import {
  NotificationType,
  NotificationPriority,
  store as notificationStore,
} from "/components/notifications/notification-store.js";

/**
 * @file This module provides a set of convenience functions and re-exports
 * commonly used utilities from other modules. It acts as a shortcut layer to
 * simplify access to APIs, notifications, chat context, and modals.
 */

// shortcuts utils for convenience

// api
export { callJsonApi };

// notifications
export { NotificationType, NotificationPriority };
/**
 * A shortcut to the `frontendNotification` method of the notification store.
 * @function
 * @param {object} notification - The notification object to display.
 */
export const frontendNotification =
  notificationStore.frontendNotification.bind(notificationStore);

// chat context
/**
 * Gets the ID of the currently selected chat context.
 * @returns {string | null} The ID of the current chat context.
 */
export function getCurrentContextId() {
  return chatsStore.getSelectedChatId();
}

/**
 * Gets the full object of the currently selected chat context.
 * @returns {object | null} The current chat context object.
 */
export function getCurrentContext(){
  return chatsStore.getSelectedContext();
}

// modals
/**
 * A shortcut to open a modal.
 * @param {string} modalPath - The path to the modal's HTML component.
 * @returns {Promise<void>} A promise that resolves when the modal is closed.
 */
export function openModal(modalPath) {
  return modals.openModal(modalPath);
}

/**
 * A shortcut to close a modal.
 * @param {string | null} [modalPath=null] - The path of the modal to close. If null, closes the topmost modal.
 */
export function closeModal(modalPath = null) {
  return modals.closeModal(modalPath);
}
