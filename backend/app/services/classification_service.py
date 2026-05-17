from app.llm.groq_client import LLMClient
from app.llm.structured_output import ClassificationOutput
from app.observability.trace_logger import TraceLogger

class ClassificationService:
    PROMPT_VERSION = "classification_v1"
    
    @staticmethod
    def classify(trace_id: str, subject: str, body: str) -> ClassificationOutput:
        start_time = TraceLogger.start_timer()
        
        system_prompt = """
        You are an expert customer support triage agent.
        Categorize the incoming ticket based on its subject and body.
        Categories: 'Billing', 'Technical', 'Account', 'General'.
        Provide your confidence as a float between 0.0 and 1.0.
        Provide brief reasoning.
        Respond in JSON.
        """
        user_prompt = f"Subject: {subject}\nBody: {body}"
        
        try:
            output: ClassificationOutput = LLMClient.get_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="llama3-8b-8192",
                response_model=ClassificationOutput
            )
            
            TraceLogger.log_node_execution(
                trace_id=trace_id,
                node_name="classification_service",
                latency_ms=TraceLogger.end_timer(start_time),
                inputs={"subject": subject, "body": body},
                outputs=output.model_dump(),
                prompt_version=ClassificationService.PROMPT_VERSION
            )
            return output
        except Exception as e:
            TraceLogger.log_node_execution(
                trace_id=trace_id,
                node_name="classification_service",
                latency_ms=TraceLogger.end_timer(start_time),
                inputs={"subject": subject, "body": body},
                outputs={},
                failures=str(e),
                prompt_version=ClassificationService.PROMPT_VERSION
            )
            # Fallback output
            return ClassificationOutput(category="General", confidence=0.0, reasoning="Error during classification")
