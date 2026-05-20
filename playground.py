# import asyncio
# from browser_use_sdk.v3 import AsyncBrowserUse

# async def main():
#     client = AsyncBrowserUse()
#     result = await client.run("List the top 10 posts on Hacker News today with their points",
#                               model="gemini-3-flash",
#                               use_own_key=True)
#     print(result.output)

# asyncio.run(main())

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
from enum import Enum
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver


class JobType(str, Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class Job(BaseModel):
    title: str
    company_description: str = None
    job_description: str = None
    qualifications: str
    compensation: str = None
    job_type: JobType




load_dotenv()

# model = ChatGoogleGenerativeAI(model="gemma-4-31b-it")


async def use_browser_mcp():
    # Connect to browser-use MCP server
    server_params = StdioServerParameters(
        command="uvx",
        args=["--from", "browser-use[cli]", "browser-use", "--mcp"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
           
            # Convert MCP tools -> LangChain tools
            tools = await load_mcp_tools(session)
            # tools = [t for t in tools if t.name in ]
            model = ChatGoogleGenerativeAI(model="gemma-4-31b-it")
            summodel = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt="You are a job search agent. Use your tools to search and return jobs. Search for all jobs on https://hiring.cafe/. the website does not have a search button, you will have to type in the search bar and click the drop down menu that appears to search. apply any filters that the user requests. Return one job posting",
                # system_prompt="You are a job applying agent. Use your tools to fill out job forms. the user will provide the job link and their profile. do not submit the application, only fill out the form. some forms may be multiple pages, make sure to fill out every page. some input fields may show a dropdown menu when typing, click the best option from the drop down menu. skip any input fields that are not provided by the user.",
                response_format=Job,
                checkpointer=InMemorySaver(),
                middleware=[
                    SummarizationMiddleware(
                        model=summodel,
                        trigger=("tokens", 100000),
                        keep=('messages', 2)
                    )
                ]
            )

            # # Navigate to a website
            # result = await session.call_tool(
            #     "browser_navigate",
            #     arguments={"url": "https://hiring.cafe/"}
            # )
            # print(result.content[0].text)

            # # Get page state
            # result = await session.call_tool(
            #     "browser_get_state",
            #     arguments={"include_screenshot": True}
            # )
            # print("Page state retrieved!")
            

            question = HumanMessage(content="search for ai engineer jobs that area remote only and max 2 years of experience")
#             question = HumanMessage(content="""apply to this job: https://careers.pdf.com/careers-home/jobs/1543?mode=apply&iis=LinkedIn with my information: "first_name": "IBRAHEEM",
#   "last_name": "ALORAN",
#   "phone_number": "+1(226)-260-8814",
#   "email": "ibraheemaloran@gmail.com",
#   "location": "Canada",
#   "current company": "Vosyn",
#   "Gender": "Male",
#   "linkedin": "linkedin.com/in/ibraheem-aloran/",
# #   "github": "github.com/IbraheemAloran""")

            response = await agent.ainvoke(
                {"messages": [question]},
                {"configurable": {"thread_id": "1"}}
            )

            print(response['messages'][-1].content)
            # model.invoke("show 5 jobs posting for pyhton developer on hiring cafe")
            

asyncio.run(use_browser_mcp())