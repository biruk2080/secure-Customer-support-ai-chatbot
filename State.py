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
import time
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
# Define the schema for routing decisions
class Route(BaseModel):
    step: Literal["Product", "Billing", "Technical"] = Field(
        None, description="The next step in the routing process"
    )
    reason: str = Field(
        None, description="Explanation for why this route was chosen"
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
    reason: str
    output: str

# time tracking variables
retrieval_time = None
llm_response_time = None
route_time = None

# Nodes
def product(state: State):
    """Handle product related questions"""
    # Search the vector database for relevant reviews
    global retrieval_time, llm_response_time
    retrieval_time_start = time.time()

    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""

    retrieval_time = time.time() - retrieval_time_start

    llm_response_time_start = time.time()
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    llm_response_time = time.time() - llm_response_time_start
    # Log retrieval and LLM response times to Splunk
    
    return {"output": result.content,"decision": state["decision"],"reason": state["reason"]}


def billing(state: State):
    """Handle billing related questions"""
    global retrieval_time, llm_response_time
    
    retrieval_time_start = time.time()
    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""
    retrieval_time = time.time() - retrieval_time_start

    llm_response_time_start = time.time()
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    llm_response_time = time.time() - llm_response_time_start
    
    return {"output": result.content,"decision": state["decision"],"reason": state["reason"]}

def technical(state: State):
    """Handle technical related questions"""
    global retrieval_time, llm_response_time
   
    retrieval_time_start = time.time()
    search_results = reviews_vector_db.similarity_search(state["input"], k=3)
    context = search_results[0].page_content if search_results else ""
    retrieval_time = time.time() - retrieval_time_start
   
    llm_response_time_start = time.time()
    result = llm.invoke(f"{state['input']}\nContext: {context}")
    llm_response_time = time.time() - llm_response_time_start
    
    return {"output": result.content,"decision": state["decision"],"reason": state["reason"]}

def llm_call_router(state: State):
    """Route the input to the appropriate node"""
    # route_ timer start
    global route_time
    start_time = time.time()
    # Run the augmented LLM with structured output to serve as routing logic
    decision = router.invoke(
        [
            SystemMessage(
                content=(
                "You are a routing assistant that categorizes user queries into one of three categories: "
                "'Product', 'Billing', or 'Technical'.\n\n"
                "Your task is to carefully read the user's input and determine the most appropriate category.\n"
                "You must also provide a concise, clear reason explaining why you chose that category.\n\n"
                "Output requirements:\n"
                "1. 'step' field: one of ['Product', 'Billing', 'Technical'].\n"
                "2. 'reason' field: a short, precise explanation (1-2 sentences) describing why this category was selected.\n\n"
                "Examples:\n"
                "Input: 'I want to know why my invoice is higher this month.'\n"
                "Output: step='Billing', reason='The user is asking about their invoice, which is related to billing.'\n\n"
                "Input: 'My device won't turn on after the update.'\n"
                "Output: step='Technical', reason='The issue is about device functionality, which is a technical problem.'\n\n"
                "Now analyze the user's input and provide the structured output exactly as specified."
            )
            ),
            HumanMessage(content=state["input"]),
        ]
    )
    route_time = time.time() - start_time
    return {
        "decision": decision.step,
        "reason": decision.reason
    }

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

    state = State(input=user_input, decision="", output="", reason="")
    final_state = chain.invoke(state)

    send_to_splunk({
        "event": {
            "alert_type": "Allowed input",
            "user_input": user_input,
            "Router_decision": final_state["decision"],
            "reason": final_state["reason"],
            "response": final_state["output"],
            "retrieval_time": retrieval_time,
            "llm_response_time": llm_response_time,
            "route_time": route_time,
            "total_processing_time": retrieval_time + llm_response_time + route_time
        },
        "sourcetype": "_json",
        "index": "main"
    })

    return final_state["output"]
