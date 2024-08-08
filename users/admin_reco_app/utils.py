import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Faculty, Adviser

# Define the expertise mapping
expertise_mapping = {
    "Machine Learning": "Data Science, Python, Statistics",
    "Web Development": "HTML, CSS, JavaScript, Django",
    "Data Analysis": "Python, Pandas, SQL",
    "Cybersecurity": "Network Security, Cryptography, Risk Management",
    "Mobile Development": "Java, Kotlin, Swift, Flutter",
    "Cloud Computing": "AWS, Azure, Google Cloud, DevOps",
    "DevOps": "CI/CD, Docker, Kubernetes, Jenkins",
    "Blockchain": "Ethereum, Smart Contracts, Solidity, Hyperledger",
    "Game Development": "Unity, Unreal Engine, C#, Game Design",
    "Artificial Intelligence": "Machine Learning, Deep Learning, TensorFlow, PyTorch",
    "Internet of Things": "IoT Protocols, Embedded Systems, Sensor Networks",
    "E-commerce": "Magento, Shopify, WooCommerce, Digital Marketing",
    "Healthcare Informatics": "Health Information Systems, EHR, Data Privacy",
    "Educational Technology": "Learning Management Systems, EdTech Tools, Online Learning",
    "Financial Technology": "FinTech, Blockchain, Payment Systems, Risk Management",
    "Smart City Technologies": "Urban Planning, IoT, Smart Grids, Sustainable Development",
    "Human-Computer Interaction": "User Experience Design, Usability Testing, Interaction Design",
    "Agricultural Technology": "Precision Agriculture, IoT in Agriculture, Smart Farming",
    "Software Engineering": "Software Development Life Cycle, Agile, Scrum, Version Control",
    "Computer Networks": "Network Protocols, Network Security, Wireless Networks",
    "Multimedia and Graphics": "Graphic Design, Video Editing, Animation, 3D Modeling",
    "Database Management and Information Systems": "Database Design, SQL, Data Warehousing",
    "Geographic Information Systems (GIS)": "Spatial Analysis, Remote Sensing, Cartography"
}

def normalize_text(text):
    # Convert camel case to space-separated words
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    # Convert to lowercase
    text = text.lower()
    return text

def get_needed_expertise_for_title(title):
    # Normalize the title
    normalized_title = normalize_text(title)
    
    # Normalize expertise keys
    normalized_expertise_keys = [normalize_text(key) for key in expertise_mapping.keys()]

    # Use scikit-learn's TfidfVectorizer
    vectorizer = TfidfVectorizer()
    # Vectorize the normalized expertise keys
    key_vectors = vectorizer.fit_transform(normalized_expertise_keys)
    # Vectorize the normalized title
    title_vector = vectorizer.transform([normalized_title])
    
    # Compute cosine similarities
    similarities = cosine_similarity(title_vector, key_vectors).flatten()

    # Find the best matching expertise key
    best_match_index = similarities.argmax()
    best_match_key = list(expertise_mapping.keys())[best_match_index]
    
    return expertise_mapping.get(best_match_key, 'General Expertise')

def get_expertise_descriptions():
    faculty_list = Faculty.objects.filter(has_master_degree=True, is_active=True)
    descriptions = []
    for faculty in faculty_list:
        description = []
        if faculty.mobile_web_dev:
            description.append("Mobile and Web Application Development")
        if faculty.database_management:
            description.append("Database Management and Information Systems")
        if faculty.ai_ml:
            description.append("Artificial Intelligence and Machine Learning")
        if faculty.iot:
            description.append("Internet of Things (IoT)")
        if faculty.cybersecurity:
            description.append("Cybersecurity")
        if faculty.gis:
            description.append("Geographic Information Systems (GIS)")
        if faculty.data_analytics:
            description.append("Data Analytics and Business Intelligence")
        if faculty.ecommerce_digital_marketing:
            description.append("E-commerce and Digital Marketing")
        if faculty.educational_technology:
            description.append("Educational Technology")
        if faculty.healthcare_informatics:
            description.append("Healthcare Informatics")
        if faculty.game_development:
            description.append("Game Development")
        if faculty.hci:
            description.append("Human-Computer Interaction")
        if faculty.agricultural_technology:
            description.append("Agricultural Technology")
        if faculty.smart_city_technologies:
            description.append("Smart City Technologies")
        if faculty.fintech:
            description.append("Financial Technology (FinTech)")
        if faculty.computer_networks:
            description.append("Computer Networks")
        if faculty.software_engineering:
            description.append("Software Engineering")
        if faculty.multimedia_graphics:
            description.append("Multimedia and Graphics")

        descriptions.append(' '.join(description))
    return descriptions, faculty_list

def find_top_n_advisers(title, top_n=3, max_matches=10):
    expertise_descriptions, faculty_list = get_expertise_descriptions()

    # Use scikit-learn's TfidfVectorizer
    vectorizer = TfidfVectorizer()
    # Vectorize the expertise descriptions
    X = vectorizer.fit_transform(expertise_descriptions)
    # Vectorize the query title
    query_vector = vectorizer.transform([title])
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_vector, X).flatten()

    # Combine faculty and their corresponding similarity scores
    scores = list(zip(faculty_list, similarities))

    # Sort by similarity score and then by years of teaching in descending order
    scores.sort(key=lambda x: (x[1], x[0].years_of_teaching), reverse=True)

    # Filter out faculty with 4 or more advisees
    eligible_advisers = [faculty for faculty, score in scores if Adviser.objects.filter(faculty=faculty).count() < 4]

    # Return top n eligible advisers and top max_matches eligible advisers
    return eligible_advisers[:top_n], eligible_advisers[:max_matches]
