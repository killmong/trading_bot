import hmac, hashlib, time, logging, requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key    = api_key
        self.api_secret = api_secret
        self.session    = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query     = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def post(self, endpoint: str, params: dict) -> dict:
        signed = self._sign(params)
        url    = f"{BASE_URL}{endpoint}"
        logger.debug("POST %s  params=%s", url, {k: v for k, v in signed.items() if k != "signature"})
        try:
            resp = self.session.post(url, params=signed, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("Response: %s", data)
            return data
        except requests.HTTPError as e:
            logger.error("HTTP error: %s  body=%s", e, e.response.text)
            raise
        except requests.RequestException as e:
            logger.error("Network error: %s", e)
            raise
