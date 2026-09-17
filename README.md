*This project has been created as part of the 42 curriculum by, kmalfois*

-------------------------------------------------------------------------------
RAG Against The Machine Project
=============

-------------------------------------------------------------------------------
# DESCRIPTION

-------------------------------------------------------------------------------
# INSTRUCTIONS

## MAKEFILE
Makefile commands:
- **make install**: installs venv using uv (**don't forget to activate**)
- **make run**: Runs Fly-in script with default input files.
- **make sync**: Runs uv sync if needed.
- **make debug**: Runs Fly-in script with python's debug mode.
- **make clean**: Destroys pycache artifacts.
- **make fclean**: Executes clean command, destroys virtual environment and clears uv cache.
- **make lint**: Executes flake8 and mypy.
- **make f8**: Executes flake8 alone.
- **make lint**: Executes mypy alone.
- **make lint-strict**: Executes flake8 and mypy with the --strict flag.

-------------------------------------------------------------------------------
# RESOURCES

-------------------------------------------------------------------------------
# CONFIGURATION

-------------------------------------------------------------------------------
# HIGHSCORE

-------------------------------------------------------------------------------
# MAZE GENERATION

-------------------------------------------------------------------------------
# IMPLEMENTATION

-------------------------------------------------------------------------------
# GENERAL SOFTWARE ARCHITETURE

- **Makefile**: Command file.
- **README.md**: Program guide and information.
- **[assets]**: images used in README.md.
- **[maps]**: map files.
- **[output]**: Simulation's data as JSON file.
- **[src]**: Contains all program files.
 - **__init__.py**: Module init file.
 - **__main__.py**: Module main file.
 - **arbiter.py**: Decision maker.
 - **cogitator.py**: Drone trajectory calculation.
 - **connection.py**: Connection object class.
 - **data_exporter.py**: Data export module.
 - **data_lib.py**: Custom pydantic type library.
 - **drone.py**: Drone object class.
 - **error_handler.py**: Error handler.
 - **hub.py**: Hub object class.
 - **interface.py**: Program interface.
 - **navigator.py**: Map data parsing and extraction.
 - **operator.py**: Orchestrator and simulation runner.
- **[visualizer]**: Contains all visualization files.
  - **simulation_data**.json: JSON result of a simulation.
  - **visualizer.pck**: GoDot file.
  - **visualizer.sh**: GoDot file.
  - **visualizer.x86_64**: Visualizer executable file.
- **.flake8**: Flake8 ignore rules.
- **.gitignore**: Files ignored by git.
- **all_run.py**: Small script to test all available maps
- **.mypy**: mypy directives, excluded files from mypy check
- **pyproject.toml**: Package directives for uv
- **uv.lock**: uv.lock

-------------------------------------------------------------------------------
# PROJECT MANAGEMENT

-------------------------------------------------------------------------------
# PROGRAM

-------------------------------------------------------------------------------
# CODE ARCHITECTURE

-------------------------------------------------------------------------------
# ALGORITHM

-------------------------------------------------------------------------------
# INTERFACE GRAPHIC

-------------------------------------------------------------------------------
# CONCLUSION
LOL

