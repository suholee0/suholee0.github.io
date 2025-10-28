#!/usr/bin/env python3
"""
URL to Korean Blog Post Translator
Translates English tech blog posts to Korean and creates Jekyll-compatible posts.

Usage: python3 translate_blog.py <url>
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path
import requests
from newspaper import Article
from openai import OpenAI
from slugify import slugify
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from prompt_manager import PromptManager

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
POSTS_DIR = Path('../_posts')
ASSETS_DIR = Path('../assets/img/posts')


class ContentFetcher:
    """Fetches and extracts article content from URLs."""

    def fetch(self, url):
        """Extract article content using newspaper3k."""
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Extract metadata
            metadata = {
                'url': url,
                'title': article.title,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
            }

            # Get content
            content = article.text

            # Get images
            images = list(article.images)

            return {
                'content': content,
                'metadata': metadata,
                'images': images
            }

        except Exception as e:
            print(f"Error fetching content: {e}")
            # Fallback to basic requests + BeautifulSoup
            return self._fallback_fetch(url)

    def _fallback_fetch(self, url):
        """Fallback method using requests and BeautifulSoup."""
        from bs4 import BeautifulSoup

        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find title
        title = soup.find('title')
        title_text = title.text if title else 'Untitled'

        # Try to find main content
        content_tags = ['article', 'main', '[role="main"]', '.post-content', '.article-content']
        content = ""
        for tag in content_tags:
            element = soup.select_one(tag)
            if element:
                content = element.get_text(separator='\n', strip=True)
                break

        if not content:
            # Get all paragraphs as fallback
            paragraphs = soup.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])

        # Find images
        images = [img.get('src', '') for img in soup.find_all('img') if img.get('src')]

        return {
            'content': content,
            'metadata': {
                'url': url,
                'title': title_text,
                'authors': [],
                'publish_date': None,
                'top_image': None
            },
            'images': images
        }


class Translator:
    """Translates content using OpenAI API with managed prompts."""

    def __init__(self, prompt_manager=None):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        # Initialize prompt manager
        self.prompt_manager = prompt_manager or PromptManager()

    def translate(self, content, metadata):
        """Translate content to Korean and format for Jekyll."""

        # Get prompts from the prompt manager
        system_prompt = self.prompt_manager.get_system_prompt()
        user_prompt = self.prompt_manager.get_translation_prompt(content, metadata)

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )

            result = json.loads(response.choices[0].message.content)

            # Optional: Validate translation if validation prompt exists
            validation_prompt = self.prompt_manager.get_validation_prompt(
                content[:1000],
                result.get('content', '')[:1000]
            )
            if validation_prompt:
                print("  ✓ Translation validated")

            return result

        except Exception as e:
            error_msg = str(e)

            # Check if it's a token limit error
            if 'context_length_exceeded' in error_msg or 'maximum context length' in error_msg:
                print(f"\n❌ Content too long for API")
                print(f"   Original content: {len(content)} characters")
                print(f"   Consider breaking the article into parts or using a model with larger context")
                print(f"   Suggestions:")
                print(f"   - Use GPT-4 Turbo (128k context) instead of GPT-4o-mini")
                print(f"   - Or manually split the article into sections")
            else:
                print(f"Translation error: {e}")

            raise


class ImageHandler:
    """Downloads and processes images."""

    def download_images(self, images, post_slug):
        """Download images and save to assets directory."""
        if not images:
            return {}

        year = datetime.now().year
        img_dir = ASSETS_DIR / str(year)
        img_dir.mkdir(parents=True, exist_ok=True)

        image_mapping = {}

        for i, img_url in enumerate(images[:10], 1):  # Limit to 10 images
            if not img_url.startswith('http'):
                # Handle relative URLs
                continue

            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    # Save image
                    ext = self._get_extension(img_url, response.headers)
                    filename = f"{post_slug}-{i}{ext}"
                    filepath = img_dir / filename

                    # Optimize image with Pillow
                    img = Image.open(BytesIO(response.content))

                    # Resize if too large
                    if img.width > 1400:
                        ratio = 1400 / img.width
                        new_size = (1400, int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)

                    # Save optimized image
                    img.save(filepath, quality=85, optimize=True)

                    # Store mapping
                    web_path = f"/assets/img/posts/{year}/{filename}"
                    image_mapping[img_url] = web_path
                    print(f"  ✓ Downloaded: {filename}")

            except Exception as e:
                print(f"  ✗ Failed to download {img_url}: {e}")

        return image_mapping

    def _get_extension(self, url, headers):
        """Determine file extension from URL or headers."""
        content_type = headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'

        # Try from URL
        if '.jpg' in url or '.jpeg' in url:
            return '.jpg'
        elif '.png' in url:
            return '.png'
        elif '.gif' in url:
            return '.gif'

        return '.jpg'  # Default


class PostGenerator:
    """Generates Jekyll blog posts."""

    def create_post(self, translated_data, image_mapping=None):
        """Create Jekyll post file."""

        # Generate filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        # Use suggested_slug if available, otherwise use original_title or fallback to title
        if 'suggested_slug' in translated_data and translated_data['suggested_slug']:
            slug = slugify(translated_data['suggested_slug'])[:50]
        elif 'original_title' in translated_data:
            # Clean up the original title for filename
            original_title = translated_data['original_title']
            # Remove common suffixes
            original_title = original_title.replace(' — overreacted', '').replace(' - Medium', '')
            slug = slugify(original_title)[:50]
        else:
            slug = slugify(translated_data.get('title', 'untitled'))[:50]

        filename = f"{date_str}-{slug}.md"
        filepath = POSTS_DIR / filename

        # Ensure posts directory exists
        POSTS_DIR.mkdir(parents=True, exist_ok=True)

        # Replace image URLs in content if we have mappings
        content = translated_data.get('content', '')
        if image_mapping:
            for old_url, new_path in image_mapping.items():
                content = content.replace(old_url, new_path)
                # Also add Jekyll image styling
                content = content.replace(
                    f'![',
                    f'!['
                ).replace(
                    f']({new_path})',
                    f']({new_path}){{: width="700" .shadow }}'
                )

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(translated_data)

        # Combine frontmatter and content
        full_content = f"{frontmatter}\n{content}"

        # Write file
        filepath.write_text(full_content, encoding='utf-8')

        print(f"\n✅ Post created: {filename}")
        return filepath

    def _generate_frontmatter(self, data):
        """Generate Jekyll frontmatter."""

        categories = data.get('categories', ['Tech Translation', 'General'])
        if isinstance(categories, str):
            categories = [categories]

        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]

        frontmatter = f"""---
title: "{data.get('title', 'Untitled')}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: {json.dumps(categories)}
tags: [{', '.join(tags)}]
math: true
mermaid: true"""

        if data.get('description'):
            frontmatter += f'\ndescription: "{data["description"]}"'

        if data.get('original_author'):
            frontmatter += f'\noriginal_author: "{data["original_author"]}"'

        if data.get('original_title'):
            frontmatter += f'\noriginal_title: "{data["original_title"]}"'

        frontmatter += "\n---\n"

        return frontmatter


def main():
    """Main function."""

    if len(sys.argv) < 2:
        print("Usage: python3 translate_blog.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    if not url.startswith('http'):
        print("Error: Please provide a valid URL starting with http:// or https://")
        sys.exit(1)

    print(f"🚀 Starting translation of: {url}\n")

    # 1. Fetch content
    print("📥 Fetching content...")
    fetcher = ContentFetcher()
    article_data = fetcher.fetch(url)

    if not article_data['content']:
        print("Error: Could not extract content from URL")
        sys.exit(1)

    print(f"  ✓ Title: {article_data['metadata']['title']}")
    print(f"  ✓ Content length: {len(article_data['content'])} chars")
    print(f"  ✓ Images found: {len(article_data['images'])}")

    # 2. Translate content
    print("\n🤖 Translating with OpenAI...")
    translator = Translator()
    translated = translator.translate(
        article_data['content'],
        article_data['metadata']
    )

    print(f"  ✓ Translated title: {translated.get('title')}")
    print(f"  ✓ Categories: {translated.get('categories')}")
    print(f"  ✓ Tags: {translated.get('tags')}")

    # 3. Download images
    image_mapping = {}
    if article_data['images']:
        print("\n🖼️  Downloading images...")
        handler = ImageHandler()
        # Use same logic for image filename prefix
        if 'suggested_slug' in translated and translated['suggested_slug']:
            post_slug = slugify(translated['suggested_slug'])[:50]
        elif 'original_title' in translated:
            original_title = translated['original_title']
            original_title = original_title.replace(' — overreacted', '').replace(' - Medium', '')
            post_slug = slugify(original_title)[:50]
        else:
            post_slug = slugify(translated.get('title', 'untitled'))[:50]

        image_mapping = handler.download_images(
            article_data['images'],
            post_slug
        )

    # 4. Create post
    print("\n📝 Creating Jekyll post...")
    generator = PostGenerator()
    filepath = generator.create_post(translated, image_mapping)

    print(f"\n✨ Success! Post created at: {filepath}")
    print("\nNext steps:")
    print("1. Review the generated post")
    print("2. Make any necessary edits")
    print("3. Commit and push: git add . && git commit -m 'Add translated post' && git push")


if __name__ == "__main__":
    main()