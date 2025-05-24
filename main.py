from server import app
from flask import Flask, jsonify, request
import json

if __name__ == "__main__":
    print("Starting server...")

    app.run(host='0.0.0.0' , port=8000,debug=True)

    print("Server started.")



    #
