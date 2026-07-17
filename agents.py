from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent

from tools import web_search, scrape_url

load_dotenv()

# Model Setup
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

#1st agent 
def build_search_agent():
    return create_agent(
        model= llm,
        tools=[web_search] 
    )

#2nd agent 
def build_reader_agent():
    return create_agent(
        model= llm,
        tools=[scrape_url]
    )

#writer chain 
writer_prompt= ChatPromptTemplate.from_messages([
    ("system", "you are an expert research writer. write clear ,structured and insightful reports."),
    ("human", """write a detailed research report on the topic below.
    
     
     Topic: {topic}

     Research Gathered:
     {research}

     Structure the report as:
     - Introduction
     - Key Findings(minimun 3 well-explained points)
     - conclusion
     - Sources (list all URLs found in the research)

     Be detailed, factual and professional.
     """),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and execute it strictly.


Report:
     {report}

Respond in this exact format:
     
score: x/10
     
Strengths:                
- ...
- ... 
     
Areas to Improve:
- ...
- ...

one line verdict:
...  """),
])


critic_chain=critic_prompt | llm | StrOutputParser()

