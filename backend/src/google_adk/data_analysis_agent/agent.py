# from google.adk.agents import Agent
from .tools import write_file, run_python_file, delete_file, register_output_file
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from pydantic import BaseModel, Field
from typing import Optional
gemini_model = "gemini-2.0-flash"

class ResponseContent(BaseModel):
    text: str = Field(
        description="The summarized answer about the user request"
    )
    img_path: Optional[str] = Field(
        description="The path to the plot created"
    )


agent = LlmAgent(
    model=gemini_model,
    name="python_data_analyst",
    description="An agent that writes, executes, and debugs python code for data analysis and visualization.",
    instruction="""
    You are a skilled Python data analyst. Your primary goal is to perform data analysis and visualization tasks on provided datasets. 
    
    You will be given the path to a dataset file.
    
    Follow these steps for any data-related request:
    1.  **Inspect the Data**: Read the data using pandas, list the columns of the dataset, and use the best one fits user's query.
    2.  **Plan the Analysis**:
        - If the data contains numeric columns, consider analyzing distributions (histogram, boxplot).
        - If the data includes categorical columns, visualize frequency counts.
        - If datetime columns exist, analyze time trends.
        - If there are missing values or outliers, suggest cleaning methods.
    3.  **Write the Code**: Generate a complete and efficient Python script, and use the `write_file` tool to write it and it will return the path of the file
    4.  **Execute and Validate**: Use the `run_python_file` tool to run the file you have write and use the path given from `write_file` tool, "When saving plots or reports, always store them in this "/mnt/d/python/mini-rag-app/frontend/imgs" path with descriptive file names.
    5.  **Retrive the Image name**: If you generate an image use `register_output_file` tool to return only the name of the image
    6.  **Cleaning**: After you excute the code delete the file you had run
    7.  **Summarize**: Write a natural language summary of the main insights that plot represents **don't add the steps of coding and creating files only give insights about the plot**.
    
    **IMPORTANT NOTE**: Don't add plt.show() when create plots only save it

    When creating visualizations, always label axes, provide a title, and include a legend if necessary. Save plots as `.png` files.
    """,
    tools=[write_file, run_python_file, delete_file, register_output_file],
    
)
formater_agent = LlmAgent(
    name="format_agent",
    model=gemini_model,
    description=(
        """
        This is an agent that formats the answers from the agent 'query_agent'.
        """
    ),
    instruction=(
        """
        You are an agent that formats the answers from the RAG system.
        """
    ),
    output_schema=ResponseContent,
    output_key="agent_response"
)

root_agent = SequentialAgent(
    name="root_agent",
    description=(
        """
        This is the root agent that coordinates the ingestion and querying process to the RAG system.
        """
    ),
    sub_agents=[agent, formater_agent],
    
)
