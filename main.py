import threading
import os
import sys
import src.mqtt.mtqq_client as mqtt_client
from src.mqtt.MqttPublisher import MqttPublisher
from src.CowrieLog import CowrieLog
from src.CollectLogCowrie import CollectLogCowrie
from src.FtpLog import FtpLog
from src.CollectLogFtp import CollectLogFtp
import src.logger.config
import logging


logger = logging.getLogger(__name__)


def initialize_logging(argv: list[str]) -> None:
    """Inizializza il sistema di logging utilizzando gli argomenti della riga di comando."""
    src.logger.config.configure_logging_from_argv(argv, use_color=True)


def create_cowrie_log(config_path: str = os.getenv("COWRIE_CONFIG_PATH"), topic: str = "cowrie/logs") -> CowrieLog:
    """Crea un'istanza di CowrieLog con i percorsi di configurazione e log specificati."""
    return CowrieLog(config_path, topic)


def create_ftp_log(config_path: str = os.getenv("FTP_CONFIG_PATH"), topic: str = "ftp/logs") -> FtpLog:
    """Crea un'istanza di FtpLog con il percorso del log e il topic MQTT."""
    return FtpLog(config_path, topic)


def create_mqtt_publisher() -> MqttPublisher:
    """Crea un'istanza di MqttPublisher."""
    try:
        mqttPub = MqttPublisher()
    except Exception as e:
        logger.error("Errore durante la creazione di MqttPublisher: %s", e)
        return None
    return mqttPub


def create_collect_log_cowrie(cowrie_log: CowrieLog, mqtt_publisher: MqttPublisher) -> CollectLogCowrie:
    """Crea un'istanza di CollectLogCowrie utilizzando CowrieLog e MqttPublisher."""
    return CollectLogCowrie(cowrie_log, mqtt_publisher)


def create_collect_log_ftp(ftp_log: FtpLog, mqtt_publisher: MqttPublisher) -> CollectLogFtp:
    """Crea un'istanza di CollectLogFtp utilizzando FtpLog e MqttPublisher."""
    return CollectLogFtp(ftp_log, mqtt_publisher)


def print_runtime_context() -> None:
    """Stampa il contesto di runtime, incluso l'ID del processo e il nome del thread principale."""
    logger.info(f"ID del processo che esegue il programma principale: {os.getpid()}")
    logger.info(f"Nome del thread principale: {threading.current_thread().name}")


def start_collect_log_cowrie_worker(
    collect_log_cowrie: CollectLogCowrie,
    thread_name: str = "Thread-MqttPublisher",
) -> threading.Thread:
    """Avvia il worker di CollectLogCowrie in un thread separato e restituisce il thread avviato."""
    thread = threading.Thread(target=collect_log_cowrie.run, name=thread_name)
    thread.start()
    return thread


def start_collect_log_ftp_worker(
    collect_log_ftp: CollectLogFtp,
    thread_name: str = "Thread-FtpPublisher",
) -> threading.Thread:
    """Avvia il worker di CollectLogFtp in un thread separato e restituisce il thread avviato."""
    thread = threading.Thread(target=collect_log_ftp.run, name=thread_name)
    thread.start()
    return thread


def main(argv: list[str] | None = None) -> None:
    """Funzione principale per inizializzare e avviare il sistema di raccolta e pubblicazione dei log."""
    if argv is None:
        argv = sys.argv

    initialize_logging(argv)
    print_runtime_context()
    cowrie_log = create_cowrie_log()
    ftp_log = create_ftp_log()
    mqtt_publisher_cowrie = create_mqtt_publisher()
    mqtt_publisher_ftp = create_mqtt_publisher()
    collect_log_cowrie = create_collect_log_cowrie(cowrie_log, mqtt_publisher_cowrie)
    collect_log_ftp = create_collect_log_ftp(ftp_log, mqtt_publisher_ftp)

    threads = [
        start_collect_log_ftp_worker(collect_log_ftp),
        start_collect_log_cowrie_worker(collect_log_cowrie),
        
    ]

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()