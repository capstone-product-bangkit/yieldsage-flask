from model import predictProjectImage, Model

from requirements import Flask, request, jsonify, make_response, load_dotenv, requests, BytesIO

from convertSingleNDVI import calculate_ndvi

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

@app.route('/calculate-ndvi', methods=['POST'])
def calculateNDVI():
    images_data = {}
    data = request.get_json()
    image_urls = data.get('imageUrls', [])
    print(image_urls)

    image_files = []

    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            image = BytesIO(response.content).read()
            image_files.append(image)

    if len(image_files) == 2:
        result = calculate_ndvi(image_files[0], image_files[1])
        if result is not None:
            health_status, average_ndvi, ndvi_base64 = result
            # print(health_status, average_ndvi, ndvi_base64)
        else:
            logging.error("Failed to calculate NDVI.")
    else:
        logging.error("Failed to download images or incorrect number of images.")

    return jsonify({'health_status': health_status, 'average_ndvi': average_ndvi, 'ndvi_image': ndvi_base64})

if __name__ == '__main__':
    app.run(debug=True, port=8000)