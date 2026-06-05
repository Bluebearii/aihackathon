from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/ai", tags=["AI"])

# Initialize OpenAI Client lazily
def get_client():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sk-your-openai-api-key-here":
        return OpenAI(api_key=api_key)
    return None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    action: Optional[Dict[str, Any]] = None

# Define the tools available to the OpenAI model
tools = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Navigate the user to a specific page in the application. Use this ONLY after completing the booking workflow if they are booking an appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "enum": ["/", "/about", "/services", "/rewards", "/admin", "/analytics", "/book", "/dashboard", "/signup", "/login"],
                        "description": "The URL path to navigate to."
                    }
                },
                "required": ["page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_medical_history",
            "description": "Update the user's medical history form with conditions mentioned in the chat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of medical conditions to add to their history (e.g. 'Asthma', 'Diabetes')."
                    }
                },
                "required": ["conditions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "contact_agent",
            "description": "Notify a human support agent to contact the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urgency": {"type": "string", "enum": ["low", "high"]}
                },
                "required": ["urgency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "show_medical_options_ui",
            "description": "Call this tool to instantly display an interactive checklist of all common real-life medical conditions on the user's screen.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    client = get_client()
    if not client:
        return ChatResponse(
            message="I'm sorry, my AI brain is currently disconnected (Missing OPENAI_API_KEY).",
            action=None
        )

    # Build the intelligent system prompt
    system_msg_content = """
    You are CareBot, a helpful AI assistant for the WeCarePeople medical clinic. 
    Always be polite, concise, and professional.
    
    CRITICAL: If the user types "Medical History", asks to see a list of medical conditions, or asks for the medical history options, YOU MUST immediately call the `show_medical_options_ui` tool. DO NOT output conversational text saying you will do it. Just call the tool!
    
    *** CRITICAL BOOKING WORKFLOW ***
    If the user asks to book an appointment, YOU MUST strictly follow this exact conversational flow BEFORE calling the `navigate` tool to send them to /book:
    
    STEP 1: Ask the user to confirm their full name and Date of Birth for security purposes. Wait for their response.
    STEP 2: Once confirmed, ask them if they would like to provide any medical history or existing conditions right now. Tell them explicitly that doing this now via chat will save them time filling out forms at the clinic. Wait for their response.
    STEP 3: If they list conditions, call the `update_medical_history` tool. If they decline or say no, proceed to Step 4.
    STEP 4: You MUST immediately call the `navigate` tool with page="/book". DO NOT output text saying you are going to navigate them. Just call the tool!
    
    Never skip these steps when someone mentions booking an appointment!
    """
    
    if req.user_context:
        system_msg_content += f"\n\n[SYSTEM NOTE: The user is currently logged in. Their file shows Name: {req.user_context.get('name', 'Unknown')} and DOB: {req.user_context.get('dob', 'Unknown')}. You can use this information to ask them to confirm if these details are still correct.]"
    else:
        system_msg_content += "\n\n[SYSTEM NOTE: The user is NOT currently logged in. You must ask them for their name and DOB from scratch.]"

    system_msg = {
        "role": "system",
        "content": system_msg_content
    }
    
    openai_messages = [system_msg] + [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            action_dict = {
                "type": function_name,
                "payload": function_args
            }
            
            return ChatResponse(
                message=f"I am executing the {function_name.replace('_', ' ')} action for you now.",
                action=action_dict
            )
            
        else:
            return ChatResponse(
                message=response_message.content,
                action=None
            )

    except Exception as e:
        return ChatResponse(message=f"Oops, something went wrong: {str(e)}", action=None)

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    route: str

@router.post("/search", response_model=SearchResponse)
def search_endpoint(req: SearchRequest):
    client = get_client()
    if not client:
        return SearchResponse(route="/")

    prompt = f"""
    You are an intelligent router for a medical clinic web app.
    Given the user's search query, determine the best page to navigate them to.
    
    Available routes:
    / (Home)
    /about
    /services
    /book (Appointments)
    /dashboard (Patient portal)
    /rewards (Points system)
    /admin (Admin portal)
    /analytics (AI analytics)
    
    User query: "{req.query}"
    
    Output ONLY the exact route string, nothing else. Defaults to / if unsure.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        route = response.choices[0].message.content.strip()
        if route not in ["/", "/about", "/services", "/book", "/dashboard", "/rewards", "/admin", "/analytics", "/login", "/signup"]:
            route = "/"
        return SearchResponse(route=route)
    except Exception:
        return SearchResponse(route="/")
