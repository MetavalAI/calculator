import sys
from app import create_app

print("1. Starting App", flush=True)
app = create_app()
print("2. App Created", flush=True)
if __name__ == '__main__':
    print("3. Running Server", flush=True)
    print(f" * Running on http://127.0.0.1:5000", flush=True)
    sys.stdout.flush()
    
    app.run(
        debug=True,
        use_reloader=False,
        host='0.0.0.0',
        port=5000
    )


# admin, admin123
# python run.py
# http://localhost:5000
# http://localhost:5000/login   
# http://localhost:5000/create-formula
# http://localhost:5000/calculate
# http://localhost:5000/download
# http://localhost:5000/logout
# http://localhost:5000/unit-conversions

