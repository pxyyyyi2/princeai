const chatBox = document.getElementById("chatBox");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const btnIcon = document.getElementById("btnIcon");
const status = document.getElementById("status");
const typingIndicator = document.getElementById("typingIndicator");
const voiceBtn = document.getElementById("voiceBtn");
const soundToggle = { checked: true };
const typingEffectToggle = { checked: true };

let chatHistory = [];
let isRecording = false;
let recognition = null;
let isSpeakingEnabled = false;
let currentUtterance = null;
let userName = '';
const APP_VERSION = '2.0';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded, initializing...');
  
  const savedVersion = localStorage.getItem('appVersion');
  if (savedVersion !== APP_VERSION) {
    console.log('🔄 Version update detected! Clearing old data...');
    localStorage.clear();
    localStorage.setItem('appVersion', APP_VERSION);
  }
  
  userName = localStorage.getItem('userName');
  if (!userName) {
    showNamePopup();
  } else {
    initializeApp();
  }
  
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.body.setAttribute('data-theme', savedTheme);
  
  isSpeakingEnabled = localStorage.getItem('ttsEnabled') === 'true';
  updateSpeakerButton();
  
  if (speechSynthesis) {
    speechSynthesis.getVoices();
  }
});

// Show Name Popup
function showNamePopup(isFirstTime = false) {
  const popup = document.createElement('div');
  popup.className = 'name-popup-overlay';
  popup.innerHTML = `
    <div class="name-popup">
      <div class="popup-icon">👋</div>
      <h2>Welcome to Prince AI!</h2>
      <p>Apna naam batao!</p>
      <input 
        type="text" 
        id="nameInput" 
        placeholder="Your name..." 
        maxlength="20"
        autocomplete="off"
      />
      <button id="submitName" class="submit-name-btn">
        <i class="fas fa-arrow-right"></i> Let's Go!
      </button>
      <p class="privacy-note">Your name is stored locally on your device only</p>
    </div>
  `;
  
  document.body.appendChild(popup);
  
  setTimeout(() => {
    const nameInput = document.getElementById('nameInput');
    nameInput.focus();
    
    nameInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        submitName(isFirstTime);
      }
    });
  }, 100);
  
  document.getElementById('submitName').addEventListener('click', () => submitName(isFirstTime));
}

// Submit Name
function submitName(isFirstTime = false) {
  const nameInput = document.getElementById('nameInput');
  const name = nameInput.value.trim();
  
  if (!name) {
    nameInput.style.borderColor = '#ff1493';
    nameInput.placeholder = 'Please enter your name!';
    nameInput.focus();
    return;
  }
  
  userName = name;
  localStorage.setItem('userName', userName);
  
  const gender = detectGender(name);
  localStorage.setItem('userGender', gender);
  
  const popup = document.querySelector('.name-popup-overlay');
  const popupBox = document.querySelector('.name-popup');
  
  popupBox.style.transform = 'scale(0.9)';
  popupBox.style.opacity = '0';
  
  setTimeout(() => {
    popup.remove();
    initializeApp();
    
    // Show welcome banner for first time users
    if (isFirstTime) {
      setTimeout(() => {
        showFirstTimeWelcomeBanner();
      }, 500);
    }
    
    setTimeout(() => {
      if (isSpeakingEnabled) {
        const greeting = gender === 'female' ? `Namaste ${userName}! Main Prince hoon. Kaise help kar sakta hoon?` : `Namaste ${userName} bhai! Main Prince hoon. Kaise help kar sakta hoon?`;
        speakText(greeting);
      }
    }, 500);
  }, 300);
}

// Detect Gender from Name
function detectGender(name) {
  const nameLower = name.toLowerCase();
  
  const femaleEndings = ['a', 'i', 'ya', 'ka', 'sha', 'na', 'ta', 'la', 'ra'];
  
  const femaleNames = [
    'priya', 'riya', 'diya', 'ananya', 'isha', 'neha', 'pooja', 'shreya',
    'kavya', 'divya', 'sneha', 'sakshi', 'nisha', 'tanvi', 'simran', 'ritika',
    'anjali', 'megha', 'swati', 'jyoti', 'preeti', 'sonal', 'shweta', 'komal',
    'ayesha', 'fatima', 'sana', 'zara', 'alisha', 'sophia', 'emily', 'sarah',
    'jessica', 'maria', 'anna', 'lisa', 'karen', 'nancy', 'linda', 'susan'
  ];
  
  if (femaleNames.some(fn => nameLower.includes(fn))) {
    return 'female';
  }
  
  if (femaleEndings.some(ending => nameLower.endsWith(ending) && nameLower.length > 3)) {
    return 'female';
  }
  
  return 'male';
}

// Initialize App
function initializeApp() {
  showWelcomeMessage();
  loadChatHistory();
  initVoiceRecognition();
  input.focus();
}

// Show Welcome Message
function showWelcomeMessage() {
  const welcomeHTML = `
    <div class="welcome-message">
      <div class="welcome-icon">👋</div>
      <h2>Namaste${userName ? ' ' + userName : ''}!</h2>
      <p>Main Prince hoon 🚀</p>
      <p class="welcome-subtext">Koi bhi doubt ho ya help chahiye, bas puchlo!</p>
      <div class="quick-actions">
        <button class="quick-btn" onclick="quickMessage('Python kaise sikhu?')">
          <i class="fas fa-code"></i> Learn Python
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

// Text-to-Speech
function speakText(text) {
  if (!isSpeakingEnabled) return;
  
  if (currentUtterance) {
    speechSynthesis.cancel();
  }
  
  const cleanText = text.replace(/[😊😄🔥💯🚀💡✨👍🎉❤️😭😅🤔]/g, '').trim();
  
  if (!cleanText) return;
  
  const utterance = new SpeechSynthesisUtterance(cleanText);
  currentUtterance = utterance;
  
  let voices = speechSynthesis.getVoices();
  
  if (voices.length === 0) {
    speechSynthesis.onvoiceschanged = () => {
      voices = speechSynthesis.getVoices();
      setVoiceAndSpeak(utterance, voices);
    };
  } else {
    setVoiceAndSpeak(utterance, voices);
  }
}

function setVoiceAndSpeak(utterance, voices) {
  let selectedVoice = null;

  selectedVoice = voices.find(voice =>
    voice.lang === 'hi-IN' &&
    (
      voice.name.toLowerCase().includes('male') ||
      voice.name.toLowerCase().includes('ravi') ||
      voice.name.toLowerCase().includes('india')
    )
  );

  if (!selectedVoice) {
    selectedVoice = voices.find(voice =>
      voice.lang.startsWith('en') &&
      !voice.name.toLowerCase().includes('female')
    );
  }

  if (!selectedVoice && voices.length > 0) {
    selectedVoice = voices[0];
  }

  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  utterance.lang = 'hi-IN';
  utterance.rate = 1.0;
  utterance.pitch = 0.85;
  utterance.volume = 1.0;

  utterance.onend = () => currentUtterance = null;

  speechSynthesis.speak(utterance);
}

// Toggle TTS
function toggleSpeaking() {
  isSpeakingEnabled = !isSpeakingEnabled;
  localStorage.setItem('ttsEnabled', isSpeakingEnabled);
  updateSpeakerButton();
  sounds.receive();
  
  if (isSpeakingEnabled) {
    speakText("Voice mode on!");
  } else {
    speechSynthesis.cancel();
  }
}

// Update Speaker Button
function updateSpeakerButton() {
  const speakerBtn = document.getElementById('speakerBtn');
  if (speakerBtn) {
    if (isSpeakingEnabled) {
      speakerBtn.classList.add('active');
      speakerBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
      speakerBtn.title = 'Voice ON';
    } else {
      speakerBtn.classList.remove('active');
      speakerBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
      speakerBtn.title = 'Voice OFF';
    }
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

// Chat History
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

// Send Message
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
    const userName = localStorage.getItem('userName') || 'anonymous';
    const userGender = localStorage.getItem('userGender') || 'male';
    
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: userText,
        user_id: userName,
        user_gender: userGender
      })
    });

    hideTyping();

    if (!response.ok) {
      throw new Error('Server error');
    }

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
      
      setTimeout(() => speakText(botMessage), 100);
    } else {
      throw new Error('Empty response');
    }

  } catch (err) {
    hideTyping();
    const errorMsg = "Sorry yaar, kuch problem ho gayi 😔\n\nServer se connection nahi ho pa raha. Try again!";
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

// Clear Chat
function clearChat() {
  if (confirm('Sab chats delete karna hai? This cannot be undone!')) {
    chatHistory = [];
    localStorage.removeItem('chatHistory');
    showWelcomeMessage();
    sounds.receive();
  }
}

// Export Chat
function exportChat() {
  if (chatHistory.length === 0) {
    alert('Abhi koi chat nahi hai export karne ke liye!');
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

// Theme Toggle Function
function toggleTheme() {
  const currentTheme = document.body.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  document.body.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Update theme button icon
  const themeBtn = document.getElementById('themeBtn');
  if (themeBtn) {
    themeBtn.innerHTML = newTheme === 'dark' 
      ? '<i class="fas fa-sun"></i>' 
      : '<i class="fas fa-moon"></i>';
    themeBtn.title = newTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  }
  
  sounds.receive();
}

// Load saved theme on startup
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.body.setAttribute('data-theme', savedTheme);
  
  const themeBtn = document.getElementById('themeBtn');
  if (themeBtn) {
    themeBtn.innerHTML = savedTheme === 'dark' 
      ? '<i class="fas fa-sun"></i>' 
      : '<i class="fas fa-moon"></i>';
    themeBtn.title = savedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  }
});

// Preload voices
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => {
    const voices = speechSynthesis.getVoices();
    console.log('✅ Voices loaded:', voices.length);
  };
}