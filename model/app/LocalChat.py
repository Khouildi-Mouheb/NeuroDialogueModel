import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain.userQuery import UserQuery
from core.domain.userState import UserState
from core.domain.emotionResult import EmotionResult
from core.context.generatorContext import GeneratorContext
from generation.agents.cloudBasedGenerator import CloudBasedGenerator
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent


generator = CloudBasedGenerator()
emotionsDetector = EmotionDetectionAgent()
intentAndNeedsDetector = IntentNeedsAgent()

def chat(query: UserQuery = None):
    text = query.text
    emotionsResult = emotionsDetector.detect_emotions(text=text)
    intentAndNeedsResult = intentAndNeedsDetector.analyze(text=text)

    userState = UserState(
        emotions=emotionsResult,
        intentsAndNeeds=intentAndNeedsResult,
    )
    generatorContext = GeneratorContext(
        user_query=query,
        user_state=userState,
    )
    prompt = generatorContext.format_context_for_prompt()
    
    # Create a generator function that yields each chunk from the stream
    def generate_response():
        try:
            # The CloudBasedGenerator.stream() method already yields chunks
            for chunk in generator.stream(prompt=prompt):
                yield chunk
        except Exception as e:
            logger.error(f"Error in chat generation: {str(e)}")
            yield f"[ERROR] {str(e)}"
    
    # Return the generator directly (not the method call)
    return generate_response()


if __name__ == "__main__":
    # Test the chat function with a sample query
    print("Testing the chat system...")
    
    # Create a sample user query
    sample_query = UserQuery(text="I'm feeling really anxious about my upcoming exam.")
    
    print(f"User query: {sample_query.text}")
    print("\nGenerating response...")
    print("-" * 50)
    
    # Test the chat function
    response_generator = chat(query=sample_query)
    
    # Print the streaming response
    for chunk in response_generator:
        print(chunk, end="", flush=True)
    
    print("\n" + "-" * 50)
    print("Test completed!")