from flask import Flask, jsonify, request, redirect
from scrapper.functions import scrape_properties
import json
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Configuración de Swagger UI
SWAGGER_URL = '/swagger'
API_DOCS_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_DOCS_URL,
    config={'app_name': "Reffindr API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint de inicio
@app.route('/')
def index():
    return redirect('/swagger')

# Endpoint para argenprop
@app.route('/argenprop', methods=['GET', 'POST'])
def argenprop_web_scraper():
    try:
        # Leer datos del request
        if request.method == 'POST':
            data = json.loads(request.data)
            pais = data.get("pais")
            limite = data.get("limite", None)
        else:  # GET
            pais = request.args.get("pais")
            limite = request.args.get("limite", type=int)

        # Validaciones
        if not pais:
            return jsonify({"error": "El campo 'pais' es obligatorio"}), 400
        if limite is not None and limite <= 0:
            return jsonify({"error": "El campo 'limite' debe ser un número entero positivo."}), 400

        # URL base
        base_url = f'https://www.argenprop.com/casas/alquiler/{pais}'

        # Ejecutar scraping
        casas = scrape_properties(base_url, limite)

        # Si no se encontraron propiedades
        if not casas:
            return jsonify({"error": "No se encontraron propiedades para el país indicado."}), 404

        return jsonify(casas)

    except json.JSONDecodeError:
        return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON válido."}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
