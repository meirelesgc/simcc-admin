from dotenv import load_dotenv

from adm_simcc import create_app

if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5001)
