// Global State
let isBeginnerMode = true;
let explanationMode = 'idle'; // 'idle', 'line', 'full'
let isChatboxExpanded = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    initializeLucideIcons();
    setupEventListeners();
    updateLineNumbers();
    initializeTheme();
    setupSmoothScroll();
});

// Initialize Lucide icons
function initializeLucideIcons() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Code editor actions
    document.getElementById('runCode').addEventListener('click', handleRunCode);
    document.getElementById('lineExplain').addEventListener('click', handleLineExplain);
    document.getElementById('fullExplain').addEventListener('click', handleFullExplain);
    document.getElementById('copyCode').addEventListener('click', handleCopyCode);
    document.getElementById('downloadCode').addEventListener('click', handleDownloadCode);

    // Explanation panel
    document.getElementById('toggleBeginnerMode').addEventListener('click', toggleBeginnerMode);

    // Code textarea
    const codeTextarea = document.getElementById('codeTextarea');
    codeTextarea.addEventListener('input', updateLineNumbers);
    codeTextarea.addEventListener('scroll', syncLineNumbersScroll);

    // AI Chatbox
    document.getElementById('chatboxHeader').addEventListener('click', toggleChatbox);
    document.getElementById('chatboxToggle').addEventListener('click', toggleChatbox);
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });

    // Console Input
    const consoleInput = document.getElementById('consoleInput');
    if (consoleInput) {
        consoleInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendConsoleInput();
            }
        });
    }

    // Close Console
    document.getElementById('closeConsole').addEventListener('click', () => {
        document.getElementById('consolePanel').style.display = 'none';
        if (socket) socket.close();
    });
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
    }
}

function toggleTheme() {
    const isDark = document.body.classList.contains('dark-mode');

    if (isDark) {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
        showToast('Switched to light mode', 'Theme updated successfully!');
    } else {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        showToast('Switched to dark mode', 'Theme updated successfully!');
    }
}

// Code Editor Functions
// ... Theme ... (unchanged)

let socket = null;

async function handleRunCode() {
    const code = document.getElementById('codeTextarea').value;
    const consolePanel = document.getElementById('consolePanel');
    const consoleOutput = document.getElementById('consoleOutput');
    const consoleInput = document.getElementById('consoleInput');

    // Reset and Show console
    consolePanel.style.display = 'flex'; // Changed to flex for layout
    consoleOutput.textContent = '';
    consoleInput.value = '';
    consoleInput.focus();

    // Close existing socket
    if (socket) {
        socket.close();
    }

    showToast('Connecting...', 'Establishing connection to server...');

    try {
        socket = new WebSocket('ws://localhost:8000/ws/run');

        socket.onopen = function () {
            socket.send(JSON.stringify({ code: code }));
            showToast('Running', 'Connected! Program starting...');
        };

        socket.onmessage = function (event) {
            consoleOutput.textContent += event.data;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        };

        socket.onclose = function () {
            consoleOutput.textContent += '\n\n[Disconnected]';
        };

        socket.onerror = function () {
            consoleOutput.textContent += '\n[Connection Error]';
        };

    } catch (e) {
        consoleOutput.textContent = 'Error connecting: ' + e.message;
    }
}

function sendConsoleInput() {
    const inputField = document.getElementById('consoleInput');
    const text = inputField.value;

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(text);
        // Echo input to console for better UX
        const consoleOutput = document.getElementById('consoleOutput');
        consoleOutput.textContent += text + '\n';
        inputField.value = '';
    } else {
        showToast('Error', 'Program is not running');
    }
}

// Explanation functions...

async function handleLineExplain() {
    explanationMode = 'line';
    updateExplanationPanel();

    const container = document.getElementById('lineExplanations');
    const code = document.getElementById('codeTextarea').value;
    const lines = code.split('\n');

    container.innerHTML = '<div style="padding: 20px; text-align: center;">Analyzing code with AI... <span class="loading-spinner">Analyzing...</span></div>';
    showToast('Analyzing', 'Getting line-by-line explanations...');

    let explanationsHtml = '';

    // Process unique non-empty lines to avoid too many requests
    // For a smoother demo, we'll explain non-empty lines

    try {
        for (let i = 0; i < lines.length; i++) {
            const lineContent = lines[i].trim();
            if (!lineContent || lineContent.startsWith('//')) continue;

            // Call backend for this line
            const response = await fetch('http://localhost:8000/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ line: lineContent })
            });

            const data = await response.json();

            // Only show if it returned a meaningful explanation (not default fallback)
            // But logic.py fallback is "I'm watching...", which we might display or filter.
            // Let's display everything for now.

            explanationsHtml += `
            <div class="line-explanation">
                <div class="line-explanation-header">
                    <span class="line-badge">Line ${i + 1}</span>
                    <code class="line-code">${lineContent.substring(0, 40)}${lineContent.length > 40 ? '...' : ''}</code>
                </div>
                <div class="line-explanation-content">
                    ${data.explanation}
                </div>
            </div>`;
        }

        if (explanationsHtml === '') {
            container.innerHTML = '<div style="padding: 20px; text-align: center;">No explainable code found. Write some C++!</div>';
        } else {
            container.innerHTML = explanationsHtml;
        }

    } catch (error) {
        container.innerHTML = `<div style="color: red; padding: 20px;">Error getting explanations: ${error.message}. Is the server running?</div>`;
    }
}

function handleFullExplain() {
    explanationMode = 'full';
    updateExplanationPanel();
    showToast('Full explanation activated', 'Generating comprehensive code analysis... (Note: Full explain static for demo)');
    // Keep static full explanation for this specific demo or upgrade to AI if needed later
}

function handleCopyCode() {
    const code = document.getElementById('codeTextarea').value;
    navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied!', 'Code has been copied to your clipboard.');
    });
}

function handleDownloadCode() {
    const code = document.getElementById('codeTextarea').value;
    const element = document.createElement('a');
    const file = new Blob([code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'code.cpp';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function updateLineNumbers() {
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    const lines = textarea.value.split('\n');

    lineNumbers.innerHTML = lines.map((_, index) =>
        `<div style="text-align: right; padding-right: 0.5rem; line-height: 1.5;">${index + 1}</div>`
    ).join('');
}

function syncLineNumbersScroll() {
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    lineNumbers.scrollTop = textarea.scrollTop;
}

// Explanation Panel Functions
function toggleBeginnerMode() {
    isBeginnerMode = !isBeginnerMode;
    updateBeginnerModeButton();
    // Re-fetch explanations if needed, or just toggle style
    updateExplanationPanel();

    const mode = isBeginnerMode ? 'beginner' : 'advanced';
    showToast(`Switched to ${mode} mode`, 'Explanations will adjust on next analysis!');
}

function updateBeginnerModeButton() {
    const button = document.getElementById('toggleBeginnerMode');
    const beginnerIcon = button.querySelector('.beginner-icon');
    const advancedIcon = button.querySelector('.advanced-icon');
    const modeText = button.querySelector('.mode-text');

    if (isBeginnerMode) {
        button.className = 'btn btn-accent btn-sm';
        beginnerIcon.style.display = 'block';
        advancedIcon.style.display = 'none';
        modeText.textContent = 'Beginner Mode';
    } else {
        button.className = 'btn btn-secondary btn-sm';
        beginnerIcon.style.display = 'none';
        advancedIcon.style.display = 'block';
        modeText.textContent = 'Advanced Mode';
    }
}

function updateExplanationPanel() {
    const title = document.getElementById('explanationTitle');
    const badge = document.getElementById('explanationBadge');
    const idleState = document.getElementById('explanationIdle');
    const lineExplanations = document.getElementById('lineExplanations');
    const fullExplanations = document.getElementById('fullExplanations');

    // Hide all content areas
    idleState.style.display = 'none';
    lineExplanations.style.display = 'none';
    fullExplanations.style.display = 'none';

    if (explanationMode === 'idle') {
        title.textContent = 'AI Explanations';
        badge.style.display = 'none';
        idleState.style.display = 'flex';
    } else if (explanationMode === 'line') {
        title.textContent = 'Line-by-Line Explanation';
        badge.textContent = 'Interactive';
        badge.style.display = 'inline-block';
        badge.className = 'explanation-badge';
        lineExplanations.style.display = 'block';
        // renderLineExplanations(); // No longer calling static render
    } else if (explanationMode === 'full') {
        title.textContent = 'Full Code Explanation';
        badge.textContent = 'Comprehensive';
        badge.style.display = 'inline-block';
        badge.className = 'explanation-badge';
        fullExplanations.style.display = 'block';
        renderFullExplanations();
    }
}

// renderLineExplanations REMOVED/REPLACED by logic inside handleLineExplain


function renderFullExplanations() {
    const container = document.getElementById('fullExplanations');

    const explanations = [
        {
            id: "overview",
            title: "What This Program Does",
            icon: "sparkles",
            content: isBeginnerMode
                ? "This C++ program calculates and prints the first 10 Fibonacci numbers. The Fibonacci sequence is famous in math and nature - each number is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34... You can see this pattern in sunflower seeds, pinecones, and even galaxies!"
                : "Implementation of the Fibonacci sequence using recursive algorithm with exponential time complexity O(2^n). Demonstrates basic C++ syntax, recursion, and I/O operations."
        },
        {
            id: "structure",
            title: "Program Structure",
            icon: "code",
            content: isBeginnerMode
                ? "Every C++ program has the same basic parts: 1) Include statements (like importing tools), 2) The 'main' function (where the program starts), and 3) Other functions we create. This program also has a 'fibonacci' function that we created to do the math calculations."
                : "Standard C++ program structure with preprocessor directives, namespace usage, function declarations, and the main entry point. Follows typical C++ organizational patterns."
        },
        {
            id: "algorithm",
            title: "How the Fibonacci Function Works",
            icon: "brain",
            content: isBeginnerMode
                ? "The fibonacci function is 'recursive' - it calls itself! Think of it like Russian nesting dolls. To find F(5), it needs F(4) and F(3). To find F(4), it needs F(3) and F(2), and so on, until it reaches F(0)=0 and F(1)=1. Then it builds the answer back up: F(2)=1, F(3)=2, F(4)=3, F(5)=5."
                : "Classic recursive approach with base cases (n ≤ 1) and recursive cases (fibonacci(n-1) + fibonacci(n-2)). Demonstrates divide-and-conquer paradigm with exponential time complexity."
        },
        {
            id: "improvements",
            title: "Making It Better",
            icon: "lightbulb",
            content: isBeginnerMode
                ? "This code is great for learning, but it's slow for big numbers because it recalculates the same values many times. Imagine asking 'What's 2+2?' a thousand times instead of remembering the answer! We could make it faster by storing previous answers or using a different approach."
                : "Consider memoization or dynamic programming to reduce time complexity from O(2^n) to O(n). Iterative approach would be more memory efficient. Could also add input validation and error handling for production code."
        }
    ];

    container.innerHTML = explanations.map(item => `
        <div class="full-explanation">
            <button class="full-explanation-trigger" onclick="toggleFullExplanation('${item.id}')">
                <div class="full-explanation-header">
                    <div class="full-explanation-title">
                        <i data-lucide="${item.icon}"></i>
                        ${item.title}
                    </div>
                    <i data-lucide="chevron-right" id="chevron-${item.id}"></i>
                </div>
            </button>
            <div class="full-explanation-content" id="content-${item.id}" style="display: none;">
                ${item.content}
            </div>
        </div>
    `).join('');

    // Re-initialize Lucide icons for the new content
    setTimeout(initializeLucideIcons, 0);
}

function toggleFullExplanation(id) {
    const content = document.getElementById(`content-${id}`);
    const chevron = document.getElementById(`chevron-${id}`);

    if (content.style.display === 'none') {
        content.style.display = 'block';
        chevron.setAttribute('data-lucide', 'chevron-down');
    } else {
        content.style.display = 'none';
        chevron.setAttribute('data-lucide', 'chevron-right');
    }

    // Re-initialize Lucide icons for the updated chevron
    setTimeout(initializeLucideIcons, 0);
}

// AI Chatbox Functions
function toggleChatbox() {
    const chatbox = document.getElementById('aiChatbox');
    const expandIcon = document.querySelector('.expand-icon');
    const collapseIcon = document.querySelector('.collapse-icon');

    isChatboxExpanded = !isChatboxExpanded;

    if (isChatboxExpanded) {
        chatbox.classList.remove('collapsed');
        expandIcon.style.display = 'none';
        collapseIcon.style.display = 'block';
    } else {
        chatbox.classList.add('collapsed');
        expandIcon.style.display = 'block';
        collapseIcon.style.display = 'none';
    }
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Simulate AI response
    setTimeout(() => {
        const responses = [
            "I can help explain that part of your C++ code! Which specific line would you like me to break down?",
            "That's a great question about the Fibonacci algorithm. The recursive approach you're using is elegant but has exponential time complexity.",
            "I notice your code uses recursion. Would you like me to explain how the function calls itself, or show you an iterative alternative?",
            "The iostream header you included gives you access to cout and cin for input/output operations. Would you like to know more about C++ headers?"
        ];

        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addChatMessage(randomResponse, 'ai');
    }, 1000);
}

function addChatMessage(message, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const avatarIcon = sender === 'ai' ? 'bot' : 'user';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i data-lucide="${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Re-initialize Lucide icons for the new message
    setTimeout(initializeLucideIcons, 0);
}

function handleQuickAction(action) {
    const actions = {
        'step-by-step': 'Can you explain my C++ code step by step?',
        'optimize': 'How can I optimize my Fibonacci code?',
        'find-errors': 'Are there any errors in my C++ code?'
    };

    const message = actions[action];
    if (message) {
        document.getElementById('chatInput').value = message;
        sendMessage();
    }
}

// Toast Notification System
function showToast(title, description) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';

    toast.innerHTML = `
        <div class="toast-header">${title}</div>
        <div class="toast-description">${description}</div>
    `;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Smooth scroll navigation
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });

    // Update active nav on scroll
    window.addEventListener('scroll', () => {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
}

// Initialize collapsed chatbox state
document.addEventListener('DOMContentLoaded', function () {
    const chatbox = document.getElementById('aiChatbox');
    chatbox.classList.add('collapsed');
});