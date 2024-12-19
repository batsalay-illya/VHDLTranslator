import chardet
import logging

class Debug():
    _loggers = {}
    _file_handler = None

    @staticmethod
    def get_logger(logger_name: str) -> logging.Logger:
        if Debug._file_handler is None:
            Debug._file_handler = Debug._get_file_handler()

        if logger_name not in Debug._loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)

            logger.addHandler(Debug._file_handler)
            logger.addHandler(Debug._get_stream_handler())
            
            logger.propagate = False

            Debug._loggers[logger_name] = logger

        return Debug._loggers[logger_name]
    
    def _get_file_handler():
        file_handler = logging.FileHandler(f"result\output.log", mode = "w")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(name)s | %(levelname)s | %(message)s"))
        return file_handler

    def _get_stream_handler():
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(name)s | %(levelname)s | %(message)s"))
        return stream_handler

    @staticmethod
    def write_visit_to_log(logger, ctx_name : str):
        logger.info(f"{ctx_name} - visited")

    @staticmethod
    def detect_encoding(logger: logging.Logger, file_path: str) -> None:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)

            logger.info(f"File encoding: {result['encoding']}")
            return result['encoding']