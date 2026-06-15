from langchain.messages import HumanMessage, ToolMessage,SystemMessage
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Annotated, Sequence
from langgraph.graph.message import BaseMessage, add_messages
from dotenv import load_dotenv
from webscrapping import serp_search
load_dotenv()

# Reducer function to handle multiple updates - just returns the latest value
def last_value(left, right):
    return right if right is not None else left

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]
    google_results: Annotated[List[str] | None, last_value]
    bing_results : Annotated[List[str] | None, last_value]
    reddit_results : Annotated[List[str] | None, last_value]

    selected_reddit_urls: List[str]
    reddit_post_data:str | None
    google_analysis:str | None
    reddit_analysis: str | None
    bing_analysis : str | None
    final_result : str | None



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

    reddit_results = None

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
    return state

# => Node 5 : analyze google result
def retreive_data_from_reddit_post(state: AgentState) -> AgentState:
    return state


# => Node 6 : analyze google result
def analyze_google_result(state:AgentState) -> AgentState:
    return state


# => Node 7 : analyze bing result :
def analyze_bing_result(state:AgentState) -> AgentState:
    return state


# => Node 8 : analyze reddit result :
def analyze_reddit_result(state:AgentState) -> AgentState:
    return state


# => Node 9 : synthesize analyses node :
def synthesize_analyses(state:AgentState) -> AgentState:
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

        initial_state = AgentState(messages=[HumanMessage(content=user_input)])

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
