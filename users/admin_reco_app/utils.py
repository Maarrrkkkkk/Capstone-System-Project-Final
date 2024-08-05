
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Faculty, Adviser

def get_expertise_descriptions():
    """
    Retrieve expertise descriptions for all faculty members who have a master's degree.
    """
    faculty_list = Faculty.objects.filter(has_master_degree=True)
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
    return descriptions, faculty_list  # Return both descriptions and the filtered faculty list

def find_top_n_advisers(title, n=3):
    # Filter out faculty with a master's degree and construct expertise descriptions
    expertise_descriptions, faculty_list = get_expertise_descriptions()
    vectorizer = TfidfVectorizer()
    title_vector = vectorizer.fit_transform([title])
    expertise_vectors = vectorizer.transform(expertise_descriptions)
    cosine_similarities = cosine_similarity(title_vector, expertise_vectors).flatten()

    # Combine faculty and their corresponding cosine similarities
    scores = list(zip(faculty_list, cosine_similarities))
    scores.sort(key=lambda x: x[1], reverse=True)  # Sort by similarity score

    # Filter out faculty with 4 advisees
    eligible_advisers = [faculty for faculty, score in scores if Adviser.objects.filter(faculty=faculty).count() < 4]

    # Return top n eligible advisers
    return eligible_advisers[:n]
