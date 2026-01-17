import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const AI: React.FC = () => {
  const { t, language } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: t('ai.welcome'),
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Update welcome message when language changes
  useEffect(() => {
    setMessages(prev => {
      if (prev.length === 1 && prev[0].role === 'assistant') {
        return [{
          role: 'assistant',
          content: t('ai.welcome'),
          timestamp: new Date().toLocaleTimeString()
        }];
      }
      return prev;
    });
  }, [language, t]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: userMsg.content,
            history: messages // Send full history
        })
      });

      if (!response.ok) throw new Error(response.statusText);

      // Create a placeholder for the assistant's response
      const botMsg: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMsg]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            
            try {
                // Parse JSON chunk {content: "..."}
                const parsed = JSON.parse(data);
                if (parsed.content) {
                    accumulatedContent += parsed.content;
                    
                    setMessages(prev => {
                      const newMsgs = [...prev];
                      newMsgs[newMsgs.length - 1] = {
                        ...newMsgs[newMsgs.length - 1],
                        content: accumulatedContent
                      };
                      return newMsgs;
                    });
                }
            } catch (e) {
                // Backward compatibility or raw text
                console.warn("Failed to parse chunk", e);
            }
          }
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: t('ai.error'),
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (content: string) => {
    // Check for JSON block
    const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/);
    
    if (jsonMatch) {
      try {
        const data = JSON.parse(jsonMatch[1]);
        const { recommendations, analysis } = data;
        
        return (
          <div className="space-y-4">
             {/* Analysis Text */}
            <div className="whitespace-pre-wrap">{analysis || content.replace(jsonMatch[0], '')}</div>
            
            {/* Stock Cards */}
            {recommendations && recommendations.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                {recommendations.map((stock: any, idx: number) => (
                  <div key={idx} className="bg-white border border-gray-200 p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="font-bold text-gray-800">{stock.code}</span>
                        {stock.name && <span className="ml-2 text-sm text-gray-500">{stock.name}</span>}
                      </div>
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                        {stock.strategy}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2" title={stock.reason}>
                      {stock.reason}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      } catch (e) {
        // Fallback if JSON parse fails
        return <div className="whitespace-pre-wrap">{content}</div>;
      }
    }
    
    return <div className="whitespace-pre-wrap">{content}</div>;
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-purple-600" />
        <h2 className="font-semibold text-gray-800">{t('ai.title')}</h2>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-blue-100' : 'bg-purple-100'}`}>
              {msg.role === 'user' ? <User className="w-5 h-5 text-blue-600" /> : <Bot className="w-5 h-5 text-purple-600" />}
            </div>
            
            <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} w-full`}>
              <div 
                className={`p-3 rounded-lg text-sm w-full ${ 
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-none' 
                    : 'bg-gray-100 text-gray-800 rounded-tl-none'
                }`}
              >
                {renderMessageContent(msg.content)}
              </div>
              <span className="text-xs text-gray-400 mt-1">{msg.timestamp}</span>
            </div>
          </div>
        ))}
        {isLoading && (
            <div className="flex gap-3 max-w-[80%]">
                 <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-100">
                    <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
                 </div>
                 <div className="flex items-center">
                    <span className="text-xs text-gray-400">{t('ai.thinking')}</span>
                 </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('ai.placeholder')}
            className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 shadow-sm"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-2 p-1.5 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default AI;