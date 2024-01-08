# -*- coding: utf-8 -*-
# Coded by Who Knows
# Please don't change any code
# https://t.me/Moonlightcrow

import os
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from queue import Queue
from colorama import Fore, Style
from platform import system
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class CMSDetector:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.url_queue = Queue()
        self.results_folder = 'results'
        self.common_cms = ['wordpress', 'joomla', 'drupal', 'wix', 'shopify', 'magento', 'vbulletin', 'prestashop',
                           'cmsmadesimple', 'drupalcommerce','opencart','phpbb']

    def create_folder(self):
        if not os.path.exists('results'):
            os.makedirs('results')

    def queue_urls(self, file_path):
        with open(file_path, 'r') as file:
            site_list = [line.strip() for line in file]
            for url in site_list:
                self.url_queue.put(url)

    def get_cms(self, url):
        try:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            fatch = requests.get(url, headers=self.headers, verify=True, timeout=10)
        except requests.RequestException :
            print(f"[!] {Fore.CYAN} {url} {Style.RESET_ALL}=>{Fore.RED} Invalid {Style.RESET_ALL}")

        else:
            if 'text/html' not in fatch.headers.get('content-type', ''):
                return
            html_content = fatch.text
            cms_headers = fatch.headers.get('X-Powered-By', '').lower()
            soup = BeautifulSoup(html_content, 'html.parser')
            meta_generator = soup.find('meta', {'name': 'generator'})
            cms_meta = meta_generator.get('content').lower() if meta_generator else ''

            detected_cms = [cms for cms in self.common_cms if cms in cms_headers or cms in cms_meta]
            if detected_cms:
                self.save_result(url, detected_cms[0])
                print(f"[+] {Fore.CYAN} {url} {Style.RESET_ALL}=>{Fore.GREEN} {', '.join(detected_cms)}{Style.RESET_ALL}")
            else:
                print(f"[-] {Fore.CYAN} {url} {Style.RESET_ALL}=>{Fore.RED} Not detected !{Style.RESET_ALL}")



    def save_result(self, url, cms):
        with open(f"results/{cms}_results.txt", 'a') as file:
            file.write(url + '\n')
            file.close()

    def process_sites(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.get_cms, iter(self.url_queue.get, None))

    def main(self, file_path):
        self.create_folder()
        self.queue_urls(file_path)
        self.process_sites()


def banner() -> None:
    print(f"""\t
\t
\t
\t ██████╗███╗   ███╗███████╗
\t██╔════╝████╗ ████║██╔════╝
\t██║     ██╔████╔██║███████╗
\t██║     ██║╚██╔╝██║╚════██║
\t╚██████╗██║ ╚═╝ ██║███████║
\t ╚═════╝╚═╝     ╚═╝╚══════╝
\t                           - detector v0.1                                      
""")
    print(f"""\tcms-detector by {Fore.GREEN}Who Knows{Style.RESET_ALL}
    \n\t {Fore.GREEN}TeaM : @Moonlightcrow{Style.RESET_ALL} Telegram : https://t.me/Moonlightcrow   

""")

def clear():
    if system() == 'Linux':
        os.system('clear')
    if system() == 'Windows':
        os.system('cls')

if __name__ == "__main__":
    clear()
    banner()
    file_path = input("Enter Your Site List : ")
    num_threads = int(input("Enter the number of threads : "))
    cms_detector = CMSDetector(num_threads)
    cms_detector.main(file_path)
