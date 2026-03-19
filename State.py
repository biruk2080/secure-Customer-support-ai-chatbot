from typing_extensions import Literal
from typing import TypedDict, List
from pydantic.v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel, Field
load_dotenv()
from langchain_community.vectorstores import Chroma 
from langchain_openai import OpenAIEmbeddings
from guardrail import detect_prompt_injection
from splunk_logger import send_to_splunk 
# vector access instance 
REVIEWS_CHROMA_PATH = "chroma_data/"
JAIBREAK_CHROMA_PATH = "chroma_jailbreak"
reviews_vector_db = Chroma(
    persist_directory=REVIEWS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings()
)
injection_vector = Chroma(
     persist_directory=JAIBREAK_CHROMA_PATH,
     embedding_function=OpenAIEmbeddings(),
 )  

class Route(BaseModel):
    step: Literal["Product", "Billing", "Technical"] = Field(
        None, description="The next step in the routing process"
    )
# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)
# Augment the LLM with schema for structured output
router = llm.with_structured_output(Route)

# State
class State(TypedDict):
    input: str
    decision: str
    output: str

# Nodes
def product(state: State):
    """Product related question"""

    print("Answer product related question")
    # Search the vector database for relevant reviews
    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    return {"output": result.content,"decision": state["decision"]}


def billing(state: State):
    """Handle billing related questions"""
    print("Answer billing related question")
    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    
    return {"output": result.content,"decision": state["decision"]}

def technical(state: State):
    """Handle technical related questions"""
    print("Answer technical related question")
    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    return {"output": result.content,"decision": state["decision"]}

def llm_call_router(state: State):
    """Route the input to the appropriate node"""

    # Run the augmented LLM with structured output to serve as routing logic
    decision = router.invoke(
        [
            SystemMessage(
                content="Route the input to product, billing, or technical based on the user's request."
            ),
            HumanMessage(content=state["input"]),
        ]
    )

    return {"decision": decision.step}

# Conditional edge function to route to the appropriate node
def route_decision(state: State):
    # Return the node name you want to visit next
    decision = state["decision"].lower() if state["decision"] else ""
    if decision == "product":
        return "product"
    elif decision == "billing":
        return "billing"
    elif decision == "technical":
        return "technical"
# Build the graph
graph = StateGraph(State)
graph.add_node("product", product)
graph.add_node("billing", billing)
graph.add_node("technical", technical)
graph.add_node("router", llm_call_router)   

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "product": "product",
        "billing": "billing",
        "technical": "technical",
    },
)
graph.add_edge("product", END)
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.set_entry_point("router")
chain = graph.compile()

def run_agent(user_input):
    detection = detect_prompt_injection(user_input)

    if detection["blocked"]:
        send_to_splunk({
            "event": {
                "alert_type": "prompt_injection",
                "layer": detection["layer"],
                "user_input": user_input
            },
            "sourcetype": "_json",
            "index": "main"
        })
        return "⚠️ Prompt injection detected and blocked."

    state = State(input=user_input, decision="", output="")
    final_state = chain.invoke(state)

    send_to_splunk({
        "event": {
            "alert_type": "Allowed input",
            "user_input": user_input,
            "Router_decision": final_state["decision"],
            "response": final_state["output"]
        },
        "sourcetype": "_json",
        "index": "main"
    })

    return final_state["output"]
