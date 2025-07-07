import React, { useState, useEffect, useRef } from 'react';
import { Send, Plane, MapPin, Calendar, Users, Star, DollarSign, Loader, CheckCircle, AlertCircle, Globe, Sparkles } from 'lucide-react';

const TravelAgentUI = () => {
  const [formData, setFormData] = useState({
    message: '',
    thread_id: `travel_${Date.now()}`,
    origin: '',
    destination: '',
    departure_date: '',
    return_date: '',
    travelers: 1,
    hotel_stars: 3,
    budget: 'medium'
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [wsConnection, setWsConnection] = useState(null);
  const [realTimeUpdates, setRealTimeUpdates] = useState([]);
  const canvasRef = useRef(null);
  
  // Animated background particles
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particleArray = [];
    const numberOfParticles = 50;
    
    for (let i = 0; i < numberOfParticles; i++) {
      particleArray.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        dx: (Math.random() - 0.5) * 0.5,
        dy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2
      });
    }
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      particleArray.forEach(particle => {
        particle.x += particle.dx;
        particle.y += particle.dy;
        
        if (particle.x < 0 || particle.x > canvas.width) particle.dx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.dy *= -1;
        
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(59, 130, 246, ${particle.opacity})`;
        ctx.fill();
      });
      
      requestAnimationFrame(animate);
    };
    
    animate();
    
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const connectWebSocket = () => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${formData.thread_id}`);
    
    ws.onopen = () => {
      setWsConnection(ws);
      setRealTimeUpdates(prev => [...prev, { type: 'info', message: 'Connected to travel agent...', timestamp: new Date().toLocaleTimeString() }]);
    };
    
    ws.onmessage = (event) => {
      const message = event.data;
      setRealTimeUpdates(prev => [...prev, { 
        type: 'update', 
        message, 
        timestamp: new Date().toLocaleTimeString() 
      }]);
    };
    
    ws.onclose = () => {
      setWsConnection(null);
      setRealTimeUpdates(prev => [...prev, { type: 'info', message: 'Connection closed', timestamp: new Date().toLocaleTimeString() }]);
    };
    
    ws.onerror = (error) => {
      setRealTimeUpdates(prev => [...prev, { type: 'error', message: 'Connection error occurred', timestamp: new Date().toLocaleTimeString() }]);
    };
    
    return ws;
  };
  
  const handleSubmit = async () => {
    if (!formData.message.trim()) return;
    
    setIsLoading(true);
    setResponse(null);
    setRealTimeUpdates([]);
    
    // Connect WebSocket for real-time updates
    const ws = connectWebSocket();
    
    try {
      const apiResponse = await fetch('http://localhost:8000/travel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      const result = await apiResponse.json();
      setResponse(result);
      
      
    } catch (error) {
      setResponse({
        flights_found: 0,
        hotels_found: 0,
        email_sent: false,
        status: 'error',
        error: error.message
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 1 }}
      />
      
      {/* Floating Elements */}
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 2 }}>
        <div className="absolute top-20 left-10 w-2 h-2 bg-blue-400 rounded-full animate-ping opacity-75"></div>
        <div className="absolute top-40 right-20 w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
        <div className="absolute bottom-40 left-20 w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 right-10 w-3 h-3 bg-yellow-400 rounded-full animate-ping opacity-50"></div>
      </div>
      
      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-7xl lg:max-w-none px-4">

          {/* Header */}
          <div className="text-center mb-12">
            <div className="relative inline-block mb-8">
              <div className="absolute -inset-4 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 rounded-full animate-spin-slow opacity-30 blur-lg"></div>
              <div className="relative w-24 h-24 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-white/20 flex items-center justify-center group hover:scale-110 transition-all duration-500">
                <div className="absolute inset-1 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-xl"></div>
                <div className="relative">
                   <img 
                src="https://images-platform.99static.com/Ssqnkj-TRUV0Y7W4QfUdYIbItMU=/102x97:902x897/500x500/top/smart/99designs-contests-attachments/69/69386/attachment_69386648"
                alt="logo"
                className="h-20 w-auto opacity-80 hover:opacity-100 transition-opacity duration-300"
              />
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-ping"></div>
                </div>
              </div>
            </div>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-6">
              Discover your perfect journey with our intelligent travel planning assistant
            </p>
            
            {/* Powered by Bright Data */}
            <div className="flex items-center justify-center space-x-3 text-gray-400 text-sm">
              <span>Powered by</span>
              <img 
                src="https://idsai.net.technion.ac.il/files/2022/01/Logo-600.png"
                alt="Bright Data"
                className="h-30 w-auto opacity-80 hover:opacity-100 transition-opacity duration-300"
              />
            </div>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Travel Form */}
            <div className="lg:col-span-1">
              <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8">
                <div className="space-y-6">
                  {/* Travel Request */}
                  <div className="space-y-2">
                    <label className="flex items-center text-white font-medium text-lg">
                      <Sparkles className="w-5 h-5 mr-2 text-yellow-400" />
                      Tell us about your dream trip
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleInputChange}
                      onKeyPress={handleKeyPress}
                      className="w-full h-32 px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent backdrop-blur-sm resize-none transition-all duration-300"
                      placeholder="Find flights and hotels from New York to Los Angeles from 2025-07-15 to 2025-07-18 for 2 travelers with a budget of $2000"
                    />
                  </div>
                  
                  
                  {/* Submit Button */}
                  <button
                    onClick={handleSubmit}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-3xl disabled:opacity-50 disabled:transform-none flex items-center justify-center text-lg"
                  >
                    {isLoading ? (
                      <>
                        <Loader className="w-6 h-6 mr-3 animate-spin" />
                        Planning Your Journey...
                      </>
                    ) : (
                      <>
                        <Send className="w-6 h-6 mr-3" />
                        Plan My Dream Trip
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
            
            {/* Results & Real-time Updates */}
            <div className="space-y-6">
              {/* Real-time Updates */}
              <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <Plane className="w-5 h-5 mr-2 text-blue-400" />
                  Live Updates
                </h3>
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {realTimeUpdates.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-full mb-4">
                        <Plane className="w-8 h-8 text-blue-400 animate-pulse" />
                      </div>
                      <p className="text-gray-400">
                        Start planning to see live updates...
                      </p>
                    </div>
                  ) : (
                    realTimeUpdates.map((update, index) => (
                      <div key={index} className="p-3 bg-white/5 rounded-xl border border-white/10 animate-fadeIn">
                        <div className="flex items-start space-x-2">
                          {update.type === 'error' ? (
                            <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          ) : update.type === 'update' ? (
                            <CheckCircle className="w-4 h-4 text-green-400 mt-1" />
                          ) : (
                            <div className="w-4 h-4 bg-blue-400 rounded-full mt-1 animate-pulse" />
                          )}
                          <div className="flex-1">
                            <p className="text-white text-sm">{update.message}</p>
                            {update.timestamp && (
                              <p className="text-gray-400 text-xs mt-1">{update.timestamp}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
              
              {/* Results Summary */}
              {response && (
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-6 animate-fadeIn">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                    {response.status === 'success' ? (
                      <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                    ) : (
                      <AlertCircle className="w-5 h-5 mr-2 text-red-400" />
                    )}
                    Trip Summary
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Plane className="w-4 h-4 text-blue-400" />
                            <span className="text-gray-300">Flights</span>
                          </div>
                          <span className="text-2xl font-bold text-blue-400">{response.flights_found}</span>
                        </div>
                      </div>
                      
                      <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <MapPin className="w-4 h-4 text-purple-400" />
                            <span className="text-gray-300">Hotels</span>
                          </div>
                          <span className="text-2xl font-bold text-purple-400">{response.hotels_found}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Send className="w-4 h-4 text-green-400" />
                          <span className="text-gray-300">Email Report</span>
                        </div>
                        <div className="flex items-center">
                          {response.email_sent ? (
                            <>
                              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                              <span className="text-green-400 font-medium">Sent</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="w-4 h-4 text-red-400 mr-2" />
                              <span className="text-red-400 font-medium">Failed</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Globe className="w-4 h-4 text-blue-400" />
                          <span className="text-gray-300">Status</span>
                        </div>
                        <span className={`font-medium px-3 py-1 rounded-full text-sm ${
                          response.status === 'success' 
                            ? 'bg-green-400/20 text-green-400' 
                            : response.status === 'partial_success'
                            ? 'bg-yellow-400/20 text-yellow-400'
                            : 'bg-red-400/20 text-red-400'
                        }`}>
                          {response.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    
                    {response.error && (
                      <div className="bg-red-400/10 border border-red-400/20 rounded-xl p-4 animate-pulse">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <p className="text-red-400 text-sm">{response.error}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
      
      
      {/* Global Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          .animate-fadeIn {
            animation: fadeIn 0.5s ease-out;
          }
          
          /* Custom scrollbar */
          ::-webkit-scrollbar {
            width: 6px;
          }
          
          ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
          }
          
          ::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.5);
            border-radius: 3px;
          }
          
          ::-webkit-scrollbar-thumb:hover {
            background: rgba(59, 130, 246, 0.7);
          }
          
          /* Glassmorphism enhancement */
          .backdrop-blur-xl {
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
          }
          
          /* Smooth focus transitions */
          input:focus, textarea:focus, select:focus {
            transform: scale(1.02);
          }
          
          /* Hover effects */
          button:hover:not(:disabled) {
            box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
          }
        `
      }} />
    </div>
  );
};

export default TravelAgentUI;