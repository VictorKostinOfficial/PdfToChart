from abc import ABC, abstractmethod
from typing import Iterable, Any, Optional

import aiofiles
import aiofiles.os


class BaseCollector(ABC):

    @abstractmethod
    async def check_new_files(**kwargs: Any) -> Optional[Iterable[Any]]:
        ...

    @abstractmethod
    async def collect(self, **kwargs: Any) -> Optional[Iterable[Any]]:
        ...

    @abstractmethod
    async def process(self, **kwargs: Any):
        ...
