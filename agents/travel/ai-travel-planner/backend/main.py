from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware 
from langchain_core.messages import HumanMessage
from backend.graph import get_graph
from backend.state import TravelAgentState

app = FastAPI(title="Travel Agent API", description="AI-powered travel planning with flights and hotels")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the compiled graph
travel_graph = get_graph()

class TravelRequest(BaseModel):
    message: str
    thread_id: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    travelers: Optional[int] = None
    hotel_stars: Optional[int] = None
    budget: Optional[str] = None

class TravelResponse(BaseModel):
    flights_found: int
    hotels_found: int
    email_sent: bool
    status: str
    error: Optional[str] = None

@app.post("/travel", response_model=TravelResponse)
async def plan_travel(request: TravelRequest):
    """
    Plan travel by finding flights and hotels, then sending an email report.
    """
    try:
        # Create initial state
        initial_state = TravelAgentState(
            messages=[HumanMessage(content=request.message)],
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            travelers=request.travelers,
            hotel_stars=request.hotel_stars,
            budget=request.budget,
            flights=None,
            hotels=None,
            flights_searched=None,
            hotels_searched=None,
            email_sent=None,
            error=None
        )
        
        # Configure the graph execution
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Execute the travel planning workflow
        final_state = await travel_graph.ainvoke(initial_state, config)
        
        # Extract results
        flights = final_state.get('flights', [])
        hotels = final_state.get('hotels', [])
        email_sent = final_state.get('email_sent', False)
        error = final_state.get('error')
        
        return TravelResponse(
            flights_found=len(flights),
            hotels_found=len(hotels),
            email_sent=email_sent,
            status="success" if not error else "partial_success",
            error=error
        )
        
    except Exception as e:
        return TravelResponse(
            flights_found=0,
            hotels_found=0,
            email_sent=False,
            status="error",
            error=str(e)
        )

@app.get("/")
async def get_chat_interface():
    """Serve a simple HTML interface for testing the travel agent."""
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Travel Agent Chat</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .form-group { margin: 15px 0; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .response { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
                .status-success { border-left: 4px solid #28a745; }
                .status-error { border-left: 4px solid #dc3545; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Travel Agent</h1>
                <form id="travelForm">
                    <div class="form-group">
                        <label for="message">Travel Request:</label>
                        <textarea id="message" rows="3" placeholder="Find flights and hotels from New York to Los Angeles from 2025-07-15 to 2025-07-18 for 2 travelers"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="thread_id">Thread ID:</label>
                        <input type="text" id="thread_id" value="travel_001" placeholder="Unique identifier for this conversation">
                    </div>
                    <button type="submit">Plan My Travel</button>
                </form>
                <div id="response" class="response" style="display: none;"></div>
            </div>
            
            <script>
                document.getElementById('travelForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = {
                        message: document.getElementById('message').value,
                        thread_id: document.getElementById('thread_id').value
                    };
                    
                    const responseDiv = document.getElementById('response');
                    responseDiv.style.display = 'block';
                    responseDiv.innerHTML = '<p>Planning your travel... This may take a few minutes.</p>';
                    responseDiv.className = 'response';
                    
                    try {
                        const response = await fetch('/travel', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(formData)
                        });
                        
                        const result = await response.json();
                        
                        responseDiv.className = result.status === 'success' ? 'response status-success' : 'response status-error';
                        responseDiv.innerHTML = `
                            <h3>Travel Planning Results</h3>
                            <p><strong>Status:</strong> ${result.status}</p>
                            <p><strong>Flights Found:</strong> ${result.flights_found}</p>
                            <p><strong>Hotels Found:</strong> ${result.hotels_found}</p>
                            <p><strong>Email Sent:</strong> ${result.email_sent ? 'Yes' : 'No'}</p>
                            ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
                        `;
                    } catch (error) {
                        responseDiv.className = 'response status-error';
                        responseDiv.innerHTML = `<p><strong>Error:</strong> ${error.message}</p>`;
                    }
                });
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """
    WebSocket endpoint for real-time travel planning updates.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive travel request
            data = await websocket.receive_text()
            
            # Create initial state
            initial_state = TravelAgentState(
                messages=[HumanMessage(content=data)],
                origin=None,
                destination=None,
                departure_date=None,
                return_date=None,
                travelers=None,
                hotel_stars=None,
                budget=None,
                flights=None,
                hotels=None,
                flights_searched=None,
                hotels_searched=None,
                email_sent=None,
                error=None
            )
            
            config = {"configurable": {"thread_id": thread_id}}
            
            # Stream the workflow execution
            await websocket.send_text("Starting travel search...")
            
            async for step in travel_graph.astream(initial_state, config):
                for node_name, node_output in step.items():
                    if node_name == "find_flights":
                        flights = node_output.get('flights', [])
                        await websocket.send_text(f"Found {len(flights)} flights")
                        
                    elif node_name == "find_hotels":
                        hotels = node_output.get('hotels', [])
                        await websocket.send_text(f"Found {len(hotels)} hotels")
                        
                    elif node_name == "send_email":
                        email_sent = node_output.get('email_sent', False)
                        if email_sent:
                            await websocket.send_text("Email sent successfully!")
                        else:
                            await websocket.send_text("Email sending failed")
                    
                    if node_output.get('error'):
                        await websocket.send_text(f"Error in {node_name}: {node_output['error']}")
            
            await websocket.send_text("Travel planning completed!")
            
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)