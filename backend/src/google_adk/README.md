
# Python Data Analysis Agent

This project contains a Python-based data analysis agent that can write, execute, and debug Python code for data analysis and visualization.

## Project Structure

- `data_store/`
  - `code/`: Stores the Python scripts that are being executed.
  - `imgs/`: Stores the images that are being generated.
- `software_team/`
  - `agent.py`: Defines the data analysis agent.
  - `tools.py`: Contains the tools used by the agent.

## How it Works

The agent uses a series of tools to perform data analysis tasks:

1. **`write_file`**: Writes a Python script to a temporary file.
2. **`run_python_file`**: Executes the Python script.
3. **`delete_file`**: Deletes the temporary file after execution.
4. **`register_output_file`**: Registers the output file path.

The agent is designed to be used in a conversational AI setting, where a user can provide a dataset and ask the agent to perform analysis on it.

## How to Run

### To create a local FastAPI server in a single command

```bash
$ adk api_server
```
### To chat with the agent

```bash
$ adk run multi_tool_agent
```
### To launch the dev UI.

```bash
$ adk api_server
```