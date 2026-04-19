import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Leaf, Send, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import './index.css';

function App() {
    const [messages, setMessages] = useState([
        { text: "Hello! I'm your agricultural assistant. Ask me about crops, fertilizers, or government schemes.", sender: 'bot', lang: 'en' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);

    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialize Speech Recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;

            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                // Automatically send after voice input
                handleSendVoice(transcript);
            };

            recognitionRef.current.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setIsRecording(false);
            };

            recognitionRef.current.onend = () => {
                setIsRecording(false);
            };
        } else {
            console.warn("Speech Recognition API not supported in this browser.");
        }
    }, []);

    const toggleRecording = () => {
        if (isRecording) {
            recognitionRef.current?.stop();
        } else {
            try {
                recognitionRef.current?.start();
                setIsRecording(true);
            } catch (e) {
                console.error("Could not start recording", e);
            }
        }
    };

    const speakText = (text, langCode) => {
        if (!isVoiceEnabled || !('speechSynthesis' in window)) return;

        // Map backend language codes to browser locales
        const localeMap = {
            'en': 'en-IN',
            'ta': 'ta-IN',
            'hi': 'hi-IN',
            'te': 'te-IN',
            'kn': 'kn-IN'
        };

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = localeMap[langCode] || 'en-US';

        // Cancel any ongoing speech before starting a new one
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    };

    const processResponse = async (userText) => {
        setIsLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/chat', {
                message: userText
            });

            const botMessage = {
                text: response.data.response,
                sender: 'bot',
                lang: response.data.language
            };
            setMessages(prev => [...prev, botMessage]);

            // Speak the response if enabled
            speakText(botMessage.text, botMessage.lang);

        } catch (error) {
            console.error("Error communicating with backend:", error);
            const errorMessage = {
                text: "Sorry, I'm having trouble connecting to the server. Please ensure the backend is running.",
                sender: 'bot',
                lang: 'en'
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSend = () => {
        if (!input.trim()) return;
        const userMessage = { text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        const textToSend = input;
        setInput('');
        processResponse(textToSend);
    };

    const handleSendVoice = (transcript) => {
        const userMessage = { text: transcript, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        processResponse(transcript);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const toggleVoice = () => {
        setIsVoiceEnabled(!isVoiceEnabled);
        if (isVoiceEnabled) {
            window.speechSynthesis.cancel();
        }
    };

    return (
        <div className="app-container">
            <header className="header">
                <Leaf size={24} />
                <span>AgriChatbot</span>
                <button
                    onClick={toggleVoice}
                    className="voice-toggle-btn"
                    title={isVoiceEnabled ? "Mute Voice Responses" : "Enable Voice Responses"}
                >
                    {isVoiceEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                </button>
            </header>

            <div className="chat-window">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}
                    >
                        {msg.text}
                    </div>
                ))}
                {isLoading && (
                    <div className="message bot-message">
                        <span className="loading-dots">Thinking</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
                <button
                    className={`mic-btn ${isRecording ? 'recording' : ''}`}
                    onClick={toggleRecording}
                    disabled={isLoading}
                    title={isRecording ? "Stop Recording" : "Start Voice Input"}
                >
                    {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                </button>

                <input
                    type="text"
                    className="input-field"
                    placeholder="Type or speak your query..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    disabled={isLoading || isRecording}
                    autoCorrect="on"
                    spellCheck="true"
                    autoComplete="on"
                />
                <button
                    className="send-btn"
                    onClick={handleSend}
                    disabled={isLoading || !input.trim() || isRecording}
                >
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
}

export default App;
