from agents import build_reader_agent , build_search_agent, writer_chain , critic_chain


def run_research_pipeline(topic : str) -> dict:

    state= {}

    # search agent working 
    print("\n" + "=" * 50)
    print("setp 1 - search agent is working... ")
    print("="*50)

    search_agent=build_search_agent()
    search_results=search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about :{topic}")]
    })
    state["search_results"] = search_results["messages"][-1].content

    print("\n  search result " , state['search_results'])


    #step 2 - reader agent 
    print("\n" + "=" * 50)
    print("setp 2 - Reader agent is scraping top resources ... ")
    print("="*50)

    reader_agent=build_reader_agent()
    reader_result=reader_agent.invoke({
        "messages": [("user",
            f"Based on the  following search results about '{topic}' , "
            f"pick the most relevant URL and scrape it for deeper content. \n\n"
            f"Search Results: \n {state['search_results'][:800]}"
          )]
    })
    state['scraped_content'] = reader_result['messages'][-1].content
    
    print("\n scraped content \n", state['scraped_content'])


    #step 3 - writer chain 
    print("\n" + "=" * 50)
    print("setp 3 - Writer is drafting the report ... ")
    print("="*50)

    research_combined=(
        f"SEARCH RESULTS : \n {state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"

    )

    state["report"]= writer_chain.invoke({
        "topic": topic , 
        "research" : research_combined
    })

    if len(state["report"]) > 1800:
        state["report"] = state["report"][:1800].rsplit("\n\n", 1)[0] + "\n\n..."

    print("\n Final Report \n", state['report'])


    #critic report 
    print("\n" + "=" * 50)
    print("setp 4 - Critic is reviewing the report  ... ")
    print("="*50)
    
    try:
        state["feedback"]= critic_chain.invoke({
            "report" : state.get('report', 'No report generated')
        })
    except Exception:
        state["feedback"] = "Critic feedback is unavailable right now."

    print("\n Critic Report \n", state['feedback'])


    return state 

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)