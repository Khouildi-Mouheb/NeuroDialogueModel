# Import Migration Guide

## All Import Changes

### Domain Entities

```python
# OLD ❌
from core.domain.userQuery import UserQuery
from core.domain.rewrittenQuery import RewrittenQuery
from core.domain.response import Response
from core.domain.agent import Agent

# NEW ✅
from domain.entities.user_query import UserQuery
from domain.entities.rewritten_query import RewrittenQuery
from domain.entities.response import Response
```

### Domain Value Objects

```python
# OLD ❌
from analysis.domain.emotionResult import EmotionResult
from analysis.domain.intentAndNeedsResult import IntentAndNeedsResult
from analysis.domain.userState import UserState

# NEW ✅
from domain.value_objects.emotion_result import EmotionResult
from domain.value_objects.intent_and_needs_result import IntentAndNeedsResult
from domain.value_objects.user_state import UserState
```

### Domain Context

```python
# OLD ❌
from core.context.generatorContext import GeneratorContext
from core.context.context import Context
from core.context.retrieverContext import RetieverContext

# NEW ✅
from domain.context.generator_context import GeneratorContext
from domain.context.context import Context
```

### LLM/Generation Adapters

```python
# OLD ❌
from generation.agents.cloudBasedGenerator import CloudBasedGenerator
from generation.agents.localBasedGenerator import LocalBasedGenerator
from generation.agents.generatorAgent import GeneratorAgent

# NEW ✅
from adapters.generation.cloud_based_generator import CloudBasedGenerator
from adapters.generation.local_based_generator import LocalBasedGenerator
from ports.llm_port import LLMPort
```

### Analysis Adapters

```python
# OLD ❌
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent

# NEW ✅
from adapters.analysis.emotion_detection_adapter import EmotionDetectionAdapter
from adapters.analysis.intent_and_needs_adapter import IntentAndNeedsAdapter
from ports.emotion_port import EmotionPort
from ports.intent_port import IntentPort
```

### Verification Adapters

```python
# OLD ❌
from verification.agents.safetyVerificator import SafetyVerificator
from verification.agents.empathyVerificator import EmpathyVerificator
from verification.agents.appropriatenessVerificator import AppropriatenessVerificator
from verification.agents.verificatorAgent import VerificatorAgent
from verification.strategies.mlVerificationStrategy import MLVerificationStrategy
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationStatus import VerificationStatus
from verification.domain.verificationIssue import VerificationIssue
from verification.config.verificationConfig import VerificationConfig

# NEW ✅
from adapters.verification.safety_verificator_adapter import SafetyVerificatorAdapter
from adapters.verification.empathy_verificator_adapter import EmpathyVerificatorAdapter
from adapters.verification.appropriateness_verificator_adapter import AppropriatenessVerificatorAdapter
from adapters.verification.ml_verification_strategy_adapter import MLVerificationStrategyAdapter
from adapters.verification.verification_models import VerificationResult, VerificationStatus, VerificationIssue
from adapters.verification.config.verification_config import VerificationConfig
from ports.verification_port import VerificationPort
from ports.verification_strategy_port import VerificationStrategyPort
```

### Application/Orchestration

```python
# OLD ❌
from orchestration.chat_orchestrator import ChatOrchestrator
from orchestration.config.orchestratorConfig import OrchestratorConfig
from app.chatService import ChatService

# NEW ✅
from application.chat_orchestrator import ChatOrchestrator
from application.orchestration_config import OrchestratorConfig
from presentation.chat import ChatService  # or ChatService in application
```

### Presentation/Main

```python
# OLD ❌
from generation.agents.cloudBasedGenerator import CloudBasedGenerator
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent
from verification.agents.safetyVerificator import SafetyVerificator
from verification.agents.empathyVerificator import EmpathyVerificator
from verification.agents.appropriatenessVerificator import AppropriatenessVerificator
from verification.strategies.mlVerificationStrategy import MLVerificationStrategy
from verification.config.verificationConfig import VerificationConfig
from app.chatService import ChatService

# NEW ✅
from adapters.generation.cloud_based_generator import CloudBasedGenerator
from adapters.analysis.emotion_detection_adapter import EmotionDetectionAdapter
from adapters.analysis.intent_and_needs_adapter import IntentAndNeedsAdapter
from adapters.verification.safety_verificator_adapter import SafetyVerificatorAdapter
from adapters.verification.empathy_verificator_adapter import EmpathyVerificatorAdapter
from adapters.verification.appropriateness_verificator_adapter import AppropriatenessVerificatorAdapter
from adapters.verification.ml_verification_strategy_adapter import MLVerificationStrategyAdapter
from adapters.verification.config.verification_config import VerificationConfig
from application.chat_orchestrator import ChatOrchestrator
```

## Import Rules by Layer

### DOMAIN LAYER (domain/)
Can import from:
- ✅ Domain entities, value objects, context
- ✅ Python standard library
- ✅ Pure utility libraries (no ML, no DB)

Cannot import from:
- ❌ ports
- ❌ adapters
- ❌ application
- ❌ presentation
- ❌ External frameworks

### PORTS LAYER (ports/)
Can import from:
- ✅ abc (abstract base classes)
- ✅ typing

Cannot import from:
- ❌ domain
- ❌ adapters
- ❌ application
- ❌ presentation
- ❌ Any external library

### ADAPTERS LAYER (adapters/)
Can import from:
- ✅ domain (entities, value objects)
- ✅ ports (interfaces to implement)
- ✅ External libraries (groq, transformers, chromadb, etc.)
- ✅ Python standard library

Cannot import from:
- ❌ application
- ❌ presentation

### APPLICATION LAYER (application/)
Can import from:
- ✅ domain (entities, value objects, context)
- ✅ ports (interfaces only, no implementations)
- ✅ Python standard library

Cannot import from:
- ❌ adapters (use ports instead!)
- ❌ presentation

### PRESENTATION LAYER (presentation/)
Can import from:
- ✅ application (orchestrators)
- ✅ adapters (concrete implementations to wire)
- ✅ External frameworks (fastapi, etc.)
- ✅ Python standard library

Cannot import from:
- ❌ Domain with business logic mixed in

## Finding and Replacing Imports

### Using find and replace in your IDE:

1. **Domain imports:**
   - `from core.domain.userQuery` → `from domain.entities.user_query`
   - `from core.domain.` → `from domain.entities.`
   - `from analysis.domain.` → `from domain.value_objects.`
   - `from core.context.` → `from domain.context.`

2. **Adapter imports:**
   - `from generation.agents.` → `from adapters.generation.`
   - `from analysis.agents.` → `from adapters.analysis.`
   - `from verification.agents.` → `from adapters.verification.`
   - `from verification.strategies.` → `from adapters.verification.`
   - `from verification.domain.` → `from adapters.verification.verification_models`
   - `from verification.config.` → `from adapters.verification.config.`

3. **Application imports:**
   - `from orchestration.` → `from application.`
   - `from app.chatService` → `from presentation.chat` or `from application.`

4. **Port imports (NEW):**
   - Add where adapters/application need interfaces
   - `from ports.llm_port import LLMPort`
   - `from ports.emotion_port import EmotionPort`

## Migration Checklist

- [ ] Update main.py entry point
- [ ] Update all test files
- [ ] Update chat.py presentation layer
- [ ] Update local_chat.py
- [ ] Update any other Python files in project
- [ ] Verify all imports work with Python import test
- [ ] Delete old files (app/, core/, generation/, etc.) after verification
- [ ] Update project documentation

## Verification Commands

```bash
# Test domain imports
python -c "from domain.entities.user_query import UserQuery; print('✓')"

# Test port imports
python -c "from ports.llm_port import LLMPort; print('✓')"

# Test application imports
python -c "from application.chat_orchestrator import ChatOrchestrator; print('✓')"

# Test main presentation
python presentation/main.py  # Will fail without GROQ_API_KEY but imports will work
```

## Common Migration Mistakes

### ❌ WRONG - Importing adapters in application
```python
from application.chat_orchestrator import ChatOrchestrator
from adapters.generation.cloud_based_generator import CloudBasedGenerator  # ❌ Wrong location

class MyClass:
    def __init__(self):
        self.orchestrator = ChatOrchestrator(
            llm_port=CloudBasedGenerator()  # ❌ Should pass to presentation, not here
        )
```

### ✅ RIGHT - Using ports in application
```python
from application.chat_orchestrator import ChatOrchestrator
from ports.llm_port import LLMPort  # ✅ Use port interface

class MyClass:
    def __init__(self, llm_port: LLMPort):
        self.orchestrator = ChatOrchestrator(
            llm_port=llm_port  # ✅ Receive as dependency
        )
```

### ❌ WRONG - Domain importing adapters
```python
from domain.entities.user_query import UserQuery
from adapters.generation.cloud_based_generator import CloudBasedGenerator  # ❌ No!

class MyService:
    def process(self):
        gen = CloudBasedGenerator()  # ❌ Domain should never instantiate adapters
```

### ✅ RIGHT - Domain stays pure
```python
from domain.entities.user_query import UserQuery
from domain.value_objects.user_state import UserState

class MyService:
    def create_user_state(self, emotions, intents):
        return UserState(emotions, intents)  # ✅ Only domain logic
```

---

**All imports follow the strict hexagonal architecture pattern!**
