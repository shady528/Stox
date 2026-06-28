import React from "react";
import BotResponse from "./BotResponse";
import "./IntroSection.css";

const IntroSection = () => {
  return (
    <div id="introsection" className="intro-section">
      <h1 className="heading" style={{ fontFamily: 'Anta, sans-serif', fontSize: '2.5rem', fontWeight: 'bold', color: '#333' }}>
        StockBot
        <BotResponse response=" - Your AI Financial Assistant" />
      </h1>
      <h2 className="subtitle" style={{ fontFamily: 'Anta, sans-serif', fontSize: '1.3rem', color: '#666' }}>
        Your personal AI-powered stock market assistant built on RAG architecture.
        Ask anything about stocks, earnings, financials, and market trends — powered
        by the LLM of your choice.
      </h2>
      <h3 style={{ fontFamily: 'Anta, sans-serif', fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>Features:</h3>
      <ul style={{ fontFamily: 'Anta, sans-serif', fontSize: '1.3rem', color: '#666' }}>
        <li>Choose your LLM — Google Gemini, Anthropic Claude, or OpenAI GPT</li>
        <li>Bring your own API key — switch providers anytime</li>
        <li>RAG-powered answers from real financial documents</li>
        <li>Conversation memory across follow-up questions</li>
        <li>Suggested follow-up questions with every answer</li>
      </ul>
      <p style={{ fontFamily: 'Anta, sans-serif', fontSize: '1.3rem', color: '#666' }}>
        Click the <strong>gear icon</strong> in the header to configure your preferred
        LLM provider, or start chatting right away with the default model.
      </p>
      <p style={{ fontFamily: 'Anta, sans-serif', fontSize: '1rem', color: '#999', marginTop: '24px' }}>
        Built by{' '}
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://www.linkedin.com/in/anurag-b94478204/"
          style={{ color: '#0077b5', textDecoration: 'none', fontWeight: 600 }}
        >
          Anurag
        </a>
      </p>
    </div>
  );
};

export default IntroSection;
