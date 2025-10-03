import threading
import os
import sys
import src.mqtt.mtqq_client as mqtt_client
from src.mqtt.MqttPublisher import MqttPublisher
from src.CowrieLog import CowrieLog
from src.CollectLogCowrie import CollectLogCowrie
from src.logger import configure_logging_from_argv


def initialize_logging(argv: list[str]) -> None:
    """Inizializza il sistema di logging utilizzando gli argomenti della riga di comando."""
    configure_logging_from_argv(argv)


def create_cowrie_log(config_path: str = "text.json", topic: str = "cowrie/logs") -> CowrieLog:
    """Crea un'istanza di CowrieLog con i percorsi di configurazione e log specificati."""
    return CowrieLog(config_path, topic)


def create_mqtt_publisher() -> MqttPublisher:
    """Crea un'istanza di MqttPublisher."""
    return MqttPublisher()


def create_collect_log_cowrie(cowrie_log: CowrieLog, mqtt_publisher: MqttPublisher) -> CollectLogCowrie:
    """Crea un'istanza di CollectLogCowrie utilizzando CowrieLog e MqttPublisher."""
    return CollectLogCowrie(cowrie_log, mqtt_publisher)


def print_runtime_context() -> None:
    """Stampa il contesto di runtime, incluso l'ID del processo e il nome del thread principale."""
    print(f"ID del processo che esegue il programma principale: {os.getpid()}")
    print(f"Nome del thread principale: {threading.current_thread().name}")


def start_collect_log_cowrie_worker(collect_log_cowrie: CollectLogCowrie, thread_name: str = "Thread-MqttPublisher") -> None:
    """Avvia il worker di CollectLogCowrie in un thread separato."""
    thread = threading.Thread(target=collect_log_cowrie.run, name=thread_name)
    thread.start()
    thread.join()


def main(argv: list[str] | None = None) -> None:
    """Funzione principale per inizializzare e avviare il sistema di raccolta e pubblicazione dei log."""
    if argv is None:
        argv = sys.argv

    initialize_logging(argv)
    cowrie_log = create_cowrie_log()
    mqtt_publisher = create_mqtt_publisher()
    collect_log_cowrie = create_collect_log_cowrie(cowrie_log, mqtt_publisher)
    print_runtime_context()
    start_collect_log_cowrie_worker(collect_log_cowrie)


if __name__ == "__main__":
    main()