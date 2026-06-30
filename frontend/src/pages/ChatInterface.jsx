import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Send, User, Bot, Sparkles, ChevronLeft, ArrowRight, ShieldAlert } from 'lucide-react';
import api from '../utils/api';

export default function ChatInterface() {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState([
    { role: 'model', content: "Hello! I'm your AI data assistant. I've analyzed your dataset and the machine learning model we just built. Ask me anything about the feature importance, model accuracy, or how to interpret the results!" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setError('');

    try {
      const response = await api.post(`/insights/${datasetId}/chat`, {
        message: userMessage,
        history: messages.map(m => ({ role: m.role, content: m.content }))
      });

      setMessages(prev => [...prev, { role: 'model', content: response.data.response }]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get a response from the AI. Please try again.');
      // Remove the user message if it failed, so they can try again? 
      // Actually better to just show the error.
    } finally {
      setIsLoading(false);
    }
  };

  const predefinedQuestions = [
    "What are the top 3 most important features driving this model?",
    "Explain the model's accuracy in simple business terms.",
    "Did we have any missing data issues?",
    "Write a python snippet to query the top predictions."
  ];

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 flex flex-col pt-16">
      {/* Header */}
      <header className="bg-white/80 dark:bg-dark-900/80 backdrop-blur-md border-b border-dark-200 dark:border-dark-800 sticky top-16 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate(`/ml/${datasetId}`)}
              className="p-2 hover:bg-dark-100 dark:hover:bg-dark-800 rounded-full text-dark-500 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-dark-900 dark:text-white leading-tight">AI Insights Engine</h1>
                <p className="text-xs text-dark-500">Powered by Gemini</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-fade-in`}>
            {/* Avatar */}
            <div className="shrink-0">
              {msg.role === 'user' ? (
                <div className="w-10 h-10 rounded-full bg-dark-200 dark:bg-dark-700 flex items-center justify-center">
                  <User className="w-5 h-5 text-dark-500 dark:text-dark-300" />
                </div>
              ) : (
                <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center shadow-md shadow-primary-500/20">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
            </div>

            {/* Bubble */}
            <div className={`max-w-[85%] rounded-2xl p-5 ${
              msg.role === 'user' 
                ? 'bg-primary-500 text-white rounded-tr-sm' 
                : 'glass-card rounded-tl-sm'
            }`}>
              {msg.role === 'user' ? (
                <p className="text-sm">{msg.content}</p>
              ) : (
                <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-dark-900 prose-pre:border prose-pre:border-dark-700">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-4 animate-fade-in">
            <div className="shrink-0">
              <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
                <Bot className="w-5 h-5 text-white animate-pulse" />
              </div>
            </div>
            <div className="glass-card rounded-2xl rounded-tl-sm p-5 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex items-center gap-2 p-4 text-sm text-accent-rose bg-accent-rose/10 border border-accent-rose/20 rounded-xl max-w-lg mx-auto">
            <ShieldAlert className="w-5 h-5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white/80 dark:bg-dark-900/80 backdrop-blur-md border-t border-dark-200 dark:border-dark-800 p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          
          {/* Suggestions */}
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2">
              {predefinedQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setInput(q)}
                  className="text-xs bg-dark-50 dark:bg-dark-800 hover:bg-dark-100 dark:hover:bg-dark-700 text-dark-600 dark:text-dark-300 px-3 py-1.5 rounded-full border border-dark-200 dark:border-dark-700 transition-colors flex items-center gap-1"
                >
                  {q} <ArrowRight className="w-3 h-3" />
                </button>
              ))}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your data, models, or feature importance..."
              disabled={isLoading}
              className="w-full bg-dark-50 dark:bg-dark-800 border border-dark-200 dark:border-dark-700 rounded-2xl py-4 pl-6 pr-16 text-dark-900 dark:text-white placeholder:text-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all shadow-sm"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-2 bottom-2 aspect-square rounded-xl gradient-primary flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-primary-500/20 transition-all"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="text-center text-[10px] text-dark-400 pb-2">
            AI can make mistakes. Consider verifying important metrics.
          </div>
        </div>
      </footer>
    </div>
  );
}
