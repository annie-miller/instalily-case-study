import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

// Simple ProductCard component for demonstration
function ProductCard({ product }) {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} className="product-image" />
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        <div className="product-number">Part #{product.partNumber}</div>
        <div className="product-price">${product.price}</div>
        <button className="add-to-cart-btn">Add to Cart</button>
      </div>
    </div>
  );
}

function ChatWindow() {
  const defaultMessage = [{
    role: "assistant",
    content: "Hi, how can I help you today?"
  }];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCategoryOptions, setShowCategoryOptions] = useState(false);

  const messagesEndRef = useRef(null);
  const chatWindowRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Scroll chat window into view on mount
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollIntoView({ behavior: "auto", block: "start" });
    }
  }, []);

  const handleSend = async (input) => {
    if (input.trim() !== "" && !loading) {
      setMessages(prevMessages => {
        const updatedMessages = [...prevMessages, { role: "user", content: input }];
        setLoading(true);
        setError(null);
        (async () => {
          const history = updatedMessages.filter((msg, idx) => idx !== 0);
          try {
            const newMessage = await getAIMessage(input, history);
            setMessages(current => [...current, newMessage]);
          } catch (err) {
            setError("Failed to get response. Please try again.");
          } finally {
            setLoading(false);
          }
        })();
        return updatedMessages;
      });
    }
  };

  // Handle quick action for 'Find a part'
  const handleFindPart = () => {
    setShowCategoryOptions(true);
  };

  // Handle category selection
  const handleCategorySelect = (category) => {
    setShowCategoryOptions(false);
    handleSend(`Show me ${category.toLowerCase()} parts.`);
  };

  // Handle Installation Help button: prefill input and prompt user
  const handleInstallationHelp = () => {
    setInput('Please provide instructions for installing part number');
    setTimeout(() => {
      setMessages(prevMessages => ([
        ...prevMessages,
        { role: 'assistant', content: 'Please enter your part number so I can assist you with installation instructions.' }
      ]));
    }, 100); // Slight delay to ensure input is set first
  };

  // Handle Model Compatibility button: prefill input and prompt user
  const handleModelCompatibility = () => {
    setInput('Is this part compatible with my model?');
    setTimeout(() => {
      setMessages(prevMessages => ([
        ...prevMessages,
        { role: 'assistant', content: 'Please enter your part number and your appliance model number so I can check compatibility.' }
      ]));
    }, 100);
  };

  // Quick action buttons for common queries
  const quickActions = [
    {
      label: "Find a part",
      query: "Show me refrigerator parts for Whirlpool."
    },
    {
      label: "Order status",
      query: "Check my order status."
    },
    {
      label: "Installation help",
      query: "How do I install part number PS11752778?"
    },
    {
      label: "Model compatibility",
      query: "Is this part compatible with model WDT780SAEM1?"
    }
  ];

  // Render message content, supporting product cards and order status
  const renderMessageContent = (message) => {
    // Example: If the message contains a product card marker, render a product card
    if (message.product) {
      return <ProductCard product={message.product} />;
    }
    // Example: If the message contains order status info
    if (message.orderStatus) {
      return (
        <div className="order-status">
          <strong>Order Status:</strong> {message.orderStatus}
        </div>
      );
    }
    // Default: render markdown
    return (
      <div dangerouslySetInnerHTML={{ __html: marked(message.content).replace(/<p>|<\/p>/g, "") }}></div>
    );
  };

  return (
    <div className="chat-window-container" ref={chatWindowRef}>
      <div className="messages-container">
        <div className="quick-actions-row">
          <button
            className="quick-action-btn"
            onClick={handleFindPart}
            disabled={loading}
          >
            Find a part
          </button>
          {/* Other quick actions */}
          <button
            className="quick-action-btn"
            onClick={() => handleSend('Check my order status.')}
            disabled={loading}
          >
            Order status
          </button>
          <button
            className="quick-action-btn"
            onClick={handleInstallationHelp}
            disabled={loading}
          >
            Installation help
          </button>
          <button
            className="quick-action-btn"
            onClick={handleModelCompatibility}
            disabled={loading}
          >
            Model compatibility
          </button>
        </div>
        {/* Render messages, and insert category options bubble after the greeting if needed */}
        {messages.map((message, index) => (
          <React.Fragment key={index}>
            <div className={`${message.role}-message-container`}>
              <div className={`message ${message.role}-message`}>
                {renderMessageContent(message)}
              </div>
            </div>
            {/* Insert category options bubble after the greeting */}
            {showCategoryOptions && index === 0 && (
              <div className="assistant-message-container">
                <div className="message assistant-message">
                  <div style={{ marginBottom: 8 }}>Which category are you interested in?</div>
                  <button
                    className="quick-action-btn"
                    onClick={() => handleCategorySelect('Refrigerator')}
                    disabled={loading}
                    style={{ marginRight: 8 }}
                  >
                    Refrigerator
                  </button>
                  <button
                    className="quick-action-btn"
                    onClick={() => handleCategorySelect('Dishwasher')}
                    disabled={loading}
                  >
                    Dishwasher
                  </button>
                </div>
              </div>
            )}
          </React.Fragment>
        ))}
        {loading && (
          <div className="assistant-message-container">
            <div className="message assistant-message loading">Assistant is typing...</div>
          </div>
        )}
        {error && (
          <div className="assistant-message-container">
            <div className="message assistant-message error">{error}</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !loading && input.trim() !== "") {
              handleSend(input);
              setInput("");
              e.preventDefault();
            }
          }}
          disabled={loading}
        />
        <button
          className="send-button"
          onClick={() => {
            if (!loading && input.trim() !== "") {
              handleSend(input);
              setInput("");
            }
          }}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
