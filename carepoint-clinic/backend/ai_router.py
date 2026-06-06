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
            "description": "Navigate the user to a specific page in the application. Use this ONLY after completing the booking workflow if they are booking an appointment, or when user explicitly asks to go somewhere.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "enum": ["/", "/about", "/services", "/rewards", "/admin", "/analytics", "/book", "/dashboard", "/signup", "/login", "/medical-history", "/admin/calendar", "/admin/patients"],
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
            "name": "show_medical_history_form",
            "description": "Call this tool when the user clicks 'Medical History' or asks about their medical history form. This shows an interactive full medical history form with all conditions from the clinic form. This is ONLY for medical history - NOT for booking appointments.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
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
    You are CareBot, a helpful AI assistant for the Care Flow AI medical clinic. 
    Always be polite, concise, and professional.
    
    *** CRITICAL: MEDICAL HISTORY vs BOOKING ARE SEPARATE FLOWS ***
    
    MEDICAL HISTORY FLOW (when user types "Medical History" or asks about medical history):
    - This is ONLY about filling out their medical history form. DO NOT ask about appointments.
    - Call the `show_medical_history_form` tool IMMEDIATELY to display the interactive form.
    - The form will ask about: patient name, height/weight, allergies, diagnosis, hospitalization history, 
      surgeries, falls, previous treatments, imaging tests (EMG, CT Scan, MRI, X-Ray), 
      and all 44 medical conditions from the clinic form.
    - Auto-fill their name if they are logged in.
    - DO NOT redirect to booking. DO NOT ask about appointments. Stay focused on medical history only.
    
    BOOKING FLOW (ONLY when user explicitly says "Book Appointment" or asks to book):
    - STEP 1: Ask the user to confirm their full name and Date of Birth. Wait for response.
    - STEP 2: Ask if they want to provide medical history now. Wait for response.
    - STEP 3: If they list conditions, call `update_medical_history`. If they decline, proceed.
    - STEP 4: Call `navigate` with page="/book" to send them to the booking page.
    
    These are COMPLETELY SEPARATE flows. Never mix them up.
    
    OTHER ACTIONS:
    - If user asks to talk to an agent, call `contact_agent`.
    - If user asks about insurance, explain the clinic accepts most major providers.
    - If user asks about points/rewards, explain the rewards system.
    """
    
    if req.user_context:
        system_msg_content += f"\n\n[SYSTEM NOTE: The user is currently logged in. Their file shows Name: {req.user_context.get('name', 'Unknown')} and DOB: {req.user_context.get('dob', 'Unknown')}. You can use this information to auto-fill forms and greet them by name.]"
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
            
            # Customize response message based on action
            if function_name == "show_medical_history_form":
                msg = "I'll pull up your medical history form now. Please review and fill in all the conditions below:"
            elif function_name == "navigate":
                msg = f"Taking you to the requested page now."
            elif function_name == "update_medical_history":
                msg = "I've updated your medical history with those conditions."
            else:
                msg = f"I am executing the {function_name.replace('_', ' ')} action for you now."
            
            return ChatResponse(
                message=msg,
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
    /admin/calendar (Calendar)
    /admin/patients (Patient database)
    /medical-history (Medical history form)
    
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
        valid_routes = ["/", "/about", "/services", "/book", "/dashboard", "/rewards", "/admin", "/analytics", "/login", "/signup", "/admin/calendar", "/admin/patients", "/medical-history"]
        if route not in valid_routes:
            route = "/"
        return SearchResponse(route=route)
    except Exception:
        return SearchResponse(route="/")
