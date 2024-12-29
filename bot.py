import asyncio
import time
import uuid
import cloudscraper
import random
from loguru import logger

# Console Colors
MAGENTA = "\033[35m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

# ASCII Banner and Tagline
ascii_banner = r"""
    ______      __        __  ______                 __
   / ____/___  / /_____  / /_/ ____/______  ______  / /_____
  / /_  / __ \/ //_/ _ \/ __/ /   / ___/ / / / __ \/ __/ __ \
 / __/ / /_/ / ,< /  __/ /_/ /___/ /  / /_/ / /_/ / /_/ /_/ /
/_/    \____/_/|_|\___/\__/\____/_/   \__, / .___/\__/\____/
                                     /____/_/
"""

tagline = """
 +-+-+-+-+-+-+ +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
 |A|n|y|o|n|e| |w|a|n|t| |d|o| |s|o|m|e| |d|o|n|a|t|i|o|n|
 +-+-+-+-+-+-+ +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
"""

# Print the banner
print(f"{MAGENTA}{'=' * 70}{RESET}")
print(f"{CYAN}{BOLD}{ascii_banner}{RESET}")
print(f"{YELLOW}{BOLD}{tagline}{RESET}")
print(f"{MAGENTA}{'=' * 70}{RESET}")
print(f"{GREEN}{BOLD}{UNDERLINE}Telegram: https://t.me/mehdreaming{RESET}")
print(f"{RED}{BOLD}{UNDERLINE}YouTube: https://youtube.com/@mehdreaming{RESET}")
print(f"{MAGENTA}{'=' * 70}{RESET}")

# Constants
PING_INTERVAL = 60
RETRIES = 60

DOMAIN_API = {
    "SESSION": "http://api.nodepay.ai/api/auth/session",
    "PING": "http://nw.nodepay.ai/api/network/ping"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}  # Store ping times for each token

# Predefined User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def show_warning():
    print("By using this tool, you understand the risks. Do it at your own risk!")

def uuidv4():
    return str(uuid.uuid4())

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp

async def render_profile_info(token):
    global browser_id, account_info

    try:
        np_session_info = load_session_info()

        if not np_session_info:
            # Generate new browser_id
            browser_id = uuidv4()
            response = await call_api(DOMAIN_API["SESSION"], {}, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(account_info)
                await start_ping(token)
            else:
                handle_logout()
        else:
            account_info = np_session_info
            await start_ping(token)
    except Exception as e:
        logger.error(f"Error in render_profile_info: {e}")

async def call_api(url, data, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": get_random_user_agent(),
        "Content-Type": "application/json",
        "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        raise ValueError(f"Failed API call to {url}")

async def start_ping(token):
    try:
        while True:
            await ping(token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Ping task was cancelled")
    except Exception as e:
        logger.error(f"Error in start_ping: {e}")

async def ping(token):
    global last_ping_time, RETRIES, status_connect

    current_time = time.time()

    # Check if the token has a separate last ping time and if enough time has passed
    if token in last_ping_time and (current_time - last_ping_time[token]) < PING_INTERVAL:
        logger.info(f"Skipping ping for token {token}, not enough time elapsed")
        return

    last_ping_time[token] = current_time  # Update the last ping time for this token

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time()),
            "version": "2.2.7"
        }

        response = await call_api(DOMAIN_API["PING"], data, token)
        if response["code"] == 0:
            logger.info(f"Ping successful for token {token}: {response}")
            RETRIES = 0
            status_connect = CONNECTION_STATES["CONNECTED"]
        else:
            handle_ping_fail(response)
    except Exception as e:
        logger.error(f"Ping failed for token {token}: {e}")
        handle_ping_fail(None)

def handle_ping_fail(response):
    global RETRIES, status_connect

    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout()
    elif RETRIES < 2:
        status_connect = CONNECTION_STATES["DISCONNECTED"]
    else:
        status_connect = CONNECTION_STATES["DISCONNECTED"]

def handle_logout():
    global status_connect, account_info

    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    logger.info(f"Logged out and cleared session info")

def save_session_info(data):
    data_to_save = {
        "uid": data.get("uid"),
        "browser_id": browser_id
    }
    pass

def load_session_info():
    return {}  # Placeholder for loading session info

async def run_with_token(token):
    tasks = {}

    tasks[asyncio.create_task(render_profile_info(token))] = token

    done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        failed_token = tasks[task]
        if task.result() is None:
            logger.info(f"Failed for token {failed_token}, retrying...")
        tasks.pop(task)

    await asyncio.sleep(10)

async def main():
    # Load tokens from the file
    try:
        with open('token.txt', 'r') as file:
            tokens = file.read().splitlines()
    except Exception as e:
        logger.error(f"Error reading token list: {e}")
        return

    if not tokens:
        print("No tokens found. Exiting.")
        return

    tasks = []
    for token in tokens:
        tasks.append(run_with_token(token))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    show_warning()
    print("\nAlright, we here! The tool will now use multiple tokens without proxies.")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
