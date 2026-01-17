from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from backend.app.api.settings import load_settings_from_file
from llm.interface import LLMAgent
from data.baostock_provider import data_provider
import datetime
import json
import asyncio

# Import strategies
from strategies.technical import MovingAverageStrategy, VolumeRiseStrategy, HighTurnoverStrategy
from strategies.fundamental import LowPeStrategy, HighGrowthStrategy, HighRoeStrategy, LowDebtStrategy

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list = [] # List of {role, content}
    context: str = "general" 

def get_market_context():
    """
    Fetches real-time market context (Shanghai Composite Index).
    """
    try:
        # Get data for the last 10 days to ensure we find a trading day
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        
        # sh.000001 is the Shanghai Composite Index
        df = data_provider.get_daily_bars('sh.000001', start_date, end_date)
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            date = latest['date']
            close = float(latest['close'])
            pct_chg = float(latest['pctChg'])
            volume = float(latest['volume'])
            
            trend = "UP" if pct_chg > 0 else "DOWN"
            
            context_str = (
                f"Market Status (Shanghai Composite as of {date}):\n"
                f"- Close: {close:.2f}\n"
                f"- Change: {pct_chg:.2f}% ({trend})\n"
                f"- Volume: {volume:,.0f}\n"
            )
            return context_str
    except Exception as e:
        print(f"Error fetching market context: {e}")
        
    return "Market Status: Market data currently unavailable."

def get_available_strategies():
    """
    Returns a formatted string of available strategies.
    """
    strategies = [
        MovingAverageStrategy(),
        VolumeRiseStrategy(),
        HighTurnoverStrategy(),
        LowPeStrategy(),
        HighGrowthStrategy(),
        HighRoeStrategy(),
        LowDebtStrategy()
    ]
    
    info_list = []
    for i, s in enumerate(strategies, 1):
        info_list.append(f"{i}. {s.name}: {s.description}")
        
    strategies_desc = "\n".join(info_list)
    
    return (
        f"{strategies_desc}\n\n"
        f"RESPONSE FORMAT INSTRUCTIONS:\n"
        f"If the user asks for stock recommendations or you are providing specific stock picks, "
        f"you MUST output a strict JSON block at the end of your response formatted as follows:\n"
        f"```json\n"
        f"{{\n"
        f"  \"recommendations\": [\n"
        f"    {{\"code\": \"600000\", \"name\": \"Pudong Bank\", \"reason\": \"Short reason here\", \"strategy\": \"Low_PE\"}}\n"
        f"  ],\n"
        f"  \"analysis\": \"General market analysis text here...\"\n"
        f"}}\n"
        f"```\n"
        f"For general questions without stock picks, just answer normally."
    )

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI Assistant using the configured provider.
    """
    settings = load_settings_from_file()
    
    # Convert Pydantic settings to dict
    ai_settings = settings.ai.model_dump()
    
    # Initialize Agent
    agent = LLMAgent(ai_settings)
    
    # Get Market Context
    market_context = get_market_context()
    
    # Get Strategy Context
    strategy_context = get_available_strategies()
    
    # Combine Contexts
    full_context = (
        f"{market_context}\n\n"
        f"AVAILABLE STRATEGIES (You can recommend these to users):\n"
        f"{strategy_context}"
    )
    
    # Prepare messages history (ensure valid format)
    messages = []
    for msg in request.history:
        # Validate role
        role = msg.get("role")
        if role not in ["user", "assistant", "system"]:
            continue
        messages.append({"role": role, "content": msg.get("content", "")})
    
    # Add current message
    messages.append({"role": "user", "content": request.message})

    async def event_generator():
        async for chunk in agent.chat_stream(messages, context_data=full_context):
            # Server-Sent Events format
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
