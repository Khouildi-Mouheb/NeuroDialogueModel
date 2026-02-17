import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from generation.agents.cloudBasedGenerator import CloudBasedGenerator
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent
from orchestration.chat_orchestrator import ChatOrchestrator
from orchestration.config.orchestratorConfig import OrchestratorConfig


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
    
    # Use the ChatOrchestrator to run the end-to-end flow
    orchestrator_cfg = OrchestratorConfig(
        enable_emotion=True,
        enable_intent=True,
        free_mode=False,
        max_retries=1,
        disabled_tools=[],
    )

    orchestrator = ChatOrchestrator(
        generator=generator,
        emotion_agent=emotionsDetector,
        intent_agent=intentAndNeedsDetector,
        verification_strategy=verification_strategy,
        verificators=verificators,
        config=orchestrator_cfg,
    )

    print(f"Analyzing and generating for: '{user_input}'")
    print("─" * 80)

    results = orchestrator.orchestrate(user_input)

    # Pretty-print results
    print("\nAnalysis:")
    print(f"  Emotions: {results['analysis'].get('emotions')}")
    print(f"  Emotion Scores: {results['analysis'].get('emotion_scores')}")
    print(f"  Intents: {results['analysis'].get('intents')}")

    print("\nVerification:")
    print(f"  Approved: {results['verification'].get('approved')}")
    print(f"  Score: {results['verification'].get('score')}")
    print(f"  Issues: {results['verification'].get('issues')}")

    print("\nFinal Response:\n")
    print(results.get("response"))


if __name__ == "__main__":
    # Run the comprehensive test
    test_all_functionality()
    
    # Option to run again
    while True:
        print("\n" + "─" * 80)
        again = input("\n Test with another input? (y/n): ").strip().lower()
        if again == 'y':
            test_all_functionality()
        else:
            print("\n Thank you for testing! Goodbye!")
            break