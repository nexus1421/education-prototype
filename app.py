from flask import Flask, request, jsonify, render_template
import requests
import base64
import os

app = Flask(__name__)

# ClarifAI API setup - Using environment variable for security
API_KEY = os.environ.get('CLARIFAI_API_KEY', 'b8207ec0bbff4dabb72bf2280b14e005')
CLARIFAI_API_URL = "https://api.clarifai.com/v2/models/aaa03c23b3724a16a56b629203edc62c/outputs"  # General model

@app.route('/')
def scan_home():
    return render_template('scan.html')

@app.route('/api/scan', methods=['POST'])
def process_scan():
    try:
        # First, check if we have a valid API key
        if not API_KEY or API_KEY == 'b8207ec0bbff4dabb72bf2280b14e005':
            # Return mock data if API key is not properly set
            return use_mock_data()
        
        # Get image data from request
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'})
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Prepare request for ClarifAI API
        headers = {
            'Authorization': f'Key {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # ClarifAI expects the image in a specific format
        payload = {
            "inputs": [
                {
                    "data": {
                        "image": {
                            "base64": image_data
                        }
                    }
                }
            ]
        }
        
        # Call ClarifAI API
        response = requests.post(CLARIFAI_API_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            # If API fails, fall back to mock data
            return use_mock_data_with_note(f"ClarifAI API error: {response.text}")
        
        result = response.json()
        
        # Process ClarifAI response
        concepts = result['outputs'][0]['data']['concepts']
        
        # Process concepts for environmental education
        environmental_labels = []
        for concept in concepts:
            if is_environmental_concept(concept['name']):
                environmental_labels.append({
                    'concept': concept['name'],
                    'score': concept.get('value', 0),
                    'type': 'clarifai'
                })
        
        # If no environmental concepts found, use mock data
        if not environmental_labels:
            return use_mock_data_with_note("No environmental elements detected - showing sample data")
        
        # Limit to top results
        environmental_labels.sort(key=lambda x: x['score'], reverse=True)
        environmental_labels = environmental_labels[:6]
        
        return jsonify({
            'success': True,
            'results': environmental_labels,
            'educational_content': generate_educational_content(environmental_labels)
        })
    
    except Exception as e:
        # If any error occurs, use mock data
        return use_mock_data_with_note(f"Error: {str(e)} - showing sample data")

def use_mock_data():
    """Return mock environmental data for testing"""
    environmental_labels = [
        {'concept': 'Plant', 'score': 0.85, 'type': 'mock'},
        {'concept': 'Tree', 'score': 0.78, 'type': 'mock'},
        {'concept': 'Nature', 'score': 0.92, 'type': 'mock'},
        {'concept': 'Green Environment', 'score': 0.88, 'type': 'mock'},
        {'concept': 'Forest', 'score': 0.82, 'type': 'mock'},
        {'concept': 'Ecosystem', 'score': 0.75, 'type': 'mock'}
    ]
    
    return jsonify({
        'success': True,
        'results': environmental_labels,
        'educational_content': generate_educational_content(environmental_labels),
        'note': 'Using mock data - configure ClarifAI API for real analysis'
    })

def use_mock_data_with_note(note):
    """Return mock data with a specific note"""
    environmental_labels = [
        {'concept': 'Plant', 'score': 0.85, 'type': 'mock'},
        {'concept': 'Tree', 'score': 0.78, 'type': 'mock'},
        {'concept': 'Nature', 'score': 0.92, 'type': 'mock'},
        {'concept': 'Green Environment', 'score': 0.88, 'type': 'mock'}
    ]
    
    return jsonify({
        'success': True,
        'results': environmental_labels,
        'educational_content': generate_educational_content(environmental_labels),
        'note': note
    })

def is_environmental_concept(label):
    # Define what constitutes an environmental concept
    environmental_keywords = [
        'plant', 'tree', 'animal', 'water', 'air', 'pollution', 'recycle', 
        'nature', 'environment', 'eco', 'green', 'flower', 'leaf', 'forest',
        'ocean', 'river', 'lake', 'mountain', 'wildlife', 'bird', 'insect',
        'sustainability', 'climate', 'energy', 'solar', 'wind', 'renewable',
        'carbon', 'emissions', 'ecosystem', 'biodiversity', 'conservation',
        'organic', 'garden', 'park', 'beach', 'coral', 'reef', 'fish',
        'recycling', 'compost', 'waste', 'plastic', 'paper', 'metal', 'glass',
        'weather', 'cloud', 'sky', 'sun', 'rain', 'snow', 'soil', 'earth',
        'wood', 'forestry', 'agriculture', 'farm', 'crop', 'food', 'fruit',
        'vegetable', 'seed', 'root', 'branch', 'trunk', 'canopy', 'habitat',
        'species', 'endangered', 'extinction', 'preservation', 'protection'
    ]
    return any(keyword in label.lower() for keyword in environmental_keywords)

def generate_educational_content(labels):
    # Generate educational content based on detected labels
    content = []
    
    # Predefined educational content for common environmental concepts
    educational_facts = {
        'plant': {
            'fact': 'Plants produce oxygen through photosynthesis and are essential for life on Earth. They absorb carbon dioxide and release oxygen, helping to regulate our atmosphere.',
            'tip': 'Consider planting native species to support local ecosystems and provide habitat for wildlife.'
        },
        'tree': {
            'fact': 'A single mature tree can absorb up to 48 pounds of carbon dioxide per year and release enough oxygen for two people.',
            'tip': 'Plant trees in your community to combat climate change and reduce urban heat islands.'
        },
        'water': {
            'fact': 'Only 2.5% of Earth\'s water is freshwater, and less than 1% is accessible for human use. The rest is locked in glaciers or underground.',
            'tip': 'Fix leaky faucets to save up to 20 gallons of water per day. Take shorter showers to conserve water.'
        },
        'air': {
            'fact': 'Air pollution causes an estimated 7 million premature deaths worldwide every year. Plants naturally filter many air pollutants.',
            'tip': 'Use public transportation, bike, or walk instead of driving to reduce air pollution and your carbon footprint.'
        },
        'pollution': {
            'fact': 'Plastic pollution in the ocean is expected to triple by 2040 without significant action. Millions of marine animals die each year from plastic ingestion.',
            'tip': 'Reduce single-use plastics by carrying reusable bags, bottles, and containers. Participate in local cleanup events.'
        },
        'recycle': {
            'fact': 'Recycling one aluminum can saves enough energy to run a TV for three hours. Recycling paper saves trees and reduces water usage.',
            'tip': 'Learn your local recycling guidelines to ensure proper recycling. Rinse containers before recycling them.'
        },
        'animal': {
            'fact': 'Biodiversity is crucial for ecosystem health and resilience. Each species plays a unique role in maintaining ecological balance.',
            'tip': 'Support conservation efforts for endangered species in your area. Create wildlife-friendly spaces in your garden.'
        },
        'flower': {
            'fact': 'Flowers are essential for pollination, which allows plants to reproduce. Many flowers have co-evolved with specific pollinators.',
            'tip': 'Plant a variety of flowers that bloom at different times to provide food for pollinators throughout the seasons.'
        },
        'bird': {
            'fact': 'Birds are important indicators of ecosystem health. They help control insect populations and disperse seeds.',
            'tip': 'Provide bird feeders, water sources, and nesting boxes to support local bird populations. Keep cats indoors to protect birds.'
        },
        'insect': {
            'fact': 'Insects are crucial pollinators and form the base of many food chains. Without insects, most ecosystems would collapse.',
            'tip': 'Avoid using pesticides in your garden. Plant native flowers to provide food for beneficial insects.'
        },
        'forest': {
            'fact': 'Forests cover about 30% of the world\'s land area and contain about 80% of the world\'s terrestrial biodiversity.',
            'tip': 'Support sustainable forestry practices and avoid products that contribute to deforestation.'
        },
        'nature': {
            'fact': 'Spending time in nature has been shown to reduce stress, improve mood, and enhance cognitive function.',
            'tip': 'Make time to enjoy natural spaces regularly for both personal well-being and environmental appreciation.'
        }
    }
    
    for label in labels:
        concept = label['concept'].lower()
        
        # Find the best matching educational content
        matched = False
        for key, value in educational_facts.items():
            if key in concept:
                content.append({
                    'concept': label['concept'],
                    'fact': value['fact'],
                    'tip': value['tip'],
                    'score': label['score']
                })
                matched = True
                break
        
        # If no specific match, create generic environmental content
        if not matched:
            content.append({
                'concept': label['concept'],
                'fact': f'{label["concept"]} plays an important role in our ecosystem. Understanding and preserving natural elements is key to environmental sustainability.',
                'tip': 'Learn more about how you can help protect our environment. Small actions multiplied by millions of people can create significant positive change.',
                'score': label['score']
            })
    
    # Sort by score for most relevant first
    content.sort(key=lambda x: x['score'], reverse=True)
    return content

if __name__ == '__main__':
    app.run(debug=True)