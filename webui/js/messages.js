/**
 * @file This module is responsible for rendering and managing all types of messages
 * in the chat history. It handles creating new message elements, updating existing
 * ones, and formatting content like markdown, code, and special tags.
 */
// message actions and components
import { store as imageViewerStore } from "../components/modals/image-viewer/image-viewer-store.js";
import { marked } from "../vendor/marked/marked.esm.js";
import { store as _messageResizeStore } from "/components/messages/resize/message-resize-store.js"; // keep here, required in html
import { store as attachmentsStore } from "/components/chat/attachments/attachmentsStore.js";
import { addActionButtonsToElement } from "/components/messages/action-buttons/simple-action-buttons.js";

const chatHistory = document.getElementById("chat-history");

let messageGroup = null;

// Simplified implementation - no complex interactions needed

/**
 * Creates or updates a message in the chat history.
 * This is the main entry point for adding any type of message to the UI.
 * It determines if the message is new or an update and calls the appropriate
 * handler to render it. It also handles grouping messages visually.
 * @param {string} id - The unique ID for the message.
 * @param {string} type - The type of message (e.g., 'user', 'agent', 'error').
 * @param {string} heading - The heading or title for the message.
 * @param {string} content - The main content of the message.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object | null} [kvps=null] - Key-value pairs to display in the message.
 * @returns {HTMLElement} The message container element.
 */
export function setMessage(id, type, heading, content, temp, kvps = null) {
  // Search for the existing message container by id
  let messageContainer = document.getElementById(`message-${id}`);
  let isNewMessage = false;

  if (messageContainer) {
    // Don't clear innerHTML - we'll do incremental updates
    // messageContainer.innerHTML = "";
  } else {
    // Create a new container if not found
    isNewMessage = true;
    const sender = type === "user" ? "user" : "ai";
    messageContainer = document.createElement("div");
    messageContainer.id = `message-${id}`;
    messageContainer.classList.add("message-container", `${sender}-container`);
  }

  const handler = getHandler(type);
  handler(messageContainer, id, type, heading, content, temp, kvps);

  // If this is a new message, handle DOM insertion
  if (!document.getElementById(`message-${id}`)) {
    // message type visual grouping
    const groupTypeMap = {
      user: "right",
      info: "mid",
      warning: "mid",
      error: "mid",
      rate_limit: "mid",
      util: "mid",
      hint: "mid",
      // anything else is "left"
    };
    //force new group on these types
    const groupStart = {
      agent: true,
      // anything else is false
    };

    const groupType = groupTypeMap[type] || "left";

    // here check if messageGroup is still in DOM, if not, then set it to null (context switch)
    if (messageGroup && !document.getElementById(messageGroup.id))
      messageGroup = null;

    if (
      !messageGroup || // no group yet exists
      groupStart[type] || // message type forces new group
      groupType != messageGroup.getAttribute("data-group-type") // message type changes group
    ) {
      messageGroup = document.createElement("div");
      messageGroup.id = `message-group-${id}`;
      messageGroup.classList.add(`message-group`, `message-group-${groupType}`);
      messageGroup.setAttribute("data-group-type", groupType);
    }
    messageGroup.appendChild(messageContainer);
    chatHistory.appendChild(messageGroup);
  }

  // Simplified implementation - no setup needed

  return messageContainer;
}

// Legacy copy button functions removed - now using action buttons component

/**
 * Returns the appropriate drawing function for a given message type.
 * @param {string} type - The message type.
 * @returns {Function} The function used to draw the message.
 */
export function getHandler(type) {
  switch (type) {
    case "user":
      return drawMessageUser;
    case "agent":
      return drawMessageAgent;
    case "response":
      return drawMessageResponse;
    case "tool":
      return drawMessageTool;
    case "code_exe":
      return drawMessageCodeExe;
    case "browser":
      return drawMessageBrowser;
    case "warning":
      return drawMessageWarning;
    case "rate_limit":
      return drawMessageWarning;
    case "error":
      return drawMessageError;
    case "info":
      return drawMessageInfo;
    case "util":
      return drawMessageUtil;
    case "hint":
      return drawMessageInfo;
    default:
      return drawMessageDefault;
  }
}

/**
 * The core drawing function that handles the rendering of most message types.
 * It's a generic function that takes numerous parameters to customize the
 * appearance and content of a message.
 * @param {HTMLElement} messageContainer - The top-level container for the message.
 * @param {string} heading - The message heading.
 * @param {string} content - The main message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {boolean} followUp - Whether this message is a follow-up to the previous one.
 * @param {string} [mainClass=""] - The main CSS class for the message div.
 * @param {Object | null} [kvps=null] - Key-value pairs.
 * @param {string[]} [messageClasses=[]] - Additional classes for the message div.
 * @param {string[]} [contentClasses=[]] - Additional classes for the content div.
 * @param {boolean} [latex=false] - Whether to render LaTeX.
 * @param {boolean} [markdown=false] - Whether to render markdown.
 * @param {boolean} [resizeBtns=true] - Whether to show resize buttons.
 * @returns {HTMLElement} The main message div.
 * @private
 */
export function _drawMessage(
  messageContainer,
  heading,
  content,
  temp,
  followUp,
  mainClass = "",
  kvps = null,
  messageClasses = [],
  contentClasses = [],
  latex = false,
  markdown = false,
  resizeBtns = true
) {
  // Find existing message div or create new one
  let messageDiv = messageContainer.querySelector(".message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageContainer.appendChild(messageDiv);
  }

  // Update message classes
  messageDiv.className = `message ${mainClass} ${messageClasses.join(" ")}`;

  // Handle heading
  if (heading) {
    let headingElement = messageDiv.querySelector(".msg-heading");
    if (!headingElement) {
      headingElement = document.createElement("div");
      headingElement.classList.add("msg-heading");
      messageDiv.insertBefore(headingElement, messageDiv.firstChild);
    }

    let headingH4 = headingElement.querySelector("h4");
    if (!headingH4) {
      headingH4 = document.createElement("h4");
      headingElement.appendChild(headingH4);
    }
    headingH4.innerHTML = convertIcons(escapeHTML(heading));

    if (resizeBtns) {
      let minMaxBtn = headingElement.querySelector(".msg-min-max-btns");
      if (!minMaxBtn) {
        minMaxBtn = document.createElement("div");
        minMaxBtn.classList.add("msg-min-max-btns");
        minMaxBtn.innerHTML = `
          <a href="#" class="msg-min-max-btn" @click.prevent="$store.messageResize.minimizeMessageClass('${mainClass}', $event)"><span class="material-symbols-outlined" x-text="$store.messageResize.getSetting('${mainClass}').minimized ? 'expand_content' : 'minimize'"></span></a>
          <a href="#" class="msg-min-max-btn" x-show="!$store.messageResize.getSetting('${mainClass}').minimized" @click.prevent="$store.messageResize.maximizeMessageClass('${mainClass}', $event)"><span class="material-symbols-outlined" x-text="$store.messageResize.getSetting('${mainClass}').maximized ? 'expand' : 'expand_all'"></span></a>
        `;
        headingElement.appendChild(minMaxBtn);
      }
    }
  } else {
    // Remove heading if it exists but heading is null
    const existingHeading = messageDiv.querySelector(".msg-heading");
    if (existingHeading) {
      existingHeading.remove();
    }
  }

  // Find existing body div or create new one
  let bodyDiv = messageDiv.querySelector(".message-body");
  if (!bodyDiv) {
    bodyDiv = document.createElement("div");
    bodyDiv.classList.add("message-body");
    messageDiv.appendChild(bodyDiv);
  }

  // reapply scroll position or autoscroll
  const scroller = new Scroller(bodyDiv);

  // Handle KVPs incrementally
  drawKvpsIncremental(bodyDiv, kvps, false);

  // Handle content
  if (content && content.trim().length > 0) {
    if (markdown) {
      let contentDiv = bodyDiv.querySelector(".msg-content");
      if (!contentDiv) {
        contentDiv = document.createElement("div");
        bodyDiv.appendChild(contentDiv);
      }
      contentDiv.className = `msg-content ${contentClasses.join(" ")}`;

      let spanElement = contentDiv.querySelector("span");
      if (!spanElement) {
        spanElement = document.createElement("span");
        contentDiv.appendChild(spanElement);
      }

      let processedContent = content;
      processedContent = convertImageTags(processedContent);
      processedContent = convertImgFilePaths(processedContent);
      processedContent = marked.parse(processedContent, { breaks: true });
      processedContent = convertPathsToLinks(processedContent);
      processedContent = addBlankTargetsToLinks(processedContent);

      spanElement.innerHTML = processedContent;

      // KaTeX rendering for markdown
      if (latex) {
        spanElement.querySelectorAll("latex").forEach((element) => {
          katex.render(element.innerHTML, element, {
            throwOnError: false,
          });
        });
      }

      // Ensure action buttons exist
      addActionButtonsToElement(bodyDiv);
      adjustMarkdownRender(contentDiv);

    } else {
      let preElement = bodyDiv.querySelector(".msg-content");
      if (!preElement) {
        preElement = document.createElement("pre");
        preElement.classList.add("msg-content", ...contentClasses);
        preElement.style.whiteSpace = "pre-wrap";
        preElement.style.wordBreak = "break-word";
        bodyDiv.appendChild(preElement);
      } else {
        // Update classes
        preElement.className = `msg-content ${contentClasses.join(" ")}`;
      }

      let spanElement = preElement.querySelector("span");
      if (!spanElement) {
        spanElement = document.createElement("span");
        preElement.appendChild(spanElement);
      }

      spanElement.innerHTML = convertHTML(content);

      // Ensure action buttons exist
      addActionButtonsToElement(bodyDiv);

    }
  } else {
    // Remove content if it exists but content is empty
    const existingContent = bodyDiv.querySelector(".msg-content");
    if (existingContent) {
      existingContent.remove();
    }
  }

  // reapply scroll position or autoscroll
  scroller.reApplyScroll();

  if (followUp) {
    messageContainer.classList.add("message-followup");
  }

  return messageDiv;
}

/**
 * Adds `target="_blank"` and `rel="noopener noreferrer"` to all links in an HTML
 * string to ensure they open in a new tab securely.
 * @param {string} str - The HTML string to process.
 * @returns {string} The processed HTML string with updated links.
 */
export function addBlankTargetsToLinks(str) {
  const doc = new DOMParser().parseFromString(str, "text/html");

  doc.querySelectorAll("a").forEach((anchor) => {
    const href = anchor.getAttribute("href") || "";
    if (
      href.startsWith("#") ||
      href.trim().toLowerCase().startsWith("javascript")
    )
      return;
    if (
      !anchor.hasAttribute("target") ||
      anchor.getAttribute("target") === ""
    ) {
      anchor.setAttribute("target", "_blank");
    }

    const rel = (anchor.getAttribute("rel") || "").split(/\s+/).filter(Boolean);
    if (!rel.includes("noopener")) rel.push("noopener");
    if (!rel.includes("noreferrer")) rel.push("noreferrer");
    anchor.setAttribute("rel", rel.join(" "));
  });
  return doc.body.innerHTML;
}

/**
 * Renders a default message type.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageDefault(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-default",
    kvps,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

/**
 * Renders a message from the agent.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageAgent(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  let kvpsFlat = null;
  if (kvps) {
    kvpsFlat = { ...kvps, ...(kvps["tool_args"] || {}) };
    delete kvpsFlat["tool_args"];
  }

  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-agent",
    kvpsFlat,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

/**
 * Renders a final response message from the agent.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageResponse(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-agent-response",
    null,
    ["message-ai"],
    [],
    true,
    true
  );
}

/**
 * Renders a message indicating agent delegation.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageDelegation(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-agent-delegation",
    kvps,
    ["message-ai", "message-agent"],
    [],
    true,
    false
  );
}

/**
 * Renders a message from the user.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs, may include attachments.
 * @param {boolean} [latex=false] - Whether to render LaTeX.
 */
export function drawMessageUser(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null,
  latex = false
) {
  // Find existing message div or create new one
  let messageDiv = messageContainer.querySelector(".message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "message-user");
    messageContainer.appendChild(messageDiv);
  } else {
    // Ensure it has the correct classes if it already exists
    messageDiv.className = "message message-user";
  }

  // Handle heading
  let headingElement = messageDiv.querySelector(".msg-heading");
  if (!headingElement) {
    headingElement = document.createElement("h4");
    headingElement.classList.add("msg-heading");
    messageDiv.insertBefore(headingElement, messageDiv.firstChild);
  }
  headingElement.innerHTML = `${heading} <span class='icon material-symbols-outlined'>person</span>`;

  // Handle content
  let textDiv = messageDiv.querySelector(".message-text");
  if (content && content.trim().length > 0) {
    if (!textDiv) {
      textDiv = document.createElement("div");
      textDiv.classList.add("message-text");
      messageDiv.appendChild(textDiv);
    }
    let spanElement = textDiv.querySelector("pre");
    if (!spanElement) {
      spanElement = document.createElement("pre");
      textDiv.appendChild(spanElement);
    }
    spanElement.innerHTML = escapeHTML(content);
    addActionButtonsToElement(textDiv);
  } else {
    if (textDiv) textDiv.remove();
  }

  // Handle attachments
  let attachmentsContainer = messageDiv.querySelector(".attachments-container");
  if (kvps && kvps.attachments && kvps.attachments.length > 0) {
    if (!attachmentsContainer) {
      attachmentsContainer = document.createElement("div");
      attachmentsContainer.classList.add("attachments-container");
      messageDiv.appendChild(attachmentsContainer);
    }
    // Important: Clear existing attachments to re-render, preventing duplicates on update
    attachmentsContainer.innerHTML = ""; 

    kvps.attachments.forEach((attachment) => {
      const attachmentDiv = document.createElement("div");
      attachmentDiv.classList.add("attachment-item");

      const displayInfo = attachmentsStore.getAttachmentDisplayInfo(attachment);

      if (displayInfo.isImage) {
        attachmentDiv.classList.add("image-type");

        const img = document.createElement("img");
        img.src = displayInfo.previewUrl;
        img.alt = displayInfo.filename;
        img.classList.add("attachment-preview");
        img.style.cursor = "pointer";

        attachmentDiv.appendChild(img);
      } else {
        // Render as file tile with title and icon
        attachmentDiv.classList.add("file-type");

        // File icon
        if (
          displayInfo.previewUrl &&
          displayInfo.previewUrl !== displayInfo.filename
        ) {
          const iconImg = document.createElement("img");
          iconImg.src = displayInfo.previewUrl;
          iconImg.alt = `${displayInfo.extension} file`;
          iconImg.classList.add("file-icon");
          attachmentDiv.appendChild(iconImg);
        }

        // File title
        const fileTitle = document.createElement("div");
        fileTitle.classList.add("file-title");
        fileTitle.textContent = displayInfo.filename;

        attachmentDiv.appendChild(fileTitle);
      }

      attachmentDiv.addEventListener("click", displayInfo.clickHandler);

      attachmentsContainer.appendChild(attachmentDiv);
    });
  } else {
    if (attachmentsContainer) attachmentsContainer.remove();
  }
  // The messageDiv is already appended or updated, no need to append again
}

/**
 * Renders a message showing a tool call.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageTool(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-tool",
    kvps,
    ["message-ai"],
    ["msg-output"],
    false,
    false
  );
}

/**
 * Renders a message showing code execution.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageCodeExe(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-code-exe",
    null,
    ["message-ai"],
    [],
    false,
    false
  );
}

/**
 * Renders a message related to browser actions.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageBrowser(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-browser",
    kvps,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

/**
 * A helper for drawing simple, centered message types like info, warning, and error.
 * @param {string} mainClass - The main CSS class for the message.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 * @private
 */
export function drawMessageAgentPlain(
  mainClass,
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    mainClass,
    kvps,
    [],
    [],
    false,
    false
  );
  messageContainer.classList.add("center-container");
}

/**
 * Renders an informational message.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageInfo(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  return drawMessageAgentPlain(
    "message-info",
    messageContainer,
    id,
    type,
    heading,
    content,
    temp,
    kvps
  );
}

/**
 * Renders a utility message.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageUtil(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-util",
    kvps,
    [],
    ["msg-json"],
    false,
    false
  );
  messageContainer.classList.add("center-container");
}

/**
 * Renders a warning message.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageWarning(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  return drawMessageAgentPlain(
    "message-warning",
    messageContainer,
    id,
    type,
    heading,
    content,
    temp,
    kvps
  );
}

/**
 * Renders an error message.
 * @param {HTMLElement} messageContainer - The message's container element.
 * @param {string} id - The message ID.
 * @param {string} type - The message type.
 * @param {string} heading - The message heading.
 * @param {string} content - The message content.
 * @param {boolean} temp - Whether the message is temporary.
 * @param {Object|null} [kvps=null] - Key-value pairs.
 */
export function drawMessageError(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  return drawMessageAgentPlain(
    "message-error",
    messageContainer,
    id,
    type,
    heading,
    content,
    temp,
    kvps
  );
}

/**
 * Renders a table of key-value pairs.
 * @param {HTMLElement} container - The element to append the table to.
 * @param {Object} kvps - The key-value data.
 * @param {boolean} latex - Whether to render LaTeX in values.
 * @private
 */
function drawKvps(container, kvps, latex) {
  if (kvps) {
    const table = document.createElement("table");
    table.classList.add("msg-kvps");
    for (let [key, value] of Object.entries(kvps)) {
      const row = table.insertRow();
      row.classList.add("kvps-row");
      if (key === "thoughts" || key === "reasoning")
        // TODO: find a better way to determine special class assignment
        row.classList.add("msg-thoughts");

      const th = row.insertCell();
      th.textContent = convertToTitleCase(key);
      th.classList.add("kvps-key");

      const td = row.insertCell();
      const tdiv = document.createElement("div");
      tdiv.classList.add("kvps-val");
      td.appendChild(tdiv);

      if (Array.isArray(value)) {
        for (const item of value) {
          addValue(item);
        }
      } else {
        addValue(value);
      }

      addActionButtonsToElement(tdiv);

      // autoscroll the KVP value if needed
      // if (getAutoScroll()) #TODO needs a better redraw system
      setTimeout(() => {
        tdiv.scrollTop = tdiv.scrollHeight;
      }, 0);

      function addValue(value) {
        if (typeof value === "object") value = JSON.stringify(value, null, 2);

        if (typeof value === "string" && value.startsWith("img://")) {
          const imgElement = document.createElement("img");
          imgElement.classList.add("kvps-img");
          imgElement.src = value.replace("img://", "/image_get?path=");
          imgElement.alt = "Image Attachment";
          tdiv.appendChild(imgElement);

          // Add click handler and cursor change
          imgElement.style.cursor = "pointer";
          imgElement.addEventListener("click", () => {
            openImageModal(imgElement.src, 1000);
          });
        } else {
          const pre = document.createElement("pre");
          const span = document.createElement("span");
          span.innerHTML = convertHTML(value);
          pre.appendChild(span);
          tdiv.appendChild(pre);

          // KaTeX rendering for markdown
          if (latex) {
            span.querySelectorAll("latex").forEach((element) => {
              katex.render(element.innerHTML, element, {
                throwOnError: false,
              });
            });
          }
        }
      }
    }
    container.appendChild(table);
  }
}

/**
 * Incrementally renders or updates a table of key-value pairs. This is more
 * efficient than `drawKvps` for streaming updates.
 * @param {HTMLElement} container - The element containing the table.
 * @param {Object} kvps - The key-value data.
 * @param {boolean} latex - Whether to render LaTeX in values.
 * @private
 */
function drawKvpsIncremental(container, kvps, latex) {
  if (kvps) {
    // Find existing table or create new one
    let table = container.querySelector(".msg-kvps");
    if (!table) {
      table = document.createElement("table");
      table.classList.add("msg-kvps");
      container.appendChild(table);
    }

    // Get all current rows for comparison
    let existingRows = table.querySelectorAll(".kvps-row");
    const kvpEntries = Object.entries(kvps);

    // Update or create rows as needed
    kvpEntries.forEach(([key, value], index) => {
      let row = existingRows[index];

      if (!row) {
        // Create new row if it doesn't exist
        row = table.insertRow();
        row.classList.add("kvps-row");
      }

      // Update row classes
      row.className = "kvps-row";
      if (key === "thoughts" || key === "reasoning") {
        row.classList.add("msg-thoughts");
      }

      // Handle key cell
      let th = row.querySelector(".kvps-key");
      if (!th) {
        th = row.insertCell(0);
        th.classList.add("kvps-key");
      }
      th.textContent = convertToTitleCase(key);

      // Handle value cell
      let td = row.cells[1];
      if (!td) {
        td = row.insertCell(1);
      }

      let tdiv = td.querySelector(".kvps-val");
      if (!tdiv) {
        tdiv = document.createElement("div");
        tdiv.classList.add("kvps-val");
        td.appendChild(tdiv);
      }

      // reapply scroll position or autoscroll
      const scroller = new Scroller(tdiv);

      // Clear and rebuild content (for now - could be optimized further)
      tdiv.innerHTML = "";

      addActionButtonsToElement(tdiv);

      if (Array.isArray(value)) {
        for (const item of value) {
          addValue(item, tdiv);
        }
      } else {
        addValue(value, tdiv);
      }

      // reapply scroll position or autoscroll
      scroller.reApplyScroll();
    });

    // Remove extra rows if we have fewer kvps now
    while (existingRows.length > kvpEntries.length) {
      const lastRow = existingRows[existingRows.length - 1];
      lastRow.remove();
      existingRows = table.querySelectorAll(".kvps-row");
    }

    function addValue(value, tdiv) {
      if (typeof value === "object") value = JSON.stringify(value, null, 2);

      if (typeof value === "string" && value.startsWith("img://")) {
        const imgElement = document.createElement("img");
        imgElement.classList.add("kvps-img");
        imgElement.src = value.replace("img://", "/image_get?path=");
        imgElement.alt = "Image Attachment";
        tdiv.appendChild(imgElement);

        // Add click handler and cursor change
        imgElement.style.cursor = "pointer";
        imgElement.addEventListener("click", () => {
          imageViewerStore.open(imgElement.src, { refreshInterval: 1000 });
        });
      } else {
        const pre = document.createElement("pre");
        const span = document.createElement("span");
        span.innerHTML = convertHTML(value);
        pre.appendChild(span);
        tdiv.appendChild(pre);

        // Add action buttons to the row
        // const row = tdiv.closest(".kvps-row");
        // if (row) {
          // addActionButtonsToElement(pre);
        // }

        // KaTeX rendering for markdown
        if (latex) {
          span.querySelectorAll("latex").forEach((element) => {
            katex.render(element.innerHTML, element, {
              throwOnError: false,
            });
          });
        }
      }
    }
  } else {
    // Remove table if kvps is null/empty
    const existingTable = container.querySelector(".msg-kvps");
    if (existingTable) {
      existingTable.remove();
    }
  }
}

/**
 * Converts a string from snake_case or kebab-case to Title Case.
 * @param {string} str - The input string.
 * @returns {string} The converted string.
 * @private
 */
function convertToTitleCase(str) {
  return str
    .replace(/_/g, " ") // Replace underscores with spaces
    .toLowerCase() // Convert the entire string to lowercase
    .replace(/\b\w/g, function (match) {
      return match.toUpperCase(); // Capitalize the first letter of each word
    });
}

/**
 * Converts custom `<image>` tags containing base64 data to standard `<img>` tags.
 * @param {string} content - The string content to process.
 * @returns {string} The processed string.
 * @private
 */
function convertImageTags(content) {
  // Regular expression to match <image> tags and extract base64 content
  const imageTagRegex = /<image>(.*?)<\/image>/g;

  // Replace <image> tags with <img> tags with base64 source
  const updatedContent = content.replace(
    imageTagRegex,
    (match, base64Content) => {
      return `<img src="data:image/jpeg;base64,${base64Content}" alt="Image Attachment" style="max-width: 250px !important;"/>`;
    }
  );

  return updatedContent;
}

/**
 * A comprehensive content conversion function that escapes HTML, converts image tags,
 * and turns file paths into links.
 * @param {*} str - The input, which will be stringified if not already a string.
 * @returns {string} The fully processed HTML string.
 * @private
 */
function convertHTML(str) {
  if (typeof str !== "string") str = JSON.stringify(str, null, 2);

  let result = escapeHTML(str);
  result = convertImageTags(result);
  result = convertPathsToLinks(result);
  return result;
}

/**
 * Converts `img://` pseudo-protocols to actual image URLs.
 * @param {string} str - The input string.
 * @returns {string} The processed string.
 * @private
 */
function convertImgFilePaths(str) {
  return str.replace(/img:\/\//g, "/image_get?path=");
}

/**
 * Converts `icon://` pseudo-protocols to Material Symbols span tags.
 * @param {string} str - The input string.
 * @returns {string} The processed string with icon tags.
 */
export function convertIcons(str) {
  return str.replace(
    /icon:\/\/([a-zA-Z0-9_]+)/g,
    '<span class="icon material-symbols-outlined">$1</span>'
  );
}

/**
 * Escapes special HTML characters in a string.
 * @param {string} str - The input string.
 * @returns {string} The escaped string.
 * @private
 */
function escapeHTML(str) {
  const escapeChars = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  };
  return str.replace(/[&<>'"]/g, (char) => escapeChars[char]);
}

/**
 * Converts absolute file paths in a string into clickable links.
 * It intelligently avoids converting paths inside HTML tags.
 * @param {string} str - The input string.
 * @returns {string} The processed string with linked paths.
 * @private
 */
function convertPathsToLinks(str) {
  function generateLinks(match) {
    const parts = match.split("/");
    if (!parts[0]) parts.shift(); // drop empty element left of first "
    let conc = "";
    let html = "";
    for (const part of parts) {
      conc += "/" + part;
      html += `/<a href="#" class="path-link" onclick="openFileLink('${conc}');">${part}</a>`;
    }
    return html;
  }

  const prefix = `(?:^|[> \`'"\\n]|&#39;|&quot;)`;
  const folder = `[a-zA-Z0-9_\\/.\\-]`;
  const file = `[a-zA-Z0-9_\\-\\/]`;
  const suffix = `(?<!\\.)`;
  const pathRegex = new RegExp(
    `(?<=${prefix})\\/${folder}*${file}${suffix}`,
    "g"
  );

  // skip paths inside html tags, like <img src="/path/to/image">
  const tagRegex = /(<(?:[^<>"']+|"[^"]*"|'[^']*')*>)/g;

  return str
    .split(tagRegex) // keep tags & text separate
    .map((chunk) => {
      // if it *starts* with '<', it's a tag -> leave untouched
      if (chunk.startsWith("<")) return chunk;
      // otherwise run your link-generation
      return chunk.replace(pathRegex, generateLinks);
    })
    .join("");
}

/**
 * Wraps tables rendered from markdown in a div for better styling and overflow handling.
 * @param {HTMLElement} element - The parent element containing the markdown-rendered content.
 * @private
 */
function adjustMarkdownRender(element) {
  // find all tables in the element
  const elements = element.querySelectorAll("table");

  // wrap each with a div with class message-markdown-table-wrap
  elements.forEach((el) => {
    const wrapper = document.createElement("div");
    wrapper.className = "message-markdown-table-wrap";
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);
  });
}

/**
 * A helper class to manage the scroll position of an element, allowing for
 * auto-scrolling if the element was already scrolled to the bottom.
 * @private
 */
class Scroller {
  constructor(element) {
    this.element = element;
    this.wasAtBottom = this.isAtBottom();
  }

  isAtBottom(tolerance = 10) {
    const scrollHeight = this.element.scrollHeight;
    const clientHeight = this.element.clientHeight;
    const distanceFromBottom =
      scrollHeight - this.element.scrollTop - clientHeight;
    return distanceFromBottom <= tolerance;
  }

  reApplyScroll() {
    if (this.wasAtBottom) this.element.scrollTop = this.element.scrollHeight;
  }
}