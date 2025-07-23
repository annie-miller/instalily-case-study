
export const getAIMessage = async (userInput, history = []) => {
  // Compose the message history for the backend
  const messages = [
    ...history,
    { role: "user", content: userInput }
  ];

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ messages })
    });
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    // If the backend returns a product or products, pass them through
    if (data.product) {
      return {
        role: "assistant",
        content: data.content,
        product: data.product
      };
    }
    if (data.products) {
      // For multiple products, just show the first for now (can be improved)
      return {
        role: "assistant",
        content: data.content,
        product: data.products[0]
      };
    }
    return {
      role: "assistant",
      content: data.content
    };
  } catch (error) {
    return {
      role: "assistant",
      content: "Sorry, I couldn't connect to the assistant. Please try again later."
    };
  }
};
