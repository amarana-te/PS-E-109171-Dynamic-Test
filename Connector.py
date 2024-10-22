import httpx
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime



##############NO Async###################################
class ConnectorSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        
        if cls._instance is None:
            
            limits = httpx.Limits(max_keepalive_connections=15, max_connections=20, keepalive_expiry=15)
            timeout = httpx.Timeout(27, read=None, pool=15)
            cls._instance = httpx.Client(limits=limits, timeout=timeout)
        
        return cls._instance


super_http = ConnectorSingleton.get_instance()

def setup_api_calls_logger():
    # Crear el logger para las llamadas de API
    logger = logging.getLogger("api_calls_logger")
    
    # Verificar si ya está configurado
    if not logger.hasHandlers():

        logger.setLevel(logging.INFO)
        
        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename='api_calls.log', maxBytes=100000, backupCount=5)
        
        # Configurar el formato del log
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)

    
    return logger


logging = setup_api_calls_logger()



def handle_api_errors(response, endpoint):
    """Handle specific API error responses."""
    
    if response.status_code in {400, 401, 403, 404, 405}:
        
        error_message = f"Error {response.status_code} for {endpoint}: {response.text}"
        logging.error(error_message)
        
        return response.status_code, response.json(), True
    
    return None, None, False


def log_request(endpoint, status_code, roundtrip):

    """Log the request details including the time taken and status code."""
    
    logging.info(f"Status Code {status_code}: {endpoint} time: {roundtrip:.4f} seconds")


def request_with_retry(method, url, **kwargs):

    """Generic request function with retry for rate limiting, timing, extra sleep time, and error handling."""
    start = time.time()
    response = super_http.request(method, url, **kwargs)
    roundtrip = time.time() - start

        # New rule: Check rate limit remaining and sleep if needed
    rate_limit_remaining = int(response.headers.get('x-organization-rate-limit-remaining', 240))
    reset_time =  (datetime.fromtimestamp(int(response.headers.get('x-organization-rate-limit-reset', 0))) - datetime.now()).total_seconds()
    
    if rate_limit_remaining <= 11 and reset_time >= 17:
        
        time.sleep(7)  # Sleep for 7 seconds to relieve the API

    if response.status_code == 429:
        
        reset_timestamp = int(response.headers.get('x-organization-rate-limit-reset', 0))
        sleep_time = (datetime.fromtimestamp(reset_timestamp) - datetime.now()).total_seconds() + 1
        time.sleep(max(0, sleep_time))
        retry_start = time.time()
        response = super_http.request(method, url, **kwargs)
        roundtrip = time.time() - retry_start
    
    log_request(url, response.status_code, roundtrip)
    # Handle specific error codes
    status_code, error_response, has_error = handle_api_errors(response, url)
    
    if has_error:

        return status_code, error_response
    
    return response.status_code, response.json()


def get_data(headers, endp_url, params):
    
    status_code, response = request_with_retry('GET', endp_url, headers=headers, params=params)
    
    if isinstance(response, dict) or status_code in {200, 201}:
    
        return status_code, response
    
    else:
        # Handle non-JSON responses or unexpected outcomes
    
        return status_code, {"error": "Unexpected error occurred"}


def post_data(headers, endp_url, payload):
    
    status_code, response = request_with_retry('POST', url=endp_url, headers=headers, data=payload)
    
    if isinstance(response, dict) or status_code in {200, 201}:
    
        return status_code, response
    
    else:
    
        # Handle non-JSON responses or unexpected outcomes
        return status_code, {"error": "Unexpected error occurred"}
    
    
def put_data(headers, endp_url, payload):
    
    status_code, response = request_with_retry('PUT', url=endp_url, headers=headers, data=payload)
    
    if isinstance(response, dict) or status_code in {200, 201}:
    
        return status_code, response
    
    else:
    
        # Handle non-JSON responses or unexpected outcomes
        return status_code, response