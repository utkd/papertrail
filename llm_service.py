import os
from openai import OpenAI
from ollama import chat

class LLMService(object):
    def __init__(self, config: dict[str, str]):
        self._config = config

    def call(self, messages: dict[str, str], use_history: bool = False) -> dict[str, str]:
        pass

class OpenAILLM(LLMService):
    def __init__(self, config):
        super().__init__(config)

        openai_key = None
        if config.get('openai_key') is not None:
            openai_key = config['openai_key']
        else:
            openai_key = os.getenv("OPENAI_APIKEY")
        if openai_key is None:
            raise Exception("Open AI key is missing. Provide one above or set it in OPENAI_AIPKEY env variable")

        self._model = 'gpt-4o-mini'
        if config is not None and config.get('model') is not None:
            self._model = config.model

        self._client = OpenAI(api_key=openai_key)

    def call(self, messages: dict[str, str]) -> dict[str, str]:
        response = None
        if messages is not None and len(messages) > 0:
            response = self._client.chat.completions.create(
                messages = messages,
                model = self._model
            )
            return {'output': response.choices[0].message.content}
        return response

# Llama models (7b/8b versions) do not seem to understand the prompt or the task at times
# Don't plan to work on this right now, gpt-4o-mini is doing great
class OllamaLLM(LLMService):
    def __init__(self, config):
        super().__init__(config)

        self._model = 'llama3.2'
    
    def call(self, messages: dict[str, str]) -> dict[str, str]:
        response = None
        if messages is not None and len(messages) > 0:
            response = chat(model=self._model, messages=messages)
            print(response.message)
            return {'output': response.message.content}
        return response


    
if __name__ == "__main__":
    # llm = OpenAILLM({})
    llm = OllamaLLM({})
    output = llm.call(messages=[{"role":"user", "content":"the fox is"}])
    print(output)
    