#!/usr/bin/env python3
"""
Enhanced Content Fetcher with JavaScript support
Handles both static and dynamic websites
"""

import os
from pathlib import Path
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class EnhancedContentFetcher:
    """Enhanced content fetcher with JavaScript rendering support."""

    def __init__(self, use_selenium=False):
        """Initialize the fetcher.

        Args:
            use_selenium: If True, always use Selenium for fetching
        """
        self.use_selenium = use_selenium
        self.min_content_length = 500  # Minimum acceptable content length

    def fetch(self, url):
        """Fetch content from URL with automatic fallback to Selenium."""

        # First try with newspaper3k
        result = self._fetch_with_newspaper(url)

        # Check if content is sufficient
        if result['content'] and len(result['content']) > self.min_content_length:
            print(f"  ✓ Content fetched successfully with newspaper3k")
            return result

        # If content is too short, try Selenium
        print(f"  ⚠ Content too short ({len(result['content'])} chars), trying Selenium...")
        selenium_result = self._fetch_with_selenium(url)

        # Use Selenium result if it's better
        if selenium_result and len(selenium_result.get('content', '')) > len(result['content']):
            print(f"  ✓ Better content fetched with Selenium ({len(selenium_result['content'])} chars)")
            return selenium_result

        # Return original result if Selenium didn't help
        return result

    def _fetch_with_newspaper(self, url):
        """Standard newspaper3k fetch."""
        try:
            article = Article(url)
            article.download()
            article.parse()

            return {
                'content': article.text,
                'metadata': {
                    'url': url,
                    'title': article.title,
                    'authors': article.authors,
                    'publish_date': article.publish_date,
                    'top_image': article.top_image,
                },
                'images': list(article.images)
            }
        except Exception as e:
            print(f"  Newspaper3k error: {e}")
            return self._basic_fetch(url)

    def _fetch_with_selenium(self, url):
        """Fetch with Selenium for JavaScript-rendered content."""
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)

            try:
                # Load page
                driver.get(url)

                # Wait for content to load
                time.sleep(3)  # Basic wait

                # Try to wait for specific content elements
                wait = WebDriverWait(driver, 10)

                # Common content selectors to wait for
                content_selectors = [
                    'article', 'main', '[role="main"]',
                    '.content', '.post-content', '.article-content'
                ]

                for selector in content_selectors:
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        break
                    except:
                        continue

                # Get page source
                page_source = driver.page_source

                # Parse with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')

                # Extract content
                content = self._extract_content_from_soup(soup)

                # Extract metadata
                title = driver.title

                # Get images
                images = [img.get_attribute('src') for img in driver.find_elements(By.TAG_NAME, 'img')]
                images = [img for img in images if img]  # Filter None values

                return {
                    'content': content,
                    'metadata': {
                        'url': url,
                        'title': title,
                        'authors': [],
                        'publish_date': None,
                        'top_image': images[0] if images else None,
                    },
                    'images': images
                }

            finally:
                driver.quit()

        except Exception as e:
            print(f"  Selenium error: {e}")
            return None

    def _extract_content_from_soup(self, soup):
        """Extract main content from BeautifulSoup object."""

        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()

        # Try various content selectors
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.article-content',
            '#content',
            '.prose'  # Common in modern frameworks
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:  # Minimum content threshold
                    return text

        # Fallback: get all paragraphs
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        return content

    def _basic_fetch(self, url):
        """Basic fetch with requests and BeautifulSoup."""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.text, 'html.parser')

            content = self._extract_content_from_soup(soup)
            title = soup.find('title')
            title_text = title.text if title else 'Untitled'

            images = [img.get('src', '') for img in soup.find_all('img') if img.get('src')]

            return {
                'content': content,
                'metadata': {
                    'url': url,
                    'title': title_text,
                    'authors': [],
                    'publish_date': None,
                    'top_image': images[0] if images else None
                },
                'images': images
            }
        except Exception as e:
            print(f"  Basic fetch error: {e}")
            return {
                'content': '',
                'metadata': {'url': url, 'title': 'Error', 'authors': [], 'publish_date': None, 'top_image': None},
                'images': []
            }


# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python content_fetcher_enhanced.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    fetcher = EnhancedContentFetcher()
    result = fetcher.fetch(url)

    print(f"\nTitle: {result['metadata']['title']}")
    print(f"Content length: {len(result['content'])} chars")
    print(f"Images found: {len(result['images'])}")
    print(f"\nFirst 500 chars of content:")
    print(result['content'][:500])