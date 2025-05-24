from server import app


if __name__ == "__main__":
    print("Starting server...")

    app.run(host='0.0.0.0' , port=8080,debug=True)

    print("Server started.")




