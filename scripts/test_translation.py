#!/usr/bin/env python3
"""
Test script for translation system
Tests individual components before running the full pipeline
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are set correctly."""
    print("🔍 Testing environment variables...")

    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    if not api_key or api_key == 'sk-...':
        print("❌ OPENAI_API_KEY not set or using example value")
        print("   Please edit .env file and add your actual API key")
        return False

    print(f"✅ API Key: {'*' * 20}{api_key[-4:]}")
    print(f"✅ Base URL: {base_url}")
    print(f"✅ Model: {model}")
    return True

def test_prompt_files():
    """Test if prompt files exist and are readable."""
    print("\n🔍 Testing prompt files...")

    prompts_dir = Path('prompts')
    if not prompts_dir.exists():
        print(f"❌ Prompts directory not found: {prompts_dir}")
        return False

    required_files = ['system.txt', 'translation.txt']
    for file in required_files:
        filepath = prompts_dir / file
        if not filepath.exists():
            print(f"❌ Missing prompt file: {filepath}")
            return False

        # Check if file is not empty
        content = filepath.read_text()
        if not content.strip():
            print(f"❌ Empty prompt file: {filepath}")
            return False

        print(f"✅ {file}: {len(content)} characters")

    return True

def test_imports():
    """Test if all required libraries are installed."""
    print("\n🔍 Testing required libraries...")

    libraries = [
        ('newspaper', 'newspaper3k'),
        ('openai', 'openai'),
        ('slugify', 'python-slugify'),
        ('PIL', 'Pillow'),
        ('prompt_manager', 'local module'),
    ]

    all_ok = True
    for module_name, package_name in libraries:
        try:
            if module_name == 'prompt_manager':
                from prompt_manager import PromptManager
            else:
                __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - run: pip install {package_name}")
            all_ok = False

    return all_ok

def test_content_fetcher():
    """Test the content fetcher with a simple URL."""
    print("\n🔍 Testing content fetcher...")

    try:
        from translate_blog import ContentFetcher

        # Test with a simple, reliable URL
        fetcher = ContentFetcher()
        test_url = "https://example.com"

        print(f"   Fetching: {test_url}")
        result = fetcher.fetch(test_url)

        if result['content']:
            print(f"✅ Content fetched: {len(result['content'])} characters")
            print(f"✅ Title: {result['metadata']['title']}")
            return True
        else:
            print("❌ No content fetched")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection with a simple request."""
    print("\n🔍 Testing OpenAI API connection...")

    try:
        from openai import OpenAI

        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        if not api_key or api_key == 'sk-...':
            print("❌ Valid API key required for this test")
            return False

        client = OpenAI(api_key=api_key, base_url=base_url)

        # Simple test message
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API connection successful' in Korean."}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        return True

    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Translation System Test Suite")
    print("=" * 60)

    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Prompt Files", test_prompt_files),
        ("Content Fetcher", test_content_fetcher),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"❌ Test '{name}' failed with error: {e}")
            results.append((name, False))

    # Optional: Test API connection if environment is set up
    if all(r[1] for r in results):
        print("\n" + "=" * 60)
        print("All basic tests passed! Testing API connection...")
        print("=" * 60)
        api_test = test_openai_connection()
        results.append(("OpenAI API", api_test))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All tests passed! You can now run:")
        print("   python3 translate_blog.py <URL>")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())