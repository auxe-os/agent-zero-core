# ⁠ gemini.md ⁠ - AI Development Assistant Guide for Agent Zero

## 🎯 Mission & Core Principles

You are an AI assistant helping to develop and extend the *Agent Zero* framework. Your primary goal is to add new features through *Extensions* and *Instruments* while maintaining the framework's modular architecture.

### Golden Rules:
1.⁠ ⁠*ALWAYS read ⁠ /docs ⁠ documentation BEFORE making any changes*
2.⁠ ⁠*PREFER Extensions and Instruments* over modifying core code
3.⁠ ⁠*DO NOT modify core files* unless explicitly instructed
4.⁠ ⁠*MAINTAIN a CHANGELOG.md* for all changes
5.⁠ ⁠*Follow existing patterns* and conventions

---

## 📚 Step 1: MANDATORY Documentation Review

Before writing ANY code, you MUST review these documentation files in order:

### Required Reading (in this order):
1.⁠ ⁠⁠ /docs/architecture.md ⁠ - Understand the system architecture
2.⁠ ⁠⁠ /docs/extensibility.md ⁠ - Learn the extensibility framework
3.⁠ ⁠⁠ /docs/development.md ⁠ - Development environment setup
4.⁠ ⁠Relevant tool/extension examples in the codebase

*YOU MUST CITE* which documentation you've reviewed before proposing changes. [1](#0-0) [2](#0-1) [3](#0-2) 

---

## 🔧 Step 2: Understanding the Architecture

### Directory Structure You Need to Know: [4](#0-3) 

### Key Components:
•⁠  ⁠*Extensions* (⁠ /python/extensions/ ⁠) - Hook into agent lifecycle
•⁠  ⁠*Tools* (⁠ /python/tools/ ⁠) - Provide functionality to agents
•⁠  ⁠*Instruments* (⁠ /instruments/ ⁠) - Custom scripts stored in memory (NOT in system prompt)
•⁠  ⁠*Prompts* (⁠ /prompts/ ⁠) - Control agent behavior
•⁠  ⁠*Agent Profiles* (⁠ /agents/ ⁠) - Custom agent configurations

---

## 🎨 Step 3: How to Add New Features

### Option A: Use Extensions (PREFERRED for behavior modifications)

*When to use:* Modifying agent behavior, adding hooks to lifecycle events

*Extension Points Available:* [5](#0-4) 

*How to create an extension:*

1.⁠ ⁠*Choose the right extension point* from the list above
2.⁠ ⁠*Create a Python file* in ⁠ /python/extensions/{extension_point}/ ⁠
3.⁠ ⁠*Name it with a number prefix* (e.g., ⁠ _10_my_extension.py ⁠) to control execution order
4.⁠ ⁠*Inherit from Extension base class*

*Example structure:* [6](#0-5) 

*Base Extension class:* [7](#0-6) 

### Option B: Use Instruments (PREFERRED for new tools/scripts)

*When to use:* Adding new capabilities without increasing token count in system prompt [8](#0-7) 

*How to create an instrument:*

1.⁠ ⁠Create folder in ⁠ /instruments/custom/{instrument_name} ⁠ (no spaces)
2.⁠ ⁠Add ⁠ {instrument_name}.md ⁠ file with description/interface
3.⁠ ⁠Add ⁠ {instrument_name}.sh ⁠ (or other executable) for implementation
4.⁠ ⁠The agent will automatically detect and use it from memory

*Instruments are loaded into memory:* [9](#0-8) 

### Option C: Create Custom Tools (ONLY if Extensions/Instruments won't work)

*When to use:* When you need a new tool that requires direct agent integration

*Steps:*
1.⁠ ⁠Create tool class in ⁠ /python/tools/{tool_name}.py ⁠
2.⁠ ⁠Create prompt file in ⁠ /prompts/agent.system.tool.{tool_name}.md ⁠
3.⁠ ⁠Inherit from Tool base class

*Tool base class structure:* [10](#0-9) 

*Example tool:* [11](#0-10) 

*Example tool prompt:* [12](#0-11) 

---

## 🚫 What NOT to Modify

### Core Files - DO NOT TOUCH unless explicitly instructed:
•⁠  ⁠⁠ /agent.py ⁠ - Core agent implementation
•⁠  ⁠⁠ /initialize.py ⁠ - Framework initialization
•⁠  ⁠⁠ /models.py ⁠ - Model providers
•⁠  ⁠⁠ /python/api/* ⁠ - API endpoints (unless adding new endpoint)
•⁠  ⁠⁠ /python/helpers/* ⁠ - Helper utilities (unless fixing bugs)

### When Core Changes Are Needed:
1.⁠ ⁠Ask the user for explicit permission
2.⁠ ⁠Explain why Extensions/Instruments won't work
3.⁠ ⁠Document the change thoroughly in CHANGELOG.md

---

## 📝 Step 4: CHANGELOG.md Requirements

You MUST maintain a ⁠ CHANGELOG.md ⁠ file in the root directory following this format:

⁠ markdown
# Changelog

All notable changes to this project extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- New extension: {name} - {description} - {date}
- New instrument: {name} - {description} - {date}

### Changed
- Modified: {what} - {why} - {date}

### Fixed
- Bug fix: {what} - {description} - {date}

## [Version] - YYYY-MM-DD

### Added
...
 ⁠

*Update CHANGELOG.md:*
•⁠  ⁠BEFORE making any changes (add to [Unreleased])
•⁠  ⁠AFTER completing changes (move to versioned section)
•⁠  ⁠Include rationale for each change

---

## ✅ Development Workflow

### For EVERY feature request, follow these steps:

1.⁠ ⁠*📖 Read Documentation*
   - Review relevant files in ⁠ /docs/ ⁠
   - Cite which docs you reviewed
   - Understand the architecture

2.⁠ ⁠*🎯 Choose Implementation Method*
   - First try: Can this be an *Instrument*?
   - Second try: Can this be an *Extension*?
   - Last resort: Does this need a new *Tool*?
   - Explain your choice

3.⁠ ⁠*📝 Update CHANGELOG.md*
   - Add entry to [Unreleased] section
   - Describe what you're adding and why

4.⁠ ⁠*💻 Write Code*
   - Follow existing patterns
   - Use appropriate base classes
   - Add clear comments
   - Follow naming conventions

5.⁠ ⁠*📋 Document*
   - Create/update relevant ⁠ .md ⁠ files
   - Add usage examples
   - Update CHANGELOG.md with completion notes

6.⁠ ⁠*🧪 Explain Testing*
   - Describe how to test the new feature
   - Provide example usage
   - Note any dependencies

---

## 🎓 Override Patterns

Agent Zero uses an override system for customization: [13](#0-12) 

*Agent-specific overrides:*
•⁠  ⁠⁠ /agents/{profile}/extensions/ ⁠ - Override default extensions
•⁠  ⁠⁠ /agents/{profile}/tools/ ⁠ - Override default tools
•⁠  ⁠⁠ /agents/{profile}/prompts/ ⁠ - Override default prompts

---

## 📌 Quick Reference

### Extension Points:
•⁠  ⁠⁠ agent_init ⁠ - Agent initialization
•⁠  ⁠⁠ message_loop_start ⁠ - Start of message processing
•⁠  ⁠⁠ message_loop_end ⁠ - End of message processing
•⁠  ⁠⁠ before_main_llm_call ⁠ - Before LLM call
•⁠  ⁠Many others (see extensibility.md)

### Tool Response Format: [14](#0-13) 

### Extension Execution: [15](#0-14) 

---

## 🚨 Final Checklist Before Submitting Code

•⁠  ⁠[ ] Read and cited relevant ⁠ /docs ⁠ documentation
•⁠  ⁠[ ] Chosen appropriate implementation (Instrument > Extension > Tool)
•⁠  ⁠[ ] Updated CHANGELOG.md with changes
•⁠  ⁠[ ] Followed existing code patterns
•⁠  ⁠[ ] Did NOT modify core files (unless explicitly approved)
•⁠  ⁠[ ] Created necessary ⁠ .md ⁠ documentation files
•⁠  ⁠[ ] Added clear comments and docstrings
•⁠  ⁠[ ] Explained testing approach
•⁠  ⁠[ ] Considered agent-specific overrides if needed

---

## 💬 Communication Template

When proposing changes, use this format:


## Feature: [Feature Name]

### Documentation Reviewed:
- [x] /docs/architecture.md
- [x] /docs/extensibility.md
- [ ] Other: ___

### Implementation Choice:
- [ ] Instrument (preferred)
- [ ] Extension
- [ ] Tool
- [ ] Core modification (requires approval)

**Rationale:** [Why this approach?]

### CHANGELOG Entry:

[Your changelog entry here]


### Files to Create/Modify:
1. [filepath] - [purpose]
2. [filepath] - [purpose]

### Code:
[Your code here]

### Testing:
[How to test this feature]


---

## 🎯 Remember

*Your job is to EXTEND, not REWRITE.* Agent Zero is designed for extensibility. Use Extensions and Instruments to add features while keeping the core framework clean and maintainable.

*When in doubt:*
1.⁠ ⁠Re-read the documentation
2.⁠ ⁠Look for existing examples
3.⁠ ⁠Ask for clarification
4.⁠ ⁠Choose the least invasive approach

---

*Good luck! Keep Agent Zero modular, maintainable, and magnificent! 🚀*

---

## Notes

This ⁠ gemini.md ⁠ file is based on the actual Agent Zero architecture and extensibility framework. The key principles are:

1.⁠ ⁠*Extensions* are for hooking into the agent lifecycle at specific points [16](#0-15) 

2.⁠ ⁠*Instruments* are stored in memory and don't consume system prompt tokens, making them ideal for adding new capabilities [8](#0-7) 

3.⁠ ⁠*Tools* should only be created when necessary, as they're always present in the system prompt [17](#0-16) 

4.⁠ ⁠The framework uses an override pattern where agent-specific implementations take precedence over defaults [13](#0-12) 

5.⁠ ⁠The development setup allows for local debugging with Docker for code execution [18](#0-17) 

Save this as ⁠ gemini.md ⁠ in your project root, and your AI assistant will have clear, comprehensive instructions for extending Agent Zero properly!

### Citations

*File:* docs/architecture.md (L1-80)
⁠ markdown
# Architecture Overview
Agent Zero is built on a flexible and modular architecture designed for extensibility and customization. This section outlines the key components and the interactions between them.

## System Architecture
This simplified diagram illustrates the hierarchical relationship between agents and their interaction with tools, extensions, instruments, prompts, memory and knowledge base.

![Agent Zero Architecture](res/arch-01.svg)

The user or Agent 0 is at the top of the hierarchy, delegating tasks to subordinate agents, which can further delegate to other agents. Each agent can utilize tools and access the shared assets (prompts, memory, knowledge, extensions and instruments) to perform its tasks.

## Runtime Architecture
Agent Zero's runtime architecture is built around Docker containers:

1. **Host System (your machine)**:
   - Requires only Docker and a web browser
   - Runs Docker Desktop or Docker Engine
   - Handles container orchestration

2. **Runtime Container**:
   - Houses the complete Agent Zero framework
   - Manages the Web UI and API endpoints
   - Handles all core functionalities including code execution
   - Provides a standardized environment across all platforms

This architecture ensures:
- Consistent environment across platforms
- Simplified deployment and updates
- Enhanced security through containerization
- Reduced dependency requirements on host systems
- Flexible deployment options for advanced users

> [!NOTE]
> The legacy approach of running Agent Zero directly on the host system (using Python, Conda, etc.) 
> is still possible but requires Remote Function Calling (RFC) configuration through the Settings 
> page. See [Full Binaries Installation](installation.md#in-depth-guide-for-full-binaries-installation) 
> for detailed instructions.

## Implementation Details

### Directory Structure
| Directory | Description |
| --- | --- |
| `/docker` | Docker-related files for runtime container |
| `/docs` | Documentation files and guides |
| `/instruments` | Custom scripts and tools for runtime environment |
| `/knowledge` | Knowledge base storage |
| `/logs` | HTML CLI-style chat logs |
| `/memory` | Persistent agent memory storage |
| `/prompts` | System and tool prompts |
| `/python` | Core Python codebase: |
| `/api` | API endpoints and interfaces |
| `/extensions` | Modular extensions |
| `/helpers` | Utility functions |
| `/tools` | Tool implementations |
| `/tmp` | Temporary runtime data |
| `/webui` | Web interface components: |
| `/css` | Stylesheets |
| `/js` | JavaScript modules |
| `/public` | Static assets |
| `/work_dir` | Working directory |

### Key Files
| File | Description |
| --- | --- |
| `.env` | Environment configuration |
| `agent.py` | Core agent implementation |
| `example.env` | Configuration template |
| `initialize.py` | Framework initialization |
| `models.py` | Model providers and configs |
| `preload.py` | Pre-initialization routines |
| `prepare.py` | Environment preparation |
| `requirements.txt` | Python dependencies |
| `run_cli.py` | CLI launcher |
| `run_ui.py` | Web UI launcher |

> [!NOTE]
> When using the Docker runtime container, these directories are mounted 
> within the `/a0` volume for data persistence until the container is restarted or deleted.

## Core Components
 ⁠

*File:* docs/architecture.md (L110-154)
⁠ markdown
### 2. Tools
Tools are functionalities that agents can leverage. These can include anything from web search and code execution to interacting with APIs or controlling external software. Agent Zero provides a mechanism for defining and integrating both built-in and custom tools.

#### Built-in Tools
Agent Zero comes with a set of built-in tools designed to help agents perform tasks efficiently:

| Tool | Function |
| --- | --- |
| behavior_adjustment | Agent Zero use this tool to change its behavior according to a prior request from the user.
| call_subordinate | Allows agents to delegate tasks to subordinate agents |
| code_execution_tool | Allows agents to execute Python, Node.js, and Shell code in the terminal |
| input | Allows agents to use the keyboard to interact with an active shell |
| response_tool | Allows agents to output a response |
| memory_tool | Enables agents to save, load, delete and forget information from memory |

#### SearXNG Integration
Agent Zero has integrated SearXNG as its primary search tool, replacing the previous knowledge tools (Perplexity and DuckDuckGo). This integration enhances the agent's ability to retrieve information while ensuring user privacy and customization.

- Privacy-Focused Search
SearXNG is an open-source metasearch engine that allows users to search multiple sources without tracking their queries. This integration ensures that user data remains private and secure while accessing a wide range of information.

- Enhanced Search Capabilities
The integration provides access to various types of content, including images, videos, and news articles, allowing users to gather comprehensive information on any topic.

- Fallback Mechanism
In cases where SearXNG might not return satisfactory results, Agent Zero can be configured to fall back on other sources or methods, ensuring that users always have access to information.

> [!NOTE]
> The Knowledge Tool is designed to work seamlessly with both online searches through 
> SearXNG and local knowledge base queries, providing a comprehensive information 
> retrieval system.

#### Custom Tools
Users can create custom tools to extend Agent Zero's capabilities. Custom tools can be integrated into the framework by defining a tool specification, which includes the tool's prompt to be placed in `/prompts/$FOLDERNAME/agent.system.tool.$TOOLNAME.md`, as detailed below.

1. Create `agent.system.tool.$TOOL_NAME.md` in `prompts/$SUBDIR`
2. Add reference in `agent.system.tools.md`
3. If needed, implement tool class in `python/tools` using `Tool` base class
4. Follow existing patterns for consistency

> [!NOTE]
> Tools are always present in system prompt, so you should keep them to minimum. 
> To save yourself some tokens, use the [Instruments module](#adding-instruments) 
> to call custom scripts or functions.

 ⁠

*File:* docs/architecture.md (L269-283)
⁠ markdown
### 6. Instruments
Instruments provide a way to add custom functionalities to Agent Zero without adding to the token count of the system prompt:
- Stored in long-term memory of Agent Zero
- Unlimited number of instruments available
- Recalled when needed by the agent
- Can modify agent behavior by introducing new procedures
- Function calls or scripts to integrate with other systems
- Scripts are run inside the Docker Container

#### Adding Instruments
1. Create folder in `instruments/custom` (no spaces in name)
2. Add `.md` description file for the interface
3. Add `.sh` script (or other executable) for implementation
4. The agent will automatically detect and use the instrument

 ⁠

*File:* docs/extensibility.md (L1-67)
⁠ markdown
# Extensibility framework in Agent Zero

> [!NOTE]
> Agent Zero is built with extensibility in mind. It provides a framework for creating custom extensions, agents, instruments, and tools that can be used to enhance the functionality of the framework.

## Extensible components
- The Python framework controlling Agent Zero is built as simple as possible, relying on independent smaller and modular scripts for individual tools, API endpoints, system extensions and helper scripts.
- This way individual components can be easily replaced, upgraded or extended.

Here's a summary of the extensible components:

### Extensions
Extensions are components that hook into specific points in the agent's lifecycle. They allow you to modify or enhance the behavior of Agent Zero at predefined extension points. The framework uses a plugin-like architecture where extensions are automatically discovered and loaded.

#### Extension Points
Agent Zero provides several extension points where custom code can be injected:

- **agent_init**: Executed when an agent is initialized
- **before_main_llm_call**: Executed before the main LLM call is made
- **message_loop_start**: Executed at the start of the message processing loop
- **message_loop_prompts_before**: Executed before prompts are processed in the message loop
- **message_loop_prompts_after**: Executed after prompts are processed in the message loop
- **message_loop_end**: Executed at the end of the message processing loop
- **monologue_start**: Executed at the start of agent monologue
- **monologue_end**: Executed at the end of agent monologue
- **reasoning_stream**: Executed when reasoning stream data is received
- **response_stream**: Executed when response stream data is received
- **system_prompt**: Executed when system prompts are processed

#### Extension Mechanism
The extension mechanism in Agent Zero works through the `call_extensions` function in `agent.py`, which:

1. Loads default extensions from `/python/extensions/{extension_point}/`
2. Loads agent-specific extensions from `/agents/{agent_profile}/extensions/{extension_point}/`
3. Merges them, with agent-specific extensions overriding default ones based on filename
4. Executes each extension in order

#### Creating Extensions
To create a custom extension:

1. Create a Python class that inherits from the `Extension` base class
2. Implement the `execute` method
3. Place the file in the appropriate extension point directory:
   - Default extensions: `/python/extensions/{extension_point}/`
   - Agent-specific extensions: `/agents/{agent_profile}/extensions/{extension_point}/`

**Example extension:**

 ⁠python
# File: /agents/_example/extensions/agent_init/_10_example_extension.py
from python.helpers.extension import Extension

class ExampleExtension(Extension):
    async def execute(self, **kwargs):
        # rename the agent to SuperAgent0
        self.agent.agent_name = "SuperAgent" + str(self.agent.number)


#### Extension Override Logic
When an extension with the same filename exists in both the default location and an agent-specific location, the agent-specific version takes precedence. This allows for selective overriding of extensions while inheriting the rest of the default behavior.

For example, if both these files exist:
- `/python/extensions/agent_init/example.py`
- `/agents/my_agent/extensions/agent_init/example.py`

The version in `/agents/my_agent/extensions/agent_init/example.py` will be used, completely replacing the default version.



*File:* docs/development.md (L1-20)
⁠ markdown
# Development manual for Agent Zero
This guide will show you how to setup a local development environment for Agent Zero in a VS Code compatible IDE, including proper debugger.


[![Tutorial video](./res/devguide_vid.png)](https://www.youtube.com/watch?v=KE39P4qBjDk)



> [!WARNING]
> This guide is for developers and contributors. It assumes you have a basic understanding of how to use Git/GitHub, Docker, IDEs and Python.

> [!NOTE]
> - Agent Zero runs in a Docker container, this simplifies installation and ensures unified environment and behavior across systems.
> - Developing and debugging in a container would be complicated though, therefore we use a hybrid approach where the python framework runs on your machine (in VS Code for example) and only connects to a Dockerized instance when it needs to execute code or use other pre-installed functionality like the built-in search engine.


## To follow this guide you will need:
1. VS Code compatible IDE (VS Code, Cursor, Windsurf...)
2. Python environment (Conda, venv, uv...)
3. Docker (Docker Desktop, docker-ce...)
 ⁠

*File:* docs/development.md (L105-145)
⁠ markdown


## Step 5: Run another instance of Agent Zero in Docker
- Some parts of A0 require standardized linux environment, additional web services and preinstalled binaries that would be unneccessarily complex to set up in a local environment.
- To make development easier, we can use existing A0 instance in docker and forward some requests to be executed there using SSH and RFC (Remote Function Call).

1. Pull the docker image `agent0ai/agent-zero` from Docker Hub and run it with a web port (`80`) mapped and SSH port (`22`) mapped.
If you want, you can also map the `/a0` folder to our local project folder as well, this way we can update our local instance and the docker instance at the same time.
This is how it looks in my example: port `80` is mapped to `8880` on the host and `22` to `8822`, `/a0` folder mapped to `/Users/frdel/Desktop/agent-zero`:

![docker run](res/dev/devinst-11.png)
![docker run](res/dev/devinst-12.png)


## Step 6: Configure SSH and RFC connection
- The last step is to configure the local development (VS Code) instance and the dockerized instance to communicate with each other. This is very simple and can be done in the settings in the Web UI of both instances.
- In my example the dark themed instance is the VS Code one, the light themed one is the dockerized instance.

1. Open the "Settings" page in the Web UI of your dockerized instance and go in the "Development" section.
2. Set the `RFC Password` field to a new password and save.
3. Open the "Settings" page in the Web UI of your local instance and go in the "Development" section.
4. Here set the `RFC Password` field to the same password you used in the dockerized instance. Also set the SSH port and HTTP port the same numbers you used when creating the container - in my case `8822` for SSH and `8880` for HTTP. The `RFC Destination URL` will most probably stay `localhost` as both instances are running on the host machine.
5. Click save and test by asking your agent to do something in the terminal, like "Get current OS version". It should be able to communicate with the dockerized instance via RFC and SSH and execute the command there, responding with something like "Kali GNU/Linux Rolling".

My Dockerized instance:
![Dockerized instance](res/dev/devinst-14.png)

My VS Code instance:
![VS Code instance](res/dev/devinst-13.png)


# 🎉 Congratulations! 🚀

You have successfully set up a complete Agent Zero development environment! You now have:

- ✅ A local development instance running in your IDE with full debugging capabilities
- ✅ A dockerized instance for code execution and system operations
- ✅ RFC and SSH communication between both instances
- ✅ The ability to develop, debug, and test Agent Zero features seamlessly

You're now ready to contribute to Agent Zero, create custom extensions, or modify the framework to suit your needs. Happy coding! 💻✨
 ⁠

*File:* python/extensions/agent_init/_10_initial_message.py (L1-42)
⁠ python
import json
from agent import LoopData
from python.helpers.extension import Extension


class InitialMessage(Extension):

    async def execute(self, **kwargs):
        """
        Add an initial greeting message when first user message is processed.
        Called only once per session via _process_chain method.
        """

        # Only add initial message for main agent (A0), not subordinate agents
        if self.agent.number != 0:
            return

        # If the context already contains log messages, do not add another initial message
        if self.agent.context.log.logs:
            return

        # Construct the initial message from prompt template
        initial_message = self.agent.read_prompt("fw.initial_message.md")

        # add initial loop data to agent (for hist_add_ai_response)
        self.agent.loop_data = LoopData(user_message=None)

        # Add the message to history as an AI response
        self.agent.hist_add_ai_response(initial_message)

        # json parse the message, get the tool_args text
        initial_message_json = json.loads(initial_message)
        initial_message_text = initial_message_json.get("tool_args", {}).get("text", "Hello! How can I help you?")

        # Add to log (green bubble) for immediate UI display
        self.agent.context.log.log(
            type="response",
            heading=f"{self.agent.agent_name}: Welcome",
            content=initial_message_text,
            finished=True,
            update_progress="none",
        )
 ⁠

*File:* python/helpers/extension.py (L8-16)
⁠ python
class Extension:

    def __init__(self, agent: "Agent|None", **kwargs):
        self.agent: "Agent" = agent # type: ignore < here we ignore the type check as there are currently no extensions without an agent
        self.kwargs = kwargs

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
 ⁠

*File:* python/helpers/extension.py (L19-40)
⁠ python
async def call_extensions(extension_point: str, agent: "Agent|None" = None, **kwargs) -> Any:

    # get default extensions
    defaults = await _get_extensions("python/extensions/" + extension_point)
    classes = defaults

    # get agent extensions
    if agent and agent.config.profile:
        agentics = await _get_extensions("agents/" + agent.config.profile + "/extensions/" + extension_point)
        if agentics:
            # merge them, agentics overwrite defaults
            unique = {}
            for cls in defaults + agentics:
                unique[_get_file_from_module(cls.__module__)] = cls

            # sort by name
            classes = sorted(unique.values(), key=lambda cls: _get_file_from_module(cls.__module__))

    # call extensions
    for cls in classes:
        await cls(agent=agent).execute(**kwargs)

 ⁠

*File:* python/helpers/memory.py (L326-334)
⁠ python
        # load instruments descriptions
        index = knowledge_import.load_knowledge(
            log_item,
            files.get_abs_path("instruments"),
            index,
            {"area": Memory.Area.INSTRUMENTS.value},
            filename_pattern="**/*.md",
            recursive=True,
        )
 ⁠

*File:* python/helpers/tool.py (L10-14)
⁠ python
@dataclass
class Response:
    message:str
    break_loop: bool
    additional: dict[str, Any] | None = None
 ⁠

*File:* python/helpers/tool.py (L16-50)
⁠ python
class Tool:

    def __init__(self, agent: Agent, name: str, method: str | None, args: dict[str,str], message: str, loop_data: LoopData | None, **kwargs) -> None:
        self.agent = agent
        self.name = name
        self.method = method
        self.args = args
        self.loop_data = loop_data
        self.message = message
        self.progress: str = ""

    @abstractmethod
    async def execute(self,**kwargs) -> Response:
        pass

    def set_progress(self, content: str | None):
        self.progress = content or ""

    def add_progress(self, content: str | None):
        if not content:
            return
        self.progress += content

    async def before_execution(self, **kwargs):
        PrintStyle(font_color="#1B4F72", padding=True, background_color="white", bold=True).print(f"{self.agent.agent_name}: Using tool '{self.name}'")
        self.log = self.get_log_object()
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(self.nice_key(key)+": ")
                PrintStyle(font_color="#85C1E9", padding=isinstance(value,str) and "\n" in value).stream(value)
                PrintStyle().print()

    async def after_execution(self, response: Response, **kwargs):
        text = sanitize_string(response.message.strip())
        self.agent.hist_add_tool_result(self.name, text, **(response.additional or {}))
 ⁠

*File:* agents/_example/tools/example_tool.py (L1-21)
⁠ python
from python.helpers.tool import Tool, Response

# this is an example tool class
# don't forget to include instructions in the system prompt by creating 
#   agent.system.tool.example_tool.md file in prompts directory of your agent
# see /python/tools folder for all default tools

class ExampleTool(Tool):
    async def execute(self, **kwargs):

        # parameters
        test_input = kwargs.get("test_input", "")

        # do something
        print("Example tool executed with test_input: " + test_input)

        # return response
        return Response(
            message="This is an example tool response, test_input: " + test_input, # response for the agent
            break_loop=False, # stop the message chain if true
        )
 ⁠

*File:* agents/_example/prompts/agent.system.tool.example_tool.md (L1-16)
⁠ markdown
### example_tool:
example tool to test functionality
this tool is automatically included to system prompt because the file name is "agent.system.tool.*.md"
usage:
~~~json
{
    "thoughts": [
        "Let's test the example tool...",
    ],
    "headline": "Testing example tool",
    "tool_name": "example_tool",
    "tool_args": {
        "test_input": "XYZ",
    }
}
~~~
 ⁠