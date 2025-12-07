

/**
 * @file This module handles the initial setup and configuration of the web UI
 * on page load.
 */
import * as device from "./device.js";

/**
 * The main initialization function for the application. This function is called
 * once to set up the necessary parts of the UI.
 */
export async function initialize(){
    // set device class to body tag
    setDeviceClass();
}

/**
 * Determines the user's input device type (touch or pointer) and applies a
 * corresponding CSS class ('device-touch' or 'device-pointer') to the `<body>` element.
 * This allows for device-specific styling.
 */
function setDeviceClass(){
    device.determineInputType().then((type) => {
        // Remove any class starting with 'device-' from <body>
        const body = document.body;
        body.classList.forEach(cls => {
            if (cls.startsWith('device-')) {
                body.classList.remove(cls);
            }
        });
        // Add the new device class
        body.classList.add(`device-${type}`);
    });
}
