#!/usr/bin/env python3
"""Test script to verify LLM setup on DGX Spark."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.llm_advanced import AdvancedLLMClient, create_financial_analyst_prompt, get_llm_client


def test_backend_detection():
    """Test 1: Check if LLM backend is available."""
    print("=" * 60)
    print("TEST 1: Backend Detection")
    print("=" * 60)

    try:
        client = AdvancedLLMClient()
        info = client.get_model_info()

        print(f"✓ Backend configured: {info['backend']}")
        print(f"✓ Model: {info['model']}")
        print(f"✓ Base URL: {info['base_url']}")
        print(f"✓ Temperature: {info['temperature']}")
        print(f"✓ Max tokens: {info['max_tokens']}")
        return True
    except Exception as e:
        print(f"✗ Backend detection failed: {e}")
        print("\nPossible solutions:")
        print("1. For NVIDIA NIM: Set NVIDIA_API_KEY in .env file")
        print("2. For Ollama: Install from https://ollama.ai and run 'ollama serve'")
        return False


def test_simple_generation():
    """Test 2: Simple text generation."""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Generation")
    print("=" * 60)

    try:
        client = get_llm_client()
        response = client.generate(
            prompt="Say 'Hello from DGX Spark!' and nothing else.",
            temperature=0.0
        )
        print(f"✓ Generation successful!")
        print(f"Response: {response[:200]}")
        return True
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return False


def test_financial_analysis():
    """Test 3: Financial analysis with system prompt."""
    print("\n" + "=" * 60)
    print("TEST 3: Financial Analysis")
    print("=" * 60)

    try:
        client = get_llm_client()
        system_prompt = create_financial_analyst_prompt(language="en")

        response = client.generate(
            prompt="In one sentence, what is Return on Equity (ROE)?",
            system_prompt=system_prompt,
            temperature=0.1
        )

        print(f"✓ Financial analysis successful!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Financial analysis failed: {e}")
        return False


def test_multilingual():
    """Test 4: Multilingual support (Polish)."""
    print("\n" + "=" * 60)
    print("TEST 4: Multilingual Support (Polish)")
    print("=" * 60)

    try:
        client = get_llm_client()
        system_prompt = create_financial_analyst_prompt(language="pl")

        response = client.generate(
            prompt="Co to jest wskaźnik ROE? Odpowiedz krótko.",
            system_prompt=system_prompt,
            temperature=0.1
        )

        print(f"✓ Polish language support works!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Multilingual test failed: {e}")
        return False


def test_chat_mode():
    """Test 5: Multi-turn chat."""
    print("\n" + "=" * 60)
    print("TEST 5: Multi-turn Chat")
    print("=" * 60)

    try:
        client = get_llm_client()

        messages = [
            {"role": "system", "content": create_financial_analyst_prompt("en")},
            {"role": "user", "content": "What are the main categories of financial ratios?"},
        ]

        response = client.chat(messages)
        print(f"✓ Chat mode successful!")
        print(f"Response: {response[:300]}...")
        return True
    except Exception as e:
        print(f"✗ Chat mode failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 DGX Spark LLM Setup Verification")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Backend Detection", test_backend_detection()))

    if not results[0][1]:
        print("\n" + "=" * 60)
        print("⚠️  Cannot proceed without LLM backend")
        print("=" * 60)
        return

    results.append(("Simple Generation", test_simple_generation()))
    results.append(("Financial Analysis", test_financial_analysis()))
    results.append(("Multilingual Support", test_multilingual()))
    results.append(("Multi-turn Chat", test_chat_mode()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your DGX Spark LLM setup is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app/app.py")
        print("2. Navigate to: 💬 CFO Chat")
        print("3. Upload an XML file and start chatting!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("\nRefer to docs/LLM_SETUP.md for troubleshooting.")


if __name__ == "__main__":
    main()
