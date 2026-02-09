import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain.userQuery import UserQuery
from core.domain.userState import UserState
from core.context.generatorContext import GeneratorContext
from generation.agents.cloudBasedGenerator import CloudBasedGenerator
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent


from verification.agents.safetyVerificator import SafetyVerificator
from verification.agents.appropriatenessVerificator import AppropriatenessVerificator
from verification.agents.empathyVerificator import EmpathyVerificator
from verification.strategies.mlVerificationStrategy import MLVerificationStrategy
from verification.config.verificationConfig import VerificationConfig


generator = CloudBasedGenerator()
emotionsDetector = EmotionDetectionAgent()
intentAndNeedsDetector = IntentNeedsAgent()
    
verification_config = VerificationConfig(
        safety_threshold=0.8,
        empathy_threshold=0.6,
        appropriateness_threshold=0.7,
        enable_fallback=True
    )
    
verificators = [
        SafetyVerificator(threshold=verification_config.safety_threshold),
        EmpathyVerificator(threshold=verification_config.empathy_threshold),
        AppropriatenessVerificator(threshold=verification_config.appropriateness_threshold)
    ]
    
verification_strategy = MLVerificationStrategy(
        score_weights=verification_config.score_weights,
        enable_fallback=verification_config.enable_fallback
    )

def test_all_functionality():
    print("\n" + "="*80)
    
    # Initialize all components
    print("\n Initializing all components...")
    
   
    
    print("\n All components initialized!")
    
    # Get user input
    print("\n" + "─" * 80)
    user_input = input("text to analyze: ").strip()
    
    if not user_input:
        print("No input provided. Using default example...")
        user_input = "I'm feeling very anxious about my exam tomorrow."
    
    # Create UserQuery object
    user_query = UserQuery(text=user_input)
    
    print(f"Analyzing: '{user_input}'")
    print("─" * 80)
    
    # ============================================
    # STEP 1: EMOTION DETECTION
    # ============================================
    print("\n STEP 1: EMOTION DETECTION")
    print("─" * 40)
    
    emotions_result = emotionsDetector.detect_emotions(text=user_query.text)
    print(f"  Primary Emotion: {emotions_result.emotions}")
    print(f"  Emotion Scores: {emotions_result.emotionsWithScore}")
    
    # ============================================
    # STEP 2: INTENT AND NEEDS ANALYSIS
    # ============================================
    print("\n STEP 2: INTENT AND NEEDS ANALYSIS")
    print("─" * 40)
    
    intent_result = intentAndNeedsDetector.analyze(text=user_query.text)
    print(f"  All Intents and Xeeds: {intent_result.result}")
    
    # ============================================
    # STEP 3: CREATE USER STATE
    # ============================================
    print("\n STEP 3: USER STATE CREATION")
    print("─" * 40)
    
    userState = UserState(
        emotions=emotions_result,
        intentsAndNeeds=intent_result,
    )
    print(f"  User State created successfully")
    print(f"   - Emotions: {userState.emotions}")
    print(f"   - Primary Intent: {userState.intentsAndNeeds}")
    
    # ============================================
    # STEP 4: GENERATE CONTEXT
    # ============================================
    print("\n STEP 4: CONTEXT GENERATION")
    print("─" * 40)
    
    generatorContext = GeneratorContext(
        user_query=user_query,
        user_state=userState,
    )
    prompt = generatorContext.format_context_for_prompt()
    
    print("  Context generated successfully")
    print(f"  Prompt Preview: {prompt[:150]}...")
    
    # ============================================
    # STEP 5A: ORIGINAL CHAT (No Verification)
    # ============================================
    print("\n STEP 5A: ORIGINAL CHAT GENERATION (No Verification)")
    print("─" * 40)
    print("Generating response without verification...")
    
    def original_chat():
        context = GeneratorContext(user_query=user_query, user_state=userState)
        prompt = context.format_context_for_prompt()
        
        try:
            for chunk in generator.stream(prompt=prompt):
                yield chunk
        except Exception as e:
            yield f"[ERROR] {str(e)}"
    
    # Collect original response
    original_response = ""
    print("\n Chatbot Response (Original):")
    print("─" * 40)
    for chunk in original_chat():
        original_response += chunk
        print(chunk, end="", flush=True)
    print("\n" + "─" * 40)
    print(f" Response length: {len(original_response)} characters")
    
    # ============================================
    # STEP 5B: CHAT WITH VERIFICATION
    # ============================================
    print("\n   STEP 5B: CHAT WITH VERIFICATION")
    print("─" * 40)
    print("Generating and verifying response...")
    
    # Generate fresh response for verification
    generatorContext2 = GeneratorContext(
        user_query=user_query,
        user_state=userState,
    )
    prompt2 = generatorContext2.format_context_for_prompt()
    
    full_response = ""
    try:
        for chunk in generator.stream(prompt=prompt2):
            full_response += chunk
    except Exception as e:
        full_response = f"[ERROR] {str(e)}"
    
    print(f"\n  Generated Response for Verification:")
    print(f"   '{full_response[:100]}...'")
    
    # ============================================
    # STEP 6: VERIFICATION PROCESS
    # ============================================
    print("\n  STEP 6: VERIFICATION PROCESS")
    print("─" * 40)
    
    verification_result = verification_strategy.execute(
        verificators=verificators,
        response=full_response,
        query=user_query.text,
        user_state=userState
    )
    
    print("\n  VERIFICATION RESULTS:")
    print("─" * 40)
    print(f"  Overall Status: {verification_result.status.value}")
    print(f"  Overall Score: {verification_result.overall_score:.2f}/1.0")
    print(f"  Is Approved: {verification_result.is_approved}")
    
    print("\n  Individual Verificator Scores:")
    print("─" * 40)
    for verificator_name, score in verification_result.scores.items():
        status_symbol = " " if score >= 0.7 else " " if score >= 0.5 else "❌"
        print(f"   {status_symbol} {verificator_name}: {score:.2f}")
    
    if verification_result.issues:
        print("\n   Issues Detected:")
        print("─" * 40)
        for issue in verification_result.issues:
            print(f"   • {issue.value}")
    
    if verification_result.recommendations:
        print("\n  Recommendations:")
        print("─" * 40)
        for rec in verification_result.recommendations:
            print(f"   • {rec}")
    
    # ============================================
    # STEP 7: FINAL RESPONSE
    # ============================================
    print("\n  STEP 7: FINAL RESPONSE")
    print("─" * 40)
    
    if verification_result.is_approved:
        print("  Response APPROVED - Using generated response")
        final_response = full_response
    else:
        if verification_result.fallback_response:
            print("   Response REJECTED - Using fallback response")
            final_response = verification_result.fallback_response
        else:
            print("   Response NEEDS REVISION - Using with warning")
            final_response = f"[NEEDS REVISION] {full_response}"
    
    print("\n" + "=" * 80)
    print(" FINAL CHATBOT RESPONSE:")
    print("=" * 80)
    print(final_response)
    print("=" * 80)
    
    # ============================================
    # STEP 8: SUMMARY
    # ============================================
    print("\n TEST SUMMARY")
    print("─" * 40)
    print(f"  Input Text: {user_input[:50]}...")
    print(f" Detected Emotion: {emotions_result.emotionsWithScore}")
    print(f" Detected Intent: {intent_result.result}")
    print(f"  Verification Status: {verification_result.status.value}")
    print(f" Verification Score: {verification_result.overall_score:.2f}/1.0")
    print(f" Final Response Length: {len(final_response)} characters")
    
    # Test individual verificators for comparison
    print("\n" + "=" * 80)
    print("  INDIVIDUAL VERIFICATOR DETAILS")
    print("=" * 80)
    
    for verificator in verificators:
        print(f"\n{verificator.name}:")
        print("─" * 40)
        result = verificator.verify(
            response=full_response,
            query=user_query.text,
            user_state=userState
        )
        print(f"   Status: {result.status.value}")
        print(f"   Score: {result.score:.2f}")
        print(f"   Threshold: {verificator.threshold}")
        if result.issues:
            print(f"   Issues: {[issue.value for issue in result.issues]}")
    
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    # Run the comprehensive test
    test_all_functionality()
    
    # Option to run again
    while True:
        print("\n" + "─" * 80)
        again = input("\n🔄 Test with another input? (y/n): ").strip().lower()
        if again == 'y':
            test_all_functionality()
        else:
            print("\n👋 Thank you for testing! Goodbye!")
            break