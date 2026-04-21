import React, { useState, useRef, useEffect } from "react";
import { Container, Card, Form, Row, Col} from "react-bootstrap";
import { FaRobot, FaUser, FaPaperPlane } from "react-icons/fa6";
// استيراد الـ API
import { sendChatMessage } from "../api/chat.api";

function ChatAssistant() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  // حالة جديدة عشان نظهر إن البوت بيكتب
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]); // ضفنا isTyping عشان ينزل لتحت وهو بيكتب برضه

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. إضافة رسالة اليوزر
    const newUserMsg = { id: Date.now(), text, sender: "user", time: currentTime };
    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue("");
    
    // 2. إظهار إن البوت بيكتب
    setIsTyping(true);

    try {
      // 3. إرسال الرسالة للـ API الوهمي
      const response = await sendChatMessage(text);
      
      // 4. استلام الرد وإضافته
      const newBotMsg = { 
        id: Date.now() + 1, 
        text: response.reply, 
        sender: "bot", 
        time: response.timestamp 
      };
      setMessages((prev) => [...prev, newBotMsg]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      // 5. إخفاء علامة الكتابة
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  const suggestions = [
    "Drug Resistance Mechanisms",
    "Biological Pathways",
    "Gene Functions",
    "Treatment Alternatives"
  ];

  return (
    <div className="chat-page py-4">
      <style>
        {`
          /* الستايل بتاعك زي ما هو بالظبط، ضفت بس حتة الـ typing */
          .chat-page { background-color: #f8fafc; min-height: calc(100vh - 70px); font-family: 'Segoe UI', system-ui, sans-serif; }
          .chat-container-card { border: 1px solid #e2e8f0; border-radius: 12px; background: white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; height: 65vh; }
          .welcome-icon-wrapper { font-size: 3rem; color: #0f766e; margin-bottom: 10px; }
          .suggestion-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; font-size: 0.9rem; font-weight: 500; color: #334155; cursor: pointer; transition: all 0.2s ease; text-align: left; height: 100%; display: flex; align-items: center; }
          .suggestion-box:hover { background-color: #f0fdfa; border-color: #14b8a6; color: #0f766e; }
          .messages-area { flex-grow: 1; overflow-y: auto; padding: 20px; background-color: #ffffff; }
          .message-row { display: flex; gap: 12px; margin-bottom: 20px; }
          .message-row.user { justify-content: flex-end; flex-direction: row-reverse; }
          .avatar-circle { width: 35px; height: 35px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 1rem; flex-shrink: 0; }
          .bot-avatar { background-color: #14b8a6; color: white; }
          .user-avatar { background-color: #e2e8f0; color: #64748b; }
          .message-bubble { padding: 12px 16px; border-radius: 12px; max-width: 75%; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; }
          .bot-bubble { background-color: #ffffff; border: 1px solid #e2e8f0; color: #334155; border-top-left-radius: 2px; }
          .user-bubble { background-color: #14b8a6; color: white; border-top-right-radius: 2px; }
          .message-time { font-size: 0.7rem; opacity: 0.7; margin-top: 5px; text-align: right; }
          .input-area { padding: 15px 20px; border-top: 1px solid #e2e8f0; background-color: #ffffff; }
          .chat-input { background-color: #f1f5f9; border: none; padding: 12px 20px; border-radius: 20px; font-size: 0.95rem; color: #334155; }
          .chat-input:focus { background-color: #e2e8f0; box-shadow: none; outline: none; }
          .send-btn { background-color: #5eead4; color: white; border: none; width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 1.1rem; transition: background-color 0.2s; }
          .send-btn:hover { background-color: #2dd4bf; color: white; }
          .send-btn:disabled { background-color: #cbd5e1; cursor: not-allowed; }
          .messages-area::-webkit-scrollbar { width: 8px; }
          .messages-area::-webkit-scrollbar-track { background: #f1f1f1; }
          .messages-area::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
          .messages-area::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
          
          /* أنيميشن الكتابة */
          .typing-indicator { display: flex; gap: 4px; padding: 4px 8px; align-items: center; }
          .dot { width: 6px; height: 6px; background-color: #94a3b8; border-radius: 50%; animation: blink 1.4s infinite both; }
          .dot:nth-child(1) { animation-delay: 0.2s; }
          .dot:nth-child(2) { animation-delay: 0.4s; }
          .dot:nth-child(3) { animation-delay: 0.6s; }
          @keyframes blink { 0%, 80%, 100% { opacity: 0.2; } 40% { opacity: 1; } }
        `}
      </style>

      <Container style={{ maxWidth: "1000px" }}>
        <div className="mb-4">
          <h3 className="fw-bold text-dark mb-1">AI Chat Assistant</h3>
          <p className="text-secondary" style={{ fontSize: "0.95rem" }}>
            Ask questions about your analysis results, biological mechanisms, and treatment options
          </p>
        </div>

        <Card className="chat-container-card">
          <div className="messages-area">
            {messages.length === 0 ? (
              <div className="d-flex flex-column align-items-center justify-content-center h-100 text-center px-3">
                <div className="welcome-icon-wrapper"><FaRobot /></div>
                <h5 className="fw-bold mb-2" style={{ color: "#0f2027" }}>Welcome to the AI Assistant</h5>
                <p className="text-secondary mb-4" style={{ fontSize: "0.95rem" }}>
                  I can help you understand your analysis results and answer questions about:
                </p>
                <Container style={{ maxWidth: "600px" }}>
                  <Row className="g-3">
                    {suggestions.map((suggestion, idx) => (
                      <Col md={6} key={idx}>
                        <div className="suggestion-box shadow-sm" onClick={() => handleSendMessage(`Tell me about ${suggestion}`)}>
                          {suggestion}
                        </div>
                      </Col>
                    ))}
                  </Row>
                </Container>
              </div>
            ) : (
              <div>
                {messages.map((msg) => (
                  <div key={msg.id} className={`message-row ${msg.sender}`}>
                    <div className={`avatar-circle ${msg.sender === "bot" ? "bot-avatar" : "user-avatar"}`}>
                      {msg.sender === "bot" ? <FaRobot /> : <FaUser />}
                    </div>
                    <div className={`message-bubble ${msg.sender === "bot" ? "bot-bubble shadow-sm" : "user-bubble shadow-sm"}`}>
                      <div dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                      <div className="message-time">{msg.time}</div>
                    </div>
                  </div>
                ))}
                
                {/* مؤشر إن البوت بيكتب */}
                {isTyping && (
                  <div className="message-row bot">
                    <div className="avatar-circle bot-avatar"><FaRobot /></div>
                    <div className="message-bubble bot-bubble shadow-sm">
                      <div className="typing-indicator">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="input-area">
            {/* قفلنا الزرار والإنبوت لو البوت لسة بيكتب */}
            <Form className="d-flex gap-2" onSubmit={(e) => { e.preventDefault(); handleSendMessage(inputValue); }}>
              <Form.Control
                type="text"
                placeholder="Ask a question about the analysis..."
                className="chat-input flex-grow-1"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                autoComplete="off"
                disabled={isTyping} 
              />
              <button type="submit" className="send-btn flex-shrink-0" disabled={!inputValue.trim() || isTyping}>
                <FaPaperPlane />
              </button>
            </Form>
          </div>
        </Card>
      </Container>
    </div>
  );
}

export default ChatAssistant;