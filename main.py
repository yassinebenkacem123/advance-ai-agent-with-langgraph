from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Annotated, Sequence
from langgraph.graph.message import BaseMessage, add_messages
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from webscrapping import serp_search, reddit_search_api,reddit_post_retrieval
from langchain_ollama import ChatOllama
from prompt import (
    get_google_analysis_messages, 
    get_bing_analysis_messages, 
    get_reddit_analysis_messages, 
    get_synthesis_messages,
    get_reddit_url_analysis_messages,
)

load_dotenv()

# calling the llm :
llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0.5,
)

# Reducer function to handle multiple updates - just returns the latest value
def last_value(left, right):
    return right if right is not None else left

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Search results — written by 3 parallel branches, so all need a reducer
    google_results:  Annotated[dict | None, last_value]
    bing_results:    Annotated[dict | None, last_value]
    reddit_results:  Annotated[dict | None, last_value]

    # All fields below are also written while parallel branches are still active
    # (each branch returns the FULL state), so they need reducers too.
    selected_reddit_urls: Annotated[List[str], last_value]
    reddit_post_data:     Annotated[dict | None, last_value]
    google_analysis:      Annotated[str | None, last_value]
    reddit_analysis:      Annotated[str | None, last_value]
    bing_analysis:        Annotated[str | None, last_value]
    final_result:         Annotated[str | None, last_value]



class RedditUrlAnanlysis(BaseModel):
    selected_reddit_urls: List[str] = Field(
        description="List of selected Reddit post URLs for analysis."
    )


# =============== > defining our nodes that we will need < ===================

# => get user question function
def get_user_question(state: AgentState) -> str:
    return state["messages"][-1].content


# => Node 1 : google search 
def google_search(state:AgentState) -> AgentState:
    """ This node is for getting informations from google. """

    print("Start Searching From Google")
    user_question = get_user_question(state)

    google_results  = serp_search(user_question, engine="google")
    state['google_results'] = google_results


    return state


# => Node 2 : reddit search : 
def reddit_search(state:AgentState) -> AgentState:
    """ This node is for reddit search."""

    user_question = get_user_question(state)

    print("Start Searching From Reddit...")

    reddit_results = reddit_search_api(user_question)
    state['reddit_results'] = reddit_results

    return state


# => Node 3 : Bing Search :
def bing_search(state:AgentState) -> AgentState:
    """
        this node is for bing search.
    """
    user_question = get_user_question(state)    
    print("Start Searching From Bing ...")

    bing_results = serp_search(user_question, engine="bing")


    state['bing_results'] = bing_results
    return state

# => Node 4 : analyze reddit post
def analyze_reddit_post(state:AgentState) -> AgentState:
    """this node is for analyzing reddit post and selecting the most relevant urls for the user question."""

    user_question = get_user_question(state)

    reddit_results = state.get('reddit_results')


    if not reddit_results:
        return state
    
    structured_llm = llm.with_structured_output(RedditUrlAnanlysis)

    # reddit_results is a dict: {"parsed_data": [...], "total_found": N}
    # Extract the list so the prompt receives a clean list of {title, url} dicts
    reddit_posts_list = reddit_results.get("parsed_data", []) if isinstance(reddit_results, dict) else reddit_results

    messages = get_reddit_url_analysis_messages(user_question, reddit_posts_list)


    try:
        analysis_result = structured_llm.invoke(messages)
        selected_urls = analysis_result.selected_reddit_urls

        print("Selected Reddit URLs for analysis:")
        for i, url in enumerate(selected_urls):
            print(f"Selected Reddit URL {i+1}: {url}")
    except Exception as e:
        print(f"Error during Reddit post analysis: {e}")
        selected_urls = []

    state['selected_reddit_urls'] = selected_urls
    return state

# => Node 5 : analyze google result
def retreive_data_from_reddit_post(state: AgentState) -> AgentState:
    """this node is for retrieving data from reddit post."""

    print("Getting reddit post comments...")

    selected_urls = state.get('selected_reddit_urls',[])

    if not selected_urls:
        return state

    print(f"Processing {len(selected_urls)} posts...")

    reddit_post_data = reddit_post_retrieval(selected_urls)

    if reddit_post_data:
        print(f"Successfully retreive {reddit_post_data.get('total_comments')} comments.")
    
    else:
        print("Failed to get post data")
        reddit_post_data = []    
    
    state['reddit_post_data'] = reddit_post_data

    return state


# => Node 6 : analyze google result
def analyze_google_result(state:AgentState) -> AgentState:
    """this node is for analyzing google result."""
    print("Analyzing Google search result...")

    user_question = get_user_question(state)

    google_results = state.get("google_results",[])

    if not google_results:
        return state

    messages = get_google_analysis_messages(user_question, google_results)

    analysis = llm.invoke(messages)

    state['google_analysis'] = analysis.content

    return state


# => Node 7 : analyze bing result :
def analyze_bing_result(state:AgentState) -> AgentState:
    """this node is for analyzing bing result."""

    print("Analyzing Bing search result...")

    user_question = get_user_question(state)

    bing_results = state.get("bing_results",[])

    if not bing_results:
        return state

    messages = get_bing_analysis_messages(user_question, bing_results)

    analysis = llm.invoke(messages)

    state['bing_analysis'] = analysis.content
    return state


# => Node 8 : analyze reddit result :
def analyze_reddit_result(state:AgentState) -> AgentState:
    """this node is for analyzing reddit result."""
    print("Analyzing Reddit result...")

    user_question = get_user_question(state)

    reddit_results = state.get("reddit_results",[])
    reddit_post_data = state.get("reddit_post_data",[])

    if not reddit_results:
        return state

    # Extract list of comments from the reddit_post_data dict
    reddit_posts_list = reddit_results.get("parsed_data", []) if isinstance(reddit_results, dict) else reddit_results
    reddit_comments_list = reddit_post_data.get("parsed_data", []) if isinstance(reddit_post_data, dict) else reddit_post_data

    messages = get_reddit_analysis_messages(user_question, reddit_posts_list, reddit_comments_list)

    analysis = llm.invoke(messages)

    state['reddit_analysis'] = analysis.content
    return state


# => Node 9 : synthesize analyses node :
def synthesize_analyses(state:AgentState) -> AgentState:
    """this node is for synthesizing all analyses."""
    print("Synthesizing all analyses...")

    user_question = get_user_question(state)

    google_analysis = state.get("google_analysis",[])
    bing_analysis = state.get("bing_analysis",[])
    reddit_analysis = state.get("reddit_analysis",[])

    messages = get_synthesis_messages(
        user_question,
        google_analysis,
        bing_analysis,
        reddit_analysis
    )

    analysis = llm.invoke(messages)

    state['final_result'] = analysis.content
    return state

    

    


# =============== > defining the graph < ===================

graph = StateGraph(AgentState)


# =============== > adding nodes < ===================

graph.add_node("google-search", google_search)
graph.add_node("reddit-search", reddit_search)
graph.add_node("bing-search", bing_search)

graph.add_node("analyze-google-result", analyze_google_result)
graph.add_node("analyze-bing-result", analyze_bing_result)

graph.add_node("analyze-reddit-post", analyze_reddit_post)
graph.add_node("retreive-reddit-post-data",retreive_data_from_reddit_post)
graph.add_node("analyze-reddit-result", analyze_reddit_result)

graph.add_node("synthesize-node", synthesize_analyses)

# =============== > adding edges to the graph < ===================
graph.add_edge(START, "google-search")
graph.add_edge(START, "reddit-search")
graph.add_edge(START, "bing-search")

graph.add_edge("google-search", "analyze-reddit-post")
graph.add_edge("reddit-search", "analyze-reddit-post")
graph.add_edge("bing-search", "analyze-reddit-post")

graph.add_edge("analyze-reddit-post", "retreive-reddit-post-data")

graph.add_edge("retreive-reddit-post-data", "analyze-reddit-result")
graph.add_edge("retreive-reddit-post-data", "analyze-google-result")
graph.add_edge("retreive-reddit-post-data", "analyze-bing-result")

graph.add_edge("analyze-reddit-result", "synthesize-node")
graph.add_edge("analyze-google-result", "synthesize-node")
graph.add_edge("analyze-bing-result", "synthesize-node")

graph.add_edge("synthesize-node", END)

app = graph.compile()


# =============== > running the chatbot < ===================
def run_chat_bot():
    print("======================> Welcome To mult-Agent Search <========================")
    print("Multi-source research agent: ")
    print("Type 'exit' to quit")
    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "exit":
            break

        initial_state = AgentState(
            messages=[HumanMessage(content=user_input)],
            google_results=None,
            bing_results=None,
            reddit_results=None,
            selected_reddit_urls=[],
            reddit_post_data=None,
            google_analysis=None,
            bing_analysis=None,
            reddit_analysis=None,
            final_result=None,
        )

        print("\nThinking...")
        final_state = app.invoke(initial_state)
        print("Search Completed, Final Result: \n")

        if final_state['final_result']:
            print(final_state['final_result'])
        
        else:
            print("No results found. Please try again with a different query.")
        

        print("-"*50)


if __name__ == "__main__":
    run_chat_bot()
