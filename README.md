

---

NodePay No-Proxy Bot

This Python script automates API interactions for multiple accounts using tokens. It establishes sessions, sends periodic pings to keep the connection alive, and handles multiple accounts concurrently without proxies.


---

Features

Multi-Account Support: Handles multiple accounts by reading tokens from a token.txt file.

Concurrent Tasks: Uses asyncio to manage multiple accounts simultaneously.

Session Management: Automatically logs in and maintains session information.

Error Handling: Handles API errors, connection issues, and token expiration gracefully.



---

Requirements

Python 3.7 or higher

Required Python libraries:

cloudscraper

requests

loguru

fake_useragent




---

Installation

1. Clone or download the repository:

git clone https://github.com/your-repo/nodepay-noproxy.git
cd nodepay-noproxy


2. Install the required libraries:

pip install cloudscraper requests loguru fake-useragent


3. Create a token.txt file in the project directory and add your tokens, one per line:

token_1
token_2
token_3




---

Usage

Run the script with the following command:

python bot.py


---

File Descriptions

bot.py: Main script that handles API interactions and multi-account management.

token.txt: File containing the tokens for each account, one per line.



---

Configuration

Constants in the Script

PING_INTERVAL: Time interval (in seconds) between pings. Default is 60.

RETRIES: Number of retry attempts for failed API requests. Default is 60.



---

Logs

The script logs activity using the loguru library. Key log messages include:

Token login status

Ping results

Errors during API calls or session handling


Logs are displayed in the console.


---

Error Handling

The script:

Retries failed API requests automatically.

Logs errors related to connection issues, invalid tokens, or expired sessions.

Skips problematic tokens without affecting others.



---

Disclaimer

This tool is provided "as is." Use it at your own risk. The author is not responsible for any misuse or consequences resulting from using this tool.


---

You can save this as a README.md file in your project directory. Let me know if you need further assistance!

