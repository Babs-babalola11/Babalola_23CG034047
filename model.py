# model.py

from deepface import DeepFace
import logging

# Set up logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_emotion(image_path):
    """
    Analyzes the emotion from an image file using DeepFace.
    
    Args:
        image_path (str): The path to the image file.
        
    Returns:
        str: The dominant emotion (capitalized), 'No face detected', or 'Analysis error'.
    """
    try:
        logging.info(f"Model: Analyzing image at: {image_path}")
        
        # Using the specified backend and settings
        analysis_results = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            detector_backend='opencv',  
            enforce_detection=False  # Crucial for preventing crash on no-face images
        )
        
        # Check if any face was detected
        if not analysis_results or len(analysis_results) == 0:
            logging.warning("Model: No face detected in the image.")
            return "No face detected"
            
        # Get the result from the first detected face
        first_face = analysis_results[0]
        dominant_emotion = first_face.get('dominant_emotion')
        
        if dominant_emotion:
            logging.info(f"Model: Dominant emotion detected: {dominant_emotion}")
            return dominant_emotion.capitalize()
        else:
            logging.warning("Model: DeepFace analysis failed to find dominant emotion key.")
            return "Analysis error"


    except Exception as e:
        # Catch any other errors (e.g., file not found, corrupted image)
        logging.error(f"Model: Error during emotion analysis: {e}")
        return "Analysis error"

# Example of how you could test this locally (optional, for development)
if __name__ == '__main__':
    # You would need an image named 'test_face.jpg' in the same directory to run this
    # result = analyze_emotion('test_face.jpg')
    # print(f"Test Result: {result}")
    pass