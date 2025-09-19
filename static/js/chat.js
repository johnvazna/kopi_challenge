const { createApp } = Vue;

createApp({
    data() {
        return {
            messages: [{
                id: 1,
                role: 'bot',
                content: 'Where should we start?',
                timestamp: new Date()
            }],
            inputMessage: '',
            currentConversationId: null,
            isLoading: false,
            conversationInfo: {},
            savedConversations: [],
            currentRequest: null
        }
    },
    
    mounted() {
        // Clear any old localStorage data to ensure fresh start
        this.clearOldStorageData();
        
        // Always start with a fresh conversation when opening the interface
        this.startNewConversation();
        this.scrollToBottom();
    },
    
    methods: {
        async sendMessage() {
            if (!this.inputMessage.trim() || this.isLoading) return;
            
            const userMessage = {
                id: Date.now(),
                role: 'user',
                content: this.inputMessage.trim(),
                timestamp: new Date()
            };
            
            this.messages.push(userMessage);
            this.inputMessage = '';
            this.isLoading = true;
            
            this.scrollToBottom();
            
            try {
                // Cancel any pending request
                if (this.currentRequest) {
                    this.currentRequest.abort();
                }
                
                // Create new request
                this.currentRequest = fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        conversation_id: this.currentConversationId,
                        message: userMessage.content
                    })
                });
                
                const response = await this.currentRequest;
                this.currentRequest = null;
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (!this.currentConversationId) {
                    this.currentConversationId = data.conversation_id;
                    this.conversationInfo = data;
                    this.saveConversationToStorage();
                }
                
                const botMessage = {
                    id: Date.now() + 1,
                    role: 'bot',
                    content: data.message[data.message.length - 1].message,
                    timestamp: new Date()
                };
                
                this.messages.push(botMessage);
                this.scrollToBottom();
                
            } catch (error) {
                console.error('Error:', error);
                const errorMessage = {
                    id: Date.now() + 1,
                    role: 'bot',
                    content: 'Sorry, I encountered an error. Please try again.',
                    timestamp: new Date()
                };
                this.messages.push(errorMessage);
            } finally {
                this.isLoading = false;
                this.currentRequest = null;
                this.scrollToBottom();
            }
        },
        
        handleEnter(event) {
            if (event.shiftKey) {
                return;
            }
            event.preventDefault();
            this.sendMessage();
        },
        
        autoResize() {
            const textarea = this.$refs.messageInput;
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
        },
        
        scrollToBottom() {
            this.$nextTick(() => {
                const chatArea = document.querySelector('.chat-area');
                if (chatArea) {
                    chatArea.scrollTop = chatArea.scrollHeight;
                }
            });
        },
        
        startNewConversation() {
            // Clear all current conversation data
            this.messages = [{
                id: 1,
                role: 'bot',
                content: 'Where should we start?',
                timestamp: new Date()
            }];
            this.currentConversationId = null;
            this.conversationInfo = {};
            this.inputMessage = '';
            this.isLoading = false;
            
            // Clear any pending requests
            if (this.currentRequest) {
                this.currentRequest.abort();
                this.currentRequest = null;
            }
            
            // Clean up old conversations to prevent memory buildup
            this.cleanupOldConversations();
            
            // Force scroll to bottom
            this.scrollToBottom();
            
            console.log('New conversation started - all data cleared');
        },
        
        saveConversationToStorage() {
            if (this.currentConversationId) {
                localStorage.setItem(`kopi_challenge_conversation_${this.currentConversationId}`, JSON.stringify({
                    id: this.currentConversationId,
                    messages: this.messages,
                    info: this.conversationInfo,
                    timestamp: new Date()
                }));
                
                const existingConversations = JSON.parse(localStorage.getItem('kopi_challenge_conversations') || '[]');
                const conversationExists = existingConversations.find(c => c.id === this.currentConversationId);
                
                if (!conversationExists) {
                    existingConversations.push({
                        id: this.currentConversationId,
                        title: this.messages[1]?.content.substring(0, 50) + '...' || 'New Chat',
                        timestamp: new Date()
                    });
                    localStorage.setItem('kopi_challenge_conversations', JSON.stringify(existingConversations));
                    this.savedConversations = existingConversations;
                }
            }
        },
        
        loadConversationFromStorage() {
            const savedConversations = JSON.parse(localStorage.getItem('kopi_challenge_conversations') || '[]');
            this.savedConversations = savedConversations;
            
            if (savedConversations.length > 0) {
                const lastConversation = savedConversations[savedConversations.length - 1];
                this.loadConversation(lastConversation.id);
            }
        },
        
        async loadConversation(conversationId) {
            try {
                const response = await fetch(`/chat/${conversationId}`);
                if (response.ok) {
                    const data = await response.json();
                    this.messages = data.message;
                    this.currentConversationId = conversationId;
                    this.conversationInfo = data;
                    this.scrollToBottom();
                } else {
                    this.loadConversationFromLocalStorage(conversationId);
                }
            } catch (error) {
                this.loadConversationFromLocalStorage(conversationId);
            }
        },
        
        loadConversationFromLocalStorage(conversationId) {
            const savedData = localStorage.getItem(`kopi_challenge_conversation_${conversationId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                this.messages = data.messages;
                this.currentConversationId = conversationId;
                this.conversationInfo = data.info;
                this.scrollToBottom();
            }
        },
        
        removeConversationFromStorage() {
            localStorage.removeItem('kopi_challenge_conversation_id');
        },

        formatMessage(content) {
            if (!content || typeof content !== 'string') {
                return '';
            }
            return content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
        },

        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        clearAllChats() {
            if (confirm('Are you sure you want to clear all chats? This action cannot be undone.')) {
                this.messages = [{
                    id: 1,
                    role: 'bot',
                    content: 'Where should we start?',
                    timestamp: new Date()
                }];
                this.currentConversationId = null;
                this.conversationInfo = {};
                this.savedConversations = [];
                
                localStorage.removeItem('kopi_challenge_conversations');
                const keys = Object.keys(localStorage);
                keys.forEach(key => {
                    if (key.startsWith('kopi_challenge_conversation_')) {
                        localStorage.removeItem(key);
                    }
                });
                
                this.scrollToBottom();
            }
        },
        
        cleanupOldConversations() {
            // Keep only the last 10 conversations to prevent memory buildup
            const maxConversations = 10;
            const savedConversations = JSON.parse(localStorage.getItem('kopi_challenge_conversations') || '[]');
            
            if (savedConversations.length > maxConversations) {
                // Remove oldest conversations
                const conversationsToRemove = savedConversations.slice(0, savedConversations.length - maxConversations);
                
                conversationsToRemove.forEach(conv => {
                    localStorage.removeItem(`kopi_challenge_conversation_${conv.id}`);
                });
                
                // Update the saved conversations list
                const remainingConversations = savedConversations.slice(-maxConversations);
                localStorage.setItem('kopi_challenge_conversations', JSON.stringify(remainingConversations));
                this.savedConversations = remainingConversations;
                
                console.log(`Cleaned up ${conversationsToRemove.length} old conversations`);
            }
        },
        
        clearOldStorageData() {
            // Clear all old conversation data to ensure fresh start
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('kopi_challenge_')) {
                    localStorage.removeItem(key);
                }
            });
            console.log('Cleared all old conversation data from localStorage');
        }
    }
}).mount('#app');
