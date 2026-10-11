"""Simple local teaching example. Run: uvicorn app:app --port 8001"""
from fastapi import FastAPI, Header, HTTPException
import httpx
from langchain_core.messages import HumanMessage, AIMessage
from session_tools import API_URL
from redis_memory import save_message, load_history

from shop_tools import chain

app = FastAPI()

# One conversation per login token, kept in this backend process.



@app.post("/chat")
def chat(user_input: dict, authorization: str = Header()):
    # Streamlit sends: Authorization: Bearer <shopping login token>
    # This is the token Streamlit received when you signed in.
    login_token = authorization.removeprefix("Bearer ")

    # For this demo, use the login token as the user's history ID.

    # For the demo only, ideally save token_id:user_id in a database and use the user_id for chat history.
    user = httpx.get(f'{API_URL}/me',
                    headers={'Authorization': authorization}, timeout=30)
    if user.status_code == 401:
        raise HTTPException(401, 'Please sign in again.')
    user.raise_for_status()

    user_id = user.json()['customer_id']

    history = load_history(user_id)


    # Send the question, history, and login token to our chain.
    response = chain.invoke(
        {"query": user_input["query"], "history": history.messages},
        config={"configurable": {"user_id": user_id, "login_token": login_token}},
    )

    # Save the question and answer for the next request.
    save_message(user_id, HumanMessage(content=user_input["query"]))
    save_message(user_id, AIMessage(content=response.content))

    return {"answer": response.content}



