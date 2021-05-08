import flask
from flask import request
import json
import util
import logging


app = flask.Flask(__name__)
logging.basicConfig(filename='record.log', level=logging.DEBUG,
    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route('/check')
def get_weather():
    if "locality" not in request.args:
        response = flask.Response("Please use locality parameter to search for locality", 400)
    else:
        locality = request.args.get("locality")
        if locality is None:
            response = flask.Response("Bad request. No locality found in request query parameters.", 400)
        else:
            try:
                result = util.get_data(locality)
                response = flask.Response(json.dumps(result, indent=1), 200)

            except LookupError:
                response = flask.Response("Sorry. Locality not found in our database.", 404)

            except RuntimeError as e:
                response = flask.Response(str(e), 500)

            except Exception as e:
                response =  flask.Response(str(e), 500)

    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    app.run(port=8889, debug=True)
