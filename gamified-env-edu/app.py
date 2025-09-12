from flask import Flask, request, jsonify, render_template
import requests
import base64
import os

app = Flask(__name__)

# Google Cloud Vision API setup
API_KEY = "AIzaSyDfSRv5sqxheq-JdZih6PJ4hF3mmRI3FqI"
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

@app.route('/')
def scan_home():
    return render_template('scan.html')

@app.route('/api/scan', methods=['POST'])
def process_scan():
    try:
        # Get image data from request
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'})
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Prepare request for Google Vision API
        vision_request = {
            "requests": [
                {
                    "image": {
                        "content": image_data
                    },
                    "features": [
                        {
                            "type": "LABEL_DETECTION",
                            "maxResults": 10
                        },
                        {
                            "type": "WEB_DETECTION",
                            "maxResults": 5
                        }
                    ]
                }
            ]
        }
        
        # Call Google Vision API
        response = requests.post(VISION_API_URL, json=vision_request)
        result = response.json()
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']['message']})
        
        # Process the results
        labels = result['responses'][0].get('labelAnnotations', [])
        web_entities = result['responses'][0].get('webDetection', {}).get('webEntities', [])
        
        # Process labels for environmental education
        environmental_labels = []
        for label in labels:
            if is_environmental_concept(label['description']):
                environmental_labels.append({
                    'concept': label['description'],
                    'score': label.get('score', 0),
                    'type': 'label'
                })
        
        # Add relevant web entities
        for entity in web_entities:
            if (entity.get('description') and 
                is_environmental_concept(entity['description']) and
                not any(item['concept'].lower() == entity['description'].lower() for item in environmental_labels)):
                environmental_labels.append({
                    'concept': entity['description'],
                    'score': entity.get('score', 0.5),
                    'type': 'web'
                })
        
        # Limit to top results and ensure uniqueness
        unique_concepts = set()
        unique_labels = []
        for label in environmental_labels:
            if label['concept'].lower() not in unique_concepts:
                unique_concepts.add(label['concept'].lower())
                unique_labels.append(label)
        
        unique_labels.sort(key=lambda x: x['score'], reverse=True)
        environmental_labels = unique_labels[:6]  # Top 6 results
        
        return jsonify({
            'success': True,
            'results': environmental_labels,
            'educational_content': generate_educational_content(environmental_labels)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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