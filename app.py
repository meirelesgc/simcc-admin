import sys

from adm_simcc.app import create_app

if __name__ == "__main__":
    default_port = 8000
    port = default_port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            print(f"Porta especificada via argumento: {port}")
        except ValueError:
            print(f"Aviso: '{sys.argv[1]}' não é um número de porta válido.")
            print(f"Usando a porta padrão: {default_port}")
            port = default_port
    else:
        print(f"Usando a porta padrão: {default_port}")

    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=port)
