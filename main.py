from langchain.messages import HumanMessage, ToolMessage,SystemMessage
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Annotated, Sequence
from langgraph.graph.message import BaseMessage, add_messages
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]
    user_input:HumanMessage | None
    google_result:str | None 
    bing_result : str | None
    reddit_result : str | None
    selected_reddit_urls: List[str]
    reddit_post_data:str | None
    google_analysis:str | None
    reddit_analysis: str | None
    bing_analysis : str | None
    final_result : str | None



# =============== > defining our nodes that we will need < ===================

# => Node 1 : google search 
def google_search(state:AgentState) -> AgentState:
    pass

# => Node 2 : reddit search : 
def reddit_search(state:AgentState) -> AgentState:
    pass

# => Node 3 : Bing Search :
def bing_search(state:AgentState) -> AgentState:
    pass

# => Node 4 : analyze reddit post
def analyze_reddit_post(state:AgentState) -> AgentState:
    pass

# => Node 5 : analyze google result
def retreive_data_from_reddit_post(state: AgentState) -> AgentState:
    pass


# => Node 6 : analyze google result
def analyze_google_result(state:AgentState) -> AgentState:
    pass


# => Node 7 : analyze bing result :
def analyze_bing_result(state:AgentState) -> AgentState:
    pass


# => Node 8 : analyze reddit result :
def analyze_reddit_result(state:AgentState) -> AgentState:
    pass


# => Node 9 : synthesize analyses node :
def synthesize_analyses(state:AgentState) -> AgentState:
    pass


# =============== > defining the graph < ===================

graph = StateGraph(AgentState)


# =============== > adding nodes < ===================

graph.add_node("google-search", google_search)
graph.add_node("reddit-search", reddit_search)
graph.add_node("bing-search", bing_search)

graph.add_node("analyze-goole-result", analyze_google_result)
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
    print("Multi-source research agent: ")
    print("Type 'exit' to quit \n")
    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "exit":
            break

        initial_state = AgentState(
            messages=[HumanMessage(content=user_input)],
            user_input=HumanMessage(content=user_input), 
            google_result=None, 
            bing_result=None, 
            reddit_result=None, 
            selected_reddit_urls=[], 
            reddit_post_data=None, 
            google_analysis=None, 
            reddit_analysis=None, 
            bing_analysis=None
        )

        print("\n Starting parallel reseach process...\n")
        print("Google search...\n")
        print("Reddit search...\n")
        print("Bing search...\n")
        print("Analyzing results...\n")
        print("Synthesizing analyses...\n")
        final_state = app.invoke(initial_state)
        print("\nResearch completed. Here are the results:\n")

        if final_state['final_result']:
            print(final_state['final_result'])
        
        else:
            print("No results found. Please try again with a different query.")
        

        print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    run_chat_bot()
