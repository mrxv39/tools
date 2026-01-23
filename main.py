import time

from src.config import load_config
from src.runtime import RouterRuntime


def main():
    cfg = load_config()
    print('ChatGPT Router (polling del portapapeles)')
    print('- Detecta cambios en el portapapeles y enruta: CMD / PowerShell / Archivo')
    print('- Ctrl+C → salir\n')

    runtime = RouterRuntime(cfg)
    runtime.start()

    try:
        while runtime.is_running():
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\n[Router detenido por Ctrl+C]')
    finally:
        runtime.stop()


if __name__ == '__main__':
    main()
