from abc import abstractmethod
from typing import Any
from python.helpers import extract_tools, files 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Agent

class Extension:
    """An abstract base class for extensions."""

    def __init__(self, agent: "Agent|None", **kwargs):
        """Initializes an Extension.

        Args:
            agent: The agent that is using the extension.
            **kwargs: Additional keyword arguments.
        """
        self.agent: "Agent" = agent # type: ignore < here we ignore the type check as there are currently no extensions without an agent
        self.kwargs = kwargs

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the extension.

        This method must be implemented by subclasses.

        Args:
            **kwargs: The arguments for the extension.
        """
        pass


async def call_extensions(extension_point: str, agent: "Agent|None" = None, **kwargs) -> Any:
    """Calls all extensions for a given extension point.

    Args:
        extension_point: The name of the extension point.
        agent: The agent that is calling the extensions.
        **kwargs: The arguments to pass to the extensions.
    """

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


def _get_file_from_module(module_name: str) -> str:
    return module_name.split(".")[-1]

_cache: dict[str, list[type[Extension]]] = {}
async def _get_extensions(folder:str):
    global _cache
    folder = files.get_abs_path(folder)
    if folder in _cache:
        classes = _cache[folder]
    else:
        if not files.exists(folder):
            return []
        classes = extract_tools.load_classes_from_folder(
            folder, "*", Extension
        )
        _cache[folder] = classes

    return classes

