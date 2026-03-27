#!/usr/bin/env python3
# AgenTester v0.1
# Automated User-Agent Tester
# By Mohamed Elsayed

import requests
import urllib3
import argparse
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings()

init(autoreset=True)

BANNER = f"""{Fore.GREEN}
        # Do you trust User-Agent? Don't… 😏{Style.BRIGHT}
    _                  _____         _            
   / \\   __ _  ___ _ _|_   _|__  ___| |_ ___ _ __ 
  / _ \\ / _` |/ _ \\ '_ \\| |/ _ \\/ __| __/ _ \\ '__|
 / ___ \\ (_| |  __/ | | | |  __/\\__ \\ ||  __/ |   
/_/   \\_\\__, |\\___|_| |_|_|\\___||___/\\__\\___|_| {Style.NORMAL}v0.2{Style.BRIGHT}
        |___/   
               {Style.RESET_ALL}{Fore.MAGENTA}# By Mohamed Elsayed - 0xkalil
{Style.RESET_ALL}"""

BASIC_HEADERS = {
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=1000",
    "Referer": "https://www.google.com/",
}


def send_request(url, method, agent, proxy):
    try:
        headers = BASIC_HEADERS.copy()
        headers["User-Agent"] = agent

        r = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=5,
            allow_redirects=True,
            proxies=proxy,
            verify=False
        )

        status = r.status_code

        if status == 403:
            status_color = Fore.RED
        elif status == 200:
            status_color = Fore.GREEN
        else:
            status_color = Fore.YELLOW

        return (
            f"{Fore.WHITE}{method:<6} "
            f"{status_color}{status:<6} "
            f"{Fore.MAGENTA}{len(r.content):<8} "
            f"{Fore.BLUE}{agent}"
        )

    except Exception as error:
        return Fore.RED + f"[ERROR] {error}"


def useragent_tester(url, method, proxy=None, threads=10):
    try:
        with open("./user-agents.txt", "r") as file:
            user_agents = file.read().splitlines()
    except FileNotFoundError:
        print(Fore.RED + "[!] user-agents.txt not found")
        return

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(send_request, url, method, agent, proxy)
            for agent in user_agents
        ]

        for future in as_completed(futures):
            try:
                print(future.result())
            except KeyboardInterrupt:
                print(Fore.RED + "\n[!] Interrupted.")
                break


# ---------------- argparse ----------------
parser = argparse.ArgumentParser(description="AgenTester - User-Agent Tester")

parser.add_argument("-u", "--url", help="Target URL", required=True)
parser.add_argument("-p", "--proxy", help="Proxy (ip:port)", required=False)
parser.add_argument("-t", "--threads", help="Number of threads (default 10)", type=int, default=10)
parser.add_argument("-m", "--method", help="HTTP Method (default GET)", default="GET")

args = parser.parse_args()

# ---------------- execution ----------------
print(BANNER)

url = args.url

if not url.startswith(("http://", "https://")):
    print(Fore.RED + "[!] Invalid URL.")
    exit()

proxy = args.proxy

if proxy:
    if not proxy.startswith("http"):
        proxy = "http://" + proxy

    proxies = {
        "http": proxy,
        "https": proxy,
    }
else:
    proxies = None

print(f"\n{Fore.WHITE}Method Status Length   Payload\n{'-'*50}")

useragent_tester(url, args.method, proxies, args.threads)
