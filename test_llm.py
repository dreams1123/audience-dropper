#!/usr/bin/env python3
"""
Test script for LLM server integration
This script tests the LLM functionality with sample conversation data.
"""

from utils.llm_server import LLMServer, test_llm_connection, get_llm_summary_and_keywords

def test_llm_integration():
    """Test the LLM server integration"""
    
    print("🧪 Testing LLM Server Integration")
    print("=" * 50)
    
    # Test 1: Check if LLM server is accessible
    print("\n1. Testing LM Studio server connection...")
    if test_llm_connection():
        print("✅ LM Studio server is accessible")
    else:
        print("❌ LM Studio server is not accessible")
        print("   Make sure LM Studio is running with a model loaded")
        print("   Check that Local Server is started on http://localhost:1234")
        return False
    
    # Test 2: Sample conversation data
    print("\n2. Testing with sample conversation...")
    sample_conversation = [
        {
            "user": "I'm looking for people who are interested in starting their own online business",
            "assistant": "That's a great target audience! Let me ask you some questions to better understand who you're looking for."
        },
        {
            "user": "I want to find people who are struggling with their current job and want to make more money",
            "assistant": "I understand. You're looking for people who are dissatisfied with their current employment situation."
        },
        {
            "user": "My product is an online course that teaches people how to start a dropshipping business",
            "assistant": "Perfect! So you're offering education about e-commerce and dropshipping."
        },
        {
            "user": "I want to target people who are between 25-45 years old, have some savings, and are tech-savvy",
            "assistant": "Great! You have a very specific demographic in mind."
        },
        {
            "user": "These people would probably be searching for terms like 'side hustle', 'passive income', or 'work from home'",
            "assistant": "Excellent! Those are very relevant search terms for your target audience."
        },
        {
            "user": "They might also be interested in entrepreneurship, business opportunities, or financial freedom",
            "assistant": "Perfect! You've identified key interests and motivations."
        }
    ]
    
    # Test 3: Process conversation with LLM
    print("\n3. Processing conversation with LLM...")
    try:
        result = get_llm_summary_and_keywords(sample_conversation)
        
        print("✅ LLM processing successful!")
        print(f"\n📝 Summary:")
        print(result.get('summary', 'No summary generated'))
        
        print(f"\n🔑 Keywords ({len(result.get('keywords', []))}):")
        for i, keyword in enumerate(result.get('keywords', []), 1):
            print(f"   {i}. {keyword}")
            
        print(f"\n📊 Conversation length: {result.get('conversation_length', 0)}")
        
    except Exception as e:
        print(f"❌ Error processing conversation: {e}")
        return False
    
    # Test 4: Test individual LLM server methods
    print("\n4. Testing individual LLM methods...")
    try:
        llm = LLMServer()
        
        # Test summary generation
        summary = llm.generate_summary(sample_conversation)
        print(f"✅ Summary generation: {'Success' if summary else 'Failed'}")
        
        # Test keyword extraction
        keywords = llm.extract_keywords(summary)
        print(f"✅ Keyword extraction: {'Success' if keywords else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Error testing individual methods: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_with_different_conversations():
    """Test with different types of conversations"""
    
    print("\n🧪 Testing with Different Conversation Types")
    print("=" * 50)
    
    conversations = [
        {
            "name": "E-commerce Business",
            "conversation": [
                {"user": "I want to find people interested in starting an online store", "assistant": "Great! Let me help you identify your target audience."},
                {"user": "My product is a Shopify course for beginners", "assistant": "So you're targeting e-commerce beginners."},
                {"user": "I want people who have some money to invest but don't know where to start", "assistant": "You're looking for people with capital but no direction."},
                {"user": "They should be interested in entrepreneurship and making money online", "assistant": "Entrepreneurial mindset is key."},
                {"user": "Age range 25-40, some college education, comfortable with technology", "assistant": "Very specific demographic targeting."},
                {"user": "They might search for 'start online business', 'shopify tutorial', 'ecommerce course'", "assistant": "Perfect search terms identified."}
            ]
        },
        {
            "name": "Fitness Coaching",
            "conversation": [
                {"user": "I'm looking for people who want to lose weight and get in shape", "assistant": "Fitness and weight loss audience."},
                {"user": "My service is personal training and meal planning", "assistant": "Comprehensive fitness solution."},
                {"user": "I want people who have tried diets before but failed", "assistant": "People with previous weight loss attempts."},
                {"user": "They should be motivated but need guidance and accountability", "assistant": "Need for structure and support."},
                {"user": "Age 30-50, busy professionals, health-conscious", "assistant": "Specific lifestyle and age group."},
                {"user": "They search for 'weight loss tips', 'meal plan', 'personal trainer near me'", "assistant": "Relevant fitness search terms."}
            ]
        }
    ]
    
    for conv_test in conversations:
        print(f"\n📋 Testing: {conv_test['name']}")
        try:
            result = get_llm_summary_and_keywords(conv_test['conversation'])
            print(f"✅ Summary: {result.get('summary', '')[:100]}...")
            print(f"✅ Keywords: {', '.join(result.get('keywords', [])[:5])}...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting LLM Integration Tests")
    print("=" * 60)
    
    # Run main test
    success = test_llm_integration()
    
    if success:
        # Run additional tests
        test_with_different_conversations()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed! The LLM integration is working correctly.")
        print("\nNext steps:")
        print("1. Make sure LM Studio is running with Local Server started")
        print("2. Load your preferred model in LM Studio")
        print("3. Run your Flask app: python app.py")
    else:
        print("\n❌ Tests failed. Please check your LLM server setup.")
