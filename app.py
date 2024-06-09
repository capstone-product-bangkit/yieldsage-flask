from model import predictProjectImage, Model

from requirements import Flask, request, jsonify, make_response, load_dotenv

load_dotenv()
app = Flask(__name__)


# create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/predict', methods=['POST'])
def predictProject():
    images_data = {}
    Yieldsage = Model('yolo_saved_model')
    data = request.get_json()
    image_urls = data.get('imageUrls', [])
    predictionResults, image_path, base64_images = predictProjectImage(image_urls, Yieldsage)

    for image_name in image_path:
        images_data[image_name] = base64_images[image_path.index(image_name)]
    
    
    return jsonify({'predictionResults': predictionResults, 'images': images_data})

if __name__ == '__main__':
    app.run(debug=True, port=8000)