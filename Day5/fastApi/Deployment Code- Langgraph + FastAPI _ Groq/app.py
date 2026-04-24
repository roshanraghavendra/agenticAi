# =========================================================
#  Agentic AI API (FastAPI + LangGraph + Groq)
# Single-file production-style starter
# =========================================================

import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict

# LangGraph
from langgraph.graph import StateGraph, END

# Groq LLM
from langchain_community.chat_models import ChatGroq
from langchain_core.messages import HumanMessage

# Optional RAG
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# =========================================================
#  CONFIG
# =========================================================
# Set this in your environment:
# export GROQ_API_KEY=""

# =========================================================
#  FastAPI INIT
# =========================================================
app = FastAPI(title="Agentic AI API")

# =========================================================
#  Request Schema
# =========================================================
class QueryRequest(BaseModel):
    question: str

# =========================================================
#  Agent State
# =========================================================
class AgentState(TypedDict):
    question: str
    context: str
    answer: str

# =========================================================
#  LLM (Groq)
# =========================================================
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# =========================================================
#  SIMPLE RAG SETUP (in-memory)
# =========================================================
documents = [
    "LangGraph is a framework for building stateful AI agents.",
    "FastAPI is a high-performance Python web framework.",
    "Groq provides ultra-fast inference for LLMs.",
    "RAG combines retrieval with generation."
]

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = embed_model.encode(documents)

index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(np.array(doc_embeddings))


def retrieve(query, k=2):
    q_emb = embed_model.encode([query])
    _, indices = index.search(np.array(q_emb), k)
    return [documents[i] for i in indices[0]]

# =========================================================
#  NODE 1: RETRIEVE CONTEXT
# =========================================================
def retrieve_node(state: AgentState):
    question = state["question"]
    docs = retrieve(question)
    context = "\n".join(docs)

    return {"context": context}

# =========================================================
#  NODE 2: GENERATE ANSWER
# =========================================================
def generate_node(state: AgentState):
    question = state["question"]
    context = state["context"]

    prompt = f"""
    Answer ONLY from context:
    {context}

    Question: {question}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    return {"answer": response.content}

# =========================================================
#  NODE 3: REFLECTION (self-improvement)
# =========================================================
def reflect_node(state: AgentState):
    answer = state["answer"]

    improved = llm.invoke([
        HumanMessage(content=f"Improve this answer:\n{answer}")
    ])

    return {"answer": improved.content}

# =========================================================
#  BUILD LANGGRAPH
# =========================================================
graph = StateGraph(AgentState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_node("reflect", reflect_node)

graph.set_entry_point("retrieve")

graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "reflect")
graph.add_edge("reflect", END)

app_graph = graph.compile()

# =========================================================
#  SIMPLE EVALUATION
# =========================================================
def faithfulness(answer, context):
    a = set(answer.lower().split())
    c = set(context.lower().split())
    return len(a & c) / max(len(a), 1)

# =========================================================
#  API ENDPOINT
# =========================================================
@app.post("/ask")
def ask(req: QueryRequest):
    result = app_graph.invoke({
        "question": req.question
    })

    score = faithfulness(result["answer"], result["context"])

    return {
        "question": req.question,
        "answer": result["answer"],
        "context": result["context"],
        "faithfulness_score": score
    }

# =========================================================
#  HEALTH CHECK
# =========================================================
@app.get("/")
def root():
    return {"message": "Agentic AI API is running "}
