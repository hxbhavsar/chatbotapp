import streamlit as st
from datetime import datetime
from rapidfuzz import process
import re

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ''

if 'human_agent' not in st.session_state:
    st.session_state['human_agent'] = False

if 'reset_password' not in st.session_state:
    st.session_state['reset_password'] = False

if 'registering' not in st.session_state:
    st.session_state['registering'] = False

# Dummy user database
USER_DB = {
    'user@example.com': 'hb123'
}

# Extended FAQ responses
FAQ_RESPONSES = {
    'What are your hours of operation?': 'Our hours of operation are 9 AM to 5 PM, Monday to Friday.',
    'Where are you located?': 'We are located at 1234 Main St, Anytown, USA.',
    'How can I reset my password?': 'To reset your password, click on "Forgot Password" on the login page and follow the instructions.',
    'What is your return policy?': 'You can return any item within 30 days of purchase for a full refund. Please keep the receipt.',
    'Do you offer technical support?': 'Yes, we offer 24/7 technical support. Please call our support hotline at 1-800-123-4567.',
    'Can I track my order?': 'Yes, you can track your order using the tracking number provided in the confirmation email.',
    'How do I update my billing information?': 'You can update your billing information in your account settings under "Billing".',
    'What payment methods do you accept?': 'We accept all major credit cards, PayPal, and Apple Pay.',
    'How do I contact customer service?': 'You can contact customer service via email at support@example.com or by calling 1-800-123-4567.'
}

# Predefined human agent responses
HUMAN_AGENT_RESPONSES = {
    'password reset': 'Sure, I can help you with resetting your password. Please provide your registered email address.',
    'order status': 'I can check the status of your order. Can you please provide your order number?',
    'technical issue': 'I am here to assist you with technical issues. Can you please describe the problem you are facing?',
    'billing issue': 'I can help you with billing issues. Please provide details of the problem.',
    'return policy': 'Our return policy allows you to return items within 30 days of purchase. Do you have any specific questions about returns?'
}

# Function to display chat messages
def display_chat():
    for message in st.session_state['chat_history']:
        user, text, timestamp = message
        st.write(f"**{user}** [{timestamp}]: {text}")

# Function to handle user message
def handle_user_message():
    user_message = st.session_state['user_message']
    if user_message:
        st.session_state['chat_history'].append(('User', user_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        st.session_state['user_message'] = ''
        if st.session_state['human_agent']:
            respond_as_human_agent(user_message)
        else:
            respond_to_user(user_message)

# Function to simulate bot response with fuzzy matching
def respond_to_user(user_message):
    key_phrases = {
        "reset password": "How can I reset my password?",
        "password": "How can I reset my password?",
        "return policy": "What is your return policy?",
        "technical support": "Do you offer technical support?",
        "track my order": "Can I track my order?",
        "update billing": "How do I update my billing information?",
        "contact customer service": "How do I contact customer service?"
    }

    for phrase, question in key_phrases.items():
        if phrase in user_message.lower():
            response = FAQ_RESPONSES[question]
            st.session_state['chat_history'].append(('Bot', response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return

    match = process.extractOne(user_message, FAQ_RESPONSES.keys(), score_cutoff=60)
    if match:
        best_match, score, _ = match
        response = FAQ_RESPONSES[best_match]
    else:
        response = "I'm sorry, I don't have an answer to that. Do you want to speak to a human agent?"
    st.session_state['chat_history'].append(('Bot', response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Function to simulate human agent response
def respond_as_human_agent(user_message):
    if st.session_state['reset_password']:
        email = user_message
        if email in USER_DB:
            new_password = 'newpassword123'  # Simulate password reset
            USER_DB[email] = new_password
            response = f"Your password has been reset. Your new password is '{new_password}'. Please change it after logging in."
        else:
            response = "The email address provided is not registered with us. Please provide a valid email address."
        st.session_state['reset_password'] = False
    else:
        match = process.extractOne(user_message, HUMAN_AGENT_RESPONSES.keys(), score_cutoff=60)
        if match:
            best_match, score, _ = match
            response = HUMAN_AGENT_RESPONSES[best_match]
            if best_match == 'password reset':
                st.session_state['reset_password'] = True
        else:
            response = "I'm here to help! Can you please provide more details?"
    st.session_state['chat_history'].append(('Human Agent', response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Function to authenticate user
def authenticate_user():
    email = st.session_state['email']
    password = st.session_state['password']
    if USER_DB.get(email) == password:
        st.session_state['authenticated'] = True
        st.session_state['user_email'] = email
        st.session_state['chat_history'].append(('Bot', "Welcome! How can I assist you today?", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        st.error("Authentication failed. Please check your email and password.")

# Function to register a new user
def register_user():
    email = st.session_state['email']
    password = st.session_state['password']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("Invalid email address")
        return
    if email in USER_DB:
        st.error("Email already registered. Please use a different email or login.")
        return
    if len(password) < 6:
        st.error("Password must be at least 6 characters long.")
        return
    USER_DB[email] = password
    st.success("Registration successful! Please log in.")
    st.session_state['registering'] = False

# Function to request human assistance
def request_human_assistance():
    st.session_state['chat_history'].append(('User', "I want to speak to a human agent.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    st.session_state['chat_history'].append(('Bot', "A human agent will be with you shortly.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    st.session_state['human_agent'] = True

# JavaScript code for Enter key detection
st.markdown("""
    <script>
    const textarea = document.querySelector('textarea');
    textarea.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.querySelector('button[aria-label="send_button"]').click();
        }
    });
    </script>
""", unsafe_allow_html=True)

# User authentication form
if not st.session_state['authenticated']:
    st.title("Customer Support Chat")
    if st.session_state['registering']:
        st.text_input("Email:", key='email')
        st.text_input("Password:", key='password', type='password')
        if st.button("Register", key='register_button', on_click=register_user):
            pass
        if st.button("Back to Login", key='back_to_login_button', on_click=lambda: st.session_state.update(registering=False)):
            pass
    else:
        st.text_input("Email:", key='email')
        st.text_input("Password:", key='password', type='password')
        if st.button("Login", key='login_button', on_click=authenticate_user):
            pass
        if st.button("Register", key='register_button', on_click=lambda: st.session_state.update(registering=True)):
            pass
else:
    st.title("Customer Support Chat")
    display_chat()

    # User input
    st.text_area("You:", key='user_message', placeholder='Type your message and press Enter to send')
    if st.button("Send", key='send_button', on_click=handle_user_message):
        pass

   # Option to request human assistance
    if st.button("Request Human Assistance", key='human_assistance_button', on_click=request_human_assistance):
        pass
