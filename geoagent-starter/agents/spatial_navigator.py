import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage
from tools.gis_operations import get_layer_metadata, reproject, repair_and_join, repair
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langsmith import Client
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()



# 1. Initialize the LLM
# Model gpt-4o is excellent at following rigid spatial logic
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"))
#llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# 2. Define the Toolbelt
tools = [get_layer_metadata, reproject, repair_and_join, repair]

# 3. Create the Custom Spatial Architect Prompt
# This template is optimized for Pydantic V2/Python 3.14
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior Spatial Architect. 
    Your mission is to maintain 100% topological and coordinate integrity.
    
    STRICT PROTOCOL:
    - Never assume a CRS; always use 'get_layer_metadata' first.
    - If a mismatch is detected, use 'repair' first to fix CRS.
    - Be technically precise. If a task is impossible, explain why in GIS terms."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), 
])

#humanprompt = HumanMessage(content="Check the CRS of {input} and re-project to 4326 if needed.")

# messages = [prompt, humanprompt]

# client= Client()
# prompt = client.pull_prompt("hwchase17/openai-functions-agent")

# 4. Initialize the Modern Agent
# We use create_agent which runs on a LangGraph-powered runtime under the hood.
# This bypasses the legacy AgentExecutor import errors.
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a Senior Spatial Architect. 
    Your mission is to maintain 100% topological and coordinate integrity.
    
    STRICT PROTOCOL:
    - Never assume a CRS; always use 'get_layer_metadata' first.
    - If reprojection is needed, use 'reproject' first to fix the CRS immediately.
    - If and only if topology error is detected or asked by user, use 'repair_and_reproject'.
    - Be technically precise. If a task is impossible, explain why in GIS terms."""# We pass our custom architect persona here
)

# - If a mismatch is detected, use 'repair_and_join'.

# Export the executor for use in main.py
__all__ = ["agent_executor"]
