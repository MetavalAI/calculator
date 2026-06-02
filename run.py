from app import create_app

print("1. Starting App")

app = create_app()

print("2. App Created")

if __name__ == '__main__':

    print("3. Running Server")

    app.run(
        debug=True,
        use_reloader=False
    )


# admin, admin123
# python run.py
# http://localhost:5000
# http://localhost:5000/login   
# http://localhost:5000/create-formula
# http://localhost:5000/calculate
# http://localhost:5000/download
# http://localhost:5000/logout
# http://localhost:5000/
