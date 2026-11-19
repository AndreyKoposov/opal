from abc import abstractmethod
import asyncio
import functools

from app.config import AI_ENGINE, AI_API_KEY, AI_MODEL, AI_TEMP


class AIEngine():
    def __init__(self, max_pool: int = 10) -> None:
        self.semaphore = asyncio.Semaphore(max_pool)

    @abstractmethod
    async def chat(self, query: str) -> str:
        pass

    @staticmethod
    def with_semaphore(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with self.semaphore:
                result = await func(self, *args, **kwargs)
            return result
        return wrapper

    @staticmethod
    def get_engine() -> 'AIEngine':
        match AI_ENGINE:
            case 'GigaChat':
                from . import gigachat
                return gigachat.GigaChatEngine(AI_API_KEY, AI_MODEL, int(AI_TEMP))
            case 'Qwen':
                from . import qwen
                return qwen.QwenEngine(AI_API_KEY, AI_MODEL, int(AI_TEMP))
            case _:
                raise ValueError("Unknown AI engine!")

engine = AIEngine.get_engine()

# Фотолитография — метод получения рисунка на поверхности материала. 
# На подложку наносится фоторезист, который засвечивается через фотошаблон, 
# проявляется, а затем используется для травления или напыления. 
# Фотолитография начинается с нанесения фоторезиста на подложку. 
# Затем происходит засвечивание через фотошаблон, проявление и 
# использование для травления или напыления.
