from django.shortcuts import render
from django.http import JsonResponse
from transformers import pipeline
import spacy
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Load Hugging Face QA pipeline
qa_pipeline = pipeline("question-answering")

# Predefined Responses
MIND2I_RESPONSES = {
    "hi": "Hello! How can I assist you today? 😊",
    "hello": "Hi there! How can I help you? 👋",
    "bye": "Goodbye! Have a great day! 😊",
    "thanks": "You're welcome! Let me know if you need anything else. 😊",
    "thank you": "You're welcome! Feel free to ask anything else. 😊",
    "services": "Mind2i offers services like Python Full stack Program, Data Science, Data Analytics, and Data Engineering.",
    "python": "This course covers both front-end and back-end development skills, including HTML, CSS, JavaScript, and server-side scripting, with over 20 hands-on projects.",
    "data science": "Covers a broad range of topics, including statistical analysis, machine learning, and data visualization.",
    "data analytics": "Focused on data analysis techniques and tools to derive insights from data.",
    "data engineering": "Emphasizes the design and management of data systems and pipelines.",
    "location": "Mind2i is headquartered in Bengaluru, India. For more details, visit our 'Contact Us' page.",
    "contact": "You can contact Mind2i via email at info@mind2i.com or call us at +91-9606561789.",
    "internship & certifications": "Hands-on training and industry-recognized certificates.",
    "job assistance": "We offer resume building, interview preparation, and placement support.",
    "eligibility & admission process": "Who are interested in the software industry are eligible and we guide applicants on prerequisites and the admission process.",
    "fees & payment options":"Flexible payment plans and EMI options are available.",
    "international presence":"Mind2i, headquartered in Bangalore, India, has a global presence with outreach in the UK, Ireland, Denmark, and the UAE.",
    "resume building": "We help craft ATS-friendly resumes to boost job opportunities.",
    "interview preparation": "Mock interviews and guidance from industry experts.",
    "duration": "The duration of these internships varies based on the program, with short-term internships lasting between 1 to 3 months and long-term internships extending up to 6 months.",
    "certification": "The certification process involves enrollment in the program, completion of assignments and projects, attending mentorship sessions, and a final evaluation. Upon successfully completing the program, candidates receive an industry-recognized certification from Mind2i, enhancing their career prospects.",
    "mind2i":"Mind2i's website features a comprehensive array of content designed to cater to various professional developmentneeds. The platform offers an extensive range of courses, including Python, Data Science, Data Engineering, and Data Analytics",
    "assistance and materials ":"They provide day-to-day material and allow you to create your own assessments, such as practice exercises. They conduct assignments based on the courses and take attendance for day-to-day classes.",
    "Branches":" With a global reach, Mind2i operates in India and the UK, with its headquarters located in Bangalore, India. Contact information is available for their headquarters and overseas offices",
}

# Initial Context for Hugging Face QA Pipeline
BASE_CONTEXT = """
Mind2i's website features a comprehensive array of content designed to cater to various professional development
needs. The platform offers an extensive range of courses, including Python, Data Science, Data Engineering, 
and Data Analytics, among others. Additionally, Mind2i provides internship programs and has collaborations 
with top multinational corporations, ensuring valuable practical experience through real-time projects. 
Their career assistance services encompass job assistance and career counseling, supported by a 
robust alumni network. Mind2i also offers online training programs, which include live classes conducted by 
industry experts and seasoned professionals, as well as recordings of daily sessions for convenient access. 
They provide day-to-day material and allow you to create your own assessments, such as practice exercises. 
They conduct assignments based on the courses and take attendance for day-to-day classes. With a global reach, 
Mind2i operates in India and the UK, with its headquarters located in Bangalore, India. Contact information is 
available for their headquarters and overseas offices, 
including the email address info@mind2i.com and contact number 9606561789, facilitating easy communication."""

# Maintain dynamic context as a global variable
dynamic_context = BASE_CONTEXT

def update_context(user_input, response):
    """Update the context dynamically based on user input and chatbot response."""
    global dynamic_context
    # Append the latest interaction to the context
    interaction = f"User: {user_input}\nChatbot: {response}\n"
    dynamic_context += "\n" + interaction

def classify_query(query):
    """Classify the query using spaCy NLP model."""
    # Tokenize and analyze the query to find a match in predefined responses
    query_lower = query.lower()
    for key in MIND2I_RESPONSES:
        if key in query_lower:
            return key
    return "unknown"

def chatbot_page(request):
    """Render the chatbot page."""
    return render(request, 'chatbot.html')

def chatbot_response(request):
    """Generate chatbot response dynamically."""
    global dynamic_context
    if request.method == 'POST':
        try:
            # Get the user input from POST request as JSON (from chat frontend)
            data = json.loads(request.body)
            user_input = data.get('user_input', '').strip()
            logger.info(f"User Input: {user_input}") # Log the user input to ensure it's being received properly
            if not user_input:
                return JsonResponse({'response': "Please enter a query."})

            # Step 1: Classify the query
            category = classify_query(user_input)
            if category and category in MIND2I_RESPONSES:
                response = MIND2I_RESPONSES[category]
            else:
                # Step 2: Handle unknown queries
                response = "I'm sorry, I can't understand your query. Please ask about Mind2i's services."

            # Step 3: Update the dynamic context
            update_context(user_input, response)

            return JsonResponse({'response': response})

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in request.")
            return JsonResponse({'response': "Invalid input format. Please check your input."})
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Error during processing the request: {e}")
            return JsonResponse({'response': "An error occurred. Please try again later."})
    
    return JsonResponse({'response': "Invalid request method."})
