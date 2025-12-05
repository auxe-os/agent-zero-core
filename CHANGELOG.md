# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- CHANGELOG.md file - Added to track all changes following GEMINI.md requirements - 2025-12-04

### Fixed
- FAISS ARM patch for Python 3.12 - Conditional import fix for ARM compatibility - 2025-12-04
- DeferredTask background tasks - Replaced with simpler asyncio.create_task pattern for better resource management - 2025-12-04
- Vision bytes sent to utility LLM - Fixed to send image summaries instead of raw bytes - 2025-12-04
- Hardcoded observations/reflection strings - Replaced with prompt files for better customization - 2025-12-04
- concat_messages function parameters - Added message range, topic, and history parameters for better control - 2025-12-04

### Changed
- Settings.py background task implementation - Simplified from DeferredTask to asyncio.create_task - 2025-12-04
- MCP tool prompt generation - Moved hardcoded strings to configurable prompt files - 2025-12-04