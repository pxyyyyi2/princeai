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




// Add to script.js - After APP_VERSION constant

// Add to script.js - After APP_VERSION constant

const APP_VERSION = '3.2'; // Change this to trigger banner for all users

// Initialize - Update this section
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded, initializing...');
  
  const savedVersion = localStorage.getItem('appVersion');
  const hasSeenUpdateBanner = localStorage.getItem('hasSeenUpdateBanner_' + APP_VERSION);
  
  // Show update banner if version changed OR never seen this version's banner
  if (savedVersion !== APP_VERSION || !hasSeenUpdateBanner) {
    showFullScreenUpdateBanner();
    localStorage.setItem('appVersion', APP_VERSION);
  }
  
  userName = localStorage.getItem('userName');
  if (!userName) {
    // Don't show name popup if update banner is showing
    if (!hasSeenUpdateBanner && savedVersion) {
      // User exists but needs to see update banner first
    } else {
      showNamePopup(true);
    }
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

// Show Full-Screen Update Banner
function showFullScreenUpdateBanner() {
  const banner = document.createElement('div');
  banner.className = 'fullscreen-update-overlay';
  banner.innerHTML = `
    <div class="fullscreen-update-container">
      <!-- Animated Background -->
      <div class="update-bg-shapes">
        <div class="update-shape update-shape-1"></div>
        <div class="update-shape update-shape-2"></div>
        <div class="update-shape update-shape-3"></div>
      </div>
      
      <!-- Content -->
      <div class="update-content">
        <!-- Icon -->
        <div class="update-icon-container">
          <div class="update-icon-glow"></div>
          <div class="update-icon">🎉</div>
        </div>
        
        <!-- Title -->
        <h1 class="update-title">Prince AI v${APP_VERSION}</h1>
        <p class="update-subtitle"> 🔥</p>
        
        <!-- Features Grid -->
        <div class="update-features">
          <div class="update-feature">
            <div class="feature-icon">⚡</div>
            <div class="feature-text">
              <h3>Super Fast</h3>
              <p>Lightning-speed responses!</p>
            </div>
          </div>
          
          <div class="update-feature">
            <div class="feature-icon">🎭</div>
            <div class="feature-text">
              <h3>New Preminum Themes</h3>
              <p>Select preminum themes </p>
            </div>
          </div>
          
          <div class="update-feature">
            <div class="feature-icon">🎙️</div>
            <div class="feature-text">
              <h3>Voice Power</h3>
              <p>Speak & hear answers!</p>
            </div>
          </div>
          
          <div class="update-feature">
            <div class="feature-icon">🎯</div>
            <div class="feature-text">
              <h3>Gender Smart</h3>
              <p>Respects everyone!</p>
            </div>
          </div>
          
          <div class="update-feature">
            <div class="feature-icon">💎</div>
            <div class="feature-text">
              <h3>Premium Design</h3>
              <p>Beautiful new Exclusive themes!</p>
            </div>
          </div>
          
          <div class="update-feature">
            <div class="feature-icon">🚀</div>
            <div class="feature-text">
              <h3>Fastest AI</h3>
              <p>Powered by Groq!</p>
            </div>
          </div>
        </div>
        
        <!-- CTA -->
        <button class="update-cta" onclick="closeFullScreenUpdateBanner()">
          <span>Let's Go!</span>
          <i class="fas fa-arrow-right"></i>
        </button>
        
        <!-- Footer -->
        <p class="update-footer">Made with ❤️ by Prince</p>
      </div>
    </div>
  `;
  
  document.body.appendChild(banner);
  
  // Animate in
  setTimeout(() => {
    banner.classList.add('show');
  }, 100);
  
  // Play sound
  sounds.receive();
}

// Close Full-Screen Update Banner
function closeFullScreenUpdateBanner() {
  const banner = document.querySelector('.fullscreen-update-overlay');
  if (!banner) return;
  
  // Mark as seen
  localStorage.setItem('hasSeenUpdateBanner_' + APP_VERSION, 'true');
  
  // Animate out
  banner.classList.remove('show');
  banner.classList.add('hide');
  
  setTimeout(() => {
    banner.remove();
    
    // Check if user needs to enter name
    const userName = localStorage.getItem('userName');
    if (!userName) {
      showNamePopup(true);
    }
  }, 500);
  
  sounds.send();
}

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

// Show First Time Welcome Banner
function showFirstTimeWelcomeBanner() {
  const banner = document.createElement('div');
  banner.className = 'update-banner';
  banner.innerHTML = `
    <div class="update-banner-icon">🎉</div>
    <div class="update-banner-text">
      Welcome to Prince AI v${APP_VERSION}! Ready to help you! 🚀
    </div>
    <button class="update-banner-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  document.body.appendChild(banner);
  
  setTimeout(() => {
    banner.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    banner.classList.remove('show');
    setTimeout(() => banner.remove(), 500);
  }, 5000);
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
        const greeting = gender === 'female' ? `Heyy😺 ${userName}! Main Prince hoon. Kaise help kar sakta hoon?` : `Namaste ${userName} bhai! Main Prince hoon. Kaise help kar sakta hoon?`;
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
      <h2>Heyy😺${userName ? ' ' + userName : ''}!</h2>
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
function showThemePicker() {
  document.getElementById('themePicker').style.display = 'flex';
  updateActiveTheme();
  sounds.receive();
}

function closeThemePicker() {
  document.getElementById('themePicker').style.display = 'none';
  sounds.send();
}

function changeTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  updateActiveTheme();
  sounds.receive();
}

function updateActiveTheme() {
  const currentTheme = localStorage.getItem('theme') || 'pink-light';
  document.querySelectorAll('.theme-card').forEach(card => {
    card.classList.remove('active');
    if (card.getAttribute('data-theme') === currentTheme) {
      card.classList.add('active');
    }
  });
}

// Close theme picker when clicking outside
document.addEventListener('click', (e) => {
  const themePicker = document.getElementById('themePicker');
  if (e.target === themePicker) {
    closeThemePicker();
  }
});

// Load saved theme on startup
// Load saved theme on startup
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'pink-light';
  document.body.setAttribute('data-theme', savedTheme);
});
// Preload voices
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => {
    const voices = speechSynthesis.getVoices();
    console.log('✅ Voices loaded:', voices.length);
  };
}