import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from tools import web_search, scrape_url

load_dotenv(override=True)
agent_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

writer_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2
)

critic_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)
def build_search_agent():
    return create_agent(
        model=agent_llm,
        tools=[web_search],
        system_prompt="""You are a research search agent.
Always call web_search with exactly one argument:
{"query": "your search query"}
Never use cursor, id, page, or offset."""
    )

def build_reader_agent():
    return create_agent(
        model=agent_llm,
        tools=[scrape_url],
        system_prompt="""You are a research reader agent.
Always call scrape_url with exactly one argument:
{"url": "https://example.com"}
The argument name MUST be "url"."""
    )

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write concise, balanced, factual reports with clear structure and no fluff."),
    ("human", """Write a short research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Requirements:
- Keep the total report under 700 words.
- Use only 4 sections in this exact order: Introduction, Key Findings, Conclusion, Sources.
- Include exactly 3 short key findings.
- Keep each section short and balanced.
- No long paragraphs, no repeated ideas, no filler.
- Use only URLs found in the research.
- Be factual, professional, and concise.
"""),
])

writer_chain = writer_prompt | writer_llm | StrOutputParser()

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
...
"""),
])

critic_chain = critic_prompt | critic_llm | StrOutputParser()