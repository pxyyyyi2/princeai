const chatBox = document.getElementById("chatBox");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const btnIcon = document.getElementById("btnIcon");
const status = document.getElementById("status");
const typingIndicator = document.getElementById("typingIndicator");
const modelSelect = document.getElementById("modelSelect");
const voiceBtn = document.getElementById("voiceBtn");
const soundToggle = { checked: true };
const typingEffectToggle = { checked: true };

let chatHistory = [];
let isRecording = false;
let recognition = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded, initializing...');
  showWelcomeMessage();
  loadChatHistory();
  loadModels();
  initVoiceRecognition();
  input.focus();
  
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.body.setAttribute('data-theme', savedTheme);
  
  const savedModel = localStorage.getItem('selectedModel') || 'llama3';
});

// Show Welcome Message
function showWelcomeMessage() {
  const welcomeHTML = `
    <div class="welcome-message">
      <div class="welcome-icon">👋</div>
      <h2>Namaste!</h2>
      <p>Main Prince hoon 🚀</p>
      <p class="welcome-subtext">Koi bhi doubt ho ya help chahiye, bas puchlo!</p>
      <div class="quick-actions">
        <button class="quick-btn" onclick="quickMessage('Python kaise sikhu?')">
          <i class="fas fa-python"></i> Learn Python
        </button>
        <button class="quick-btn" onclick="quickMessage('Web development tips do')">
          <i class="fas fa-globe"></i> Web Dev
        </button>
        <button class="quick-btn" onclick="quickMessage('Git kaise use karte hai?')">
          <i class="fab fa-git-alt"></i> Git Help
        </button>
      </div>
    </div>
  `;
  
  if (chatHistory.length === 0) {
    chatBox.innerHTML = welcomeHTML;
  }
}

// Sound Effects
const sounds = {
  send: () => playSound(800, 0.1, 'sine'),
  receive: () => playSound(600, 0.1, 'sine'),
  error: () => playSound(400, 0.2, 'sawtooth'),
};

function playSound(frequency, duration, type) {
  if (!soundToggle.checked) return;
  
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = type;
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
  } catch (e) {
    console.log('Audio not supported');
  }
}

// Chat History Management
function loadChatHistory() {
  const saved = localStorage.getItem('chatHistory');
  if (saved) {
    try {
      chatHistory = JSON.parse(saved);
      if (chatHistory.length > 0) {
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
        
        chatHistory.forEach(msg => {
          addMessageToUI(msg.text, msg.sender, false);
        });
      }
    } catch (e) {
      console.error('Error loading chat history:', e);
      chatHistory = [];
    }
  }
}

function saveChatHistory() {
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

function addToHistory(text, sender) {
  chatHistory.push({ text, sender, timestamp: Date.now() });
  saveChatHistory();
}

// UI Functions
function addMessageToUI(text, sender, animate = true) {
  const welcomeMsg = document.querySelector('.welcome-message');
  if (welcomeMsg) welcomeMsg.remove();
  
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  
  if (animate && sender === 'bot' && typingEffectToggle.checked) {
    msg.style.opacity = '0';
    chatBox.appendChild(msg);
    typeWriter(msg, text, 0);
  } else {
    msg.innerText = text;
    chatBox.appendChild(msg);
  }
  
  chatBox.scrollTop = chatBox.scrollHeight;
}

function typeWriter(element, text, index) {
  if (index < text.length) {
    element.style.opacity = '1';
    element.innerText += text.charAt(index);
    chatBox.scrollTop = chatBox.scrollHeight;
    setTimeout(() => typeWriter(element, text, index + 1), 20);
  }
}

function setLoading(isLoading) {
  if (isLoading) {
    sendBtn.disabled = true;
    input.disabled = true;
    btnIcon.className = 'fas fa-spinner fa-spin';
  } else {
    sendBtn.disabled = false;
    input.disabled = false;
    btnIcon.className = 'fas fa-paper-plane';
  }
}

function updateStatus(online) {
  if (online) {
    status.innerHTML = '<i class="fas fa-circle"></i> Online';
  } else {
    status.innerHTML = '<i class="fas fa-circle"></i> Offline';
  }
}

function showTyping() {
  typingIndicator.style.display = 'flex';
  chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
  typingIndicator.style.display = 'none';
}

// Send Message with Streaming
async function sendMessage() {
  const userText = input.value.trim();
  if (!userText) return;

  addMessageToUI(userText, "user");
  addToHistory(userText, "user");
  input.value = "";
  
  sounds.send();
  setLoading(true);
  showTyping();

  try {
    const selectedModel = localStorage.getItem('selectedModel') || 'llama3';
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: userText,
        model: selectedModel 
      })
    });

    hideTyping();

    if (!response.ok) {
      throw new Error('Server error');
    }

    // Handle streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let botMessage = '';
    let messageElement = null;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.error) {
              throw new Error(data.error);
            }
            
            if (data.content) {
              botMessage += data.content;
              
              if (!messageElement) {
                messageElement = document.createElement("div");
                messageElement.classList.add("message", "bot");
                chatBox.appendChild(messageElement);
              }
              
              messageElement.innerText = botMessage;
              chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            if (data.done) {
              break;
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }
    }

    if (botMessage) {
      addToHistory(botMessage, "bot");
      sounds.receive();
      updateStatus(true);
    } else {
      throw new Error('Empty response');
    }

  } catch (err) {
    hideTyping();
    const errorMsg = "Bhai, kuch gadbad ho gayi 😭\n\nServer se connection nahi ho pa raha. Check kar:\n1. Internet connected hai?\n2. Server running hai?\n\nTry again after some time!";
    addMessageToUI(errorMsg, "bot");
    sounds.error();
    updateStatus(false);
    console.error("Error:", err);
  } finally {
    setLoading(false);
  }
}

// Quick Messages
function quickMessage(text) {
  input.value = text;
  sendMessage();
}

// Voice Recognition
function initVoiceRecognition() {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      input.value = transcript;
      isRecording = false;
      voiceBtn.classList.remove('recording');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      isRecording = false;
      voiceBtn.classList.remove('recording');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    };

    recognition.onend = () => {
      isRecording = false;
      voiceBtn.classList.remove('recording');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    };
  } else {
    voiceBtn.disabled = true;
    voiceBtn.title = 'Voice input not supported';
  }
}

function toggleVoice() {
  if (!recognition) return;

  if (isRecording) {
    recognition.stop();
    isRecording = false;
    voiceBtn.classList.remove('recording');
    voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
  } else {
    recognition.start();
    isRecording = true;
    voiceBtn.classList.add('recording');
    voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
  }
}

// Settings
function toggleSettings() {
  const panel = document.getElementById('settingsPanel');
  panel.classList.toggle('active');
}

function setTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.theme === theme) {
      btn.classList.add('active');
    }
  });
}

// Load Available Models
async function loadModels() {
  console.log('Using Groq models');
}

// Model Selection
modelSelect.addEventListener('change', () => {
  localStorage.setItem('selectedModel', modelSelect.value);
  sounds.receive();
});

// Clear Chat
function clearChat() {
  if (confirm('Bhai, sab chats delete karna hai? This cannot be undone!')) {
    chatHistory = [];
    localStorage.removeItem('chatHistory');
    showWelcomeMessage();
    sounds.receive();
  }
}

// Export Chat
function exportChat() {
  if (chatHistory.length === 0) {
    alert('Bhai, abhi koi chat nahi hai export karne ke liye!');
    return;
  }

  let exportText = '=== Prince AI Chat Export ===\n\n';
  chatHistory.forEach(msg => {
    const timestamp = new Date(msg.timestamp).toLocaleString();
    const sender = msg.sender === 'user' ? 'You' : 'Prince';
    exportText += `[${timestamp}] ${sender}:\n${msg.text}\n\n`;
  });

  const blob = new Blob([exportText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `prince-chat-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  
  sounds.receive();
}

// Enter key support
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !sendBtn.disabled) {
    sendMessage();
  }
});