import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Faculty

def get_expertise_descriptions():
    """
    Retrieve expertise descriptions for all faculty members who have a master's degree.
    """
    faculty_list = Faculty.objects.filter(has_master_degree=True)
    descriptions = []
    for faculty in faculty_list:
        # Constructing a description based on Boolean fields
        expertise = []
        if faculty.mobile_web_dev: expertise.append('Mobile/Web Development')
        if faculty.database_management: expertise.append('Database Management')
        if faculty.ai_ml: expertise.append('AI/ML')
        if faculty.iot: expertise.append('IoT')
        if faculty.cybersecurity: expertise.append('Cybersecurity')
        if faculty.gis: expertise.append('GIS')
        if faculty.data_analytics: expertise.append('Data Analytics')
        if faculty.ecommerce_digital_marketing: expertise.append('E-commerce/Digital Marketing')
        if faculty.educational_technology: expertise.append('Educational Technology')
        if faculty.healthcare_informatics: expertise.append('Healthcare Informatics')
        if faculty.game_development: expertise.append('Game Development')
        if faculty.hci: expertise.append('HCI')
        if faculty.agricultural_technology: expertise.append('Agricultural Technology')
        if faculty.smart_city_technologies: expertise.append('Smart City Technologies')
        if faculty.fintech: expertise.append('FinTech')
        if faculty.computer_networks: expertise.append('Computer Networks')
        if faculty.software_engineering: expertise.append('Software Engineering')
        if faculty.multimedia_graphics: expertise.append('Multimedia/Graphics')
        
        description = ', '.join(expertise)
        descriptions.append(description)
    return descriptions, faculty_list  # Return both descriptions and the filtered faculty list

def extract_faculty_features(faculty):
    """
    Convert the Boolean expertise fields into a feature vector.
    """
    return np.array([
        faculty.mobile_web_dev,
        faculty.database_management,
        faculty.ai_ml,
        faculty.iot,
        faculty.cybersecurity,
        faculty.gis,
        faculty.data_analytics,
        faculty.ecommerce_digital_marketing,
        faculty.educational_technology,
        faculty.healthcare_informatics,
        faculty.game_development,
        faculty.hci,
        faculty.agricultural_technology,
        faculty.smart_city_technologies,
        faculty.fintech,
        faculty.computer_networks,
        faculty.software_engineering,
        faculty.multimedia_graphics
    ])

def get_title_and_expertise_vectors(title, expertise_descriptions):
    """
    Convert the project title and expertise descriptions to TF-IDF vectors.
    """
    vectorizer = TfidfVectorizer()
    all_texts = [title] + expertise_descriptions
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    title_vector = tfidf_matrix[0:1]  # Vector for the project title
    expertise_vectors = tfidf_matrix[1:]  # Vectors for expertise descriptions
    return title_vector, expertise_vectors

def extract_needed_expertise(title, expertise_keywords):
    """
    Extract needed expertise based on the project title.
    """
    title_lower = title.lower()
    needed_expertise = set()

    for keyword in expertise_keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title_lower:
            needed_expertise.add(keyword)

    return list(needed_expertise)

def find_top_advisers(title, eligible_faculty_list):
    """
    Find and rank top advisers based on the project title and Boolean expertise fields.
    """
    expertise_keywords = [
        "Game Development", "Software Engineering", "Human-Computer Interaction",
        "Internet of Things (IoT)", "Data Analytics and Business Intelligence",
        "Cybersecurity", "Database Management and Information Systems", "Educational Technology",
        "Healthcare Informatics", "E-commerce and Digital Marketing", "Geographic Information Systems (GIS)",
        "Smart City Technologies", "Financial Technology (FinTech)", "Multimedia and Graphics",
        "Computer Networks", "Mobile and Web Application Development", "Agricultural Technology"
    ]
    
    expertise_descriptions, faculty_list = get_expertise_descriptions()
    title_vector, expertise_vectors = get_title_and_expertise_vectors(title, expertise_descriptions)
    
    def score_faculty(faculty):
        """
        Score the faculty based on the match between the project's required expertise and the faculty's expertise.
        """
        expertise_vector = extract_faculty_features(faculty)
        matched_expertise = extract_needed_expertise(title, expertise_keywords)
        score = sum(expertise_vector[expertise_keywords.index(keyword.lower())] for keyword in matched_expertise)
        return score

    faculty_scores = [(faculty, score_faculty(faculty)) for faculty in eligible_faculty_list]
    sorted_faculty_scores = sorted(faculty_scores, key=lambda x: x[1], reverse=True)
    top_advisers = [faculty for faculty, score in sorted_faculty_scores]

    needed_expertise = extract_needed_expertise(title, expertise_keywords)

    return top_advisers, needed_expertise


def format_recommendation(title, needed_expertise, top_advisers):
    """
    Format the recommendation result for display.
    """
    result = f"Approved Title: {title}\nNeeded Expertise\n"
    result += ', '.join(needed_expertise) if needed_expertise else "None identified"
    result += "\n\nRecommended Advisers\n"
    
    for adviser in top_advisers:
        expertise = ', '.join([e for e, has in zip([
            'Mobile/Web Development', 'Database Management', 'AI/ML', 'IoT', 'Cybersecurity', 'GIS',
            'Data Analytics', 'E-commerce/Digital Marketing', 'Educational Technology', 'Healthcare Informatics',
            'Game Development', 'HCI', 'Agricultural Technology', 'Smart City Technologies', 'FinTech',
            'Computer Networks', 'Software Engineering', 'Multimedia/Graphics'
        ], extract_faculty_features(adviser)) if has])
        experience = adviser.years_of_teaching if adviser.years_of_teaching else "N/A"
        result += f"{adviser.name} - Expertise: {expertise} - Years of Teaching: {experience}\n"
    
    return result
