"""News feed."""
from dataclasses import dataclass, field
@dataclass
class NewsDesk:
    articles:list[str]=field(default_factory=list)
    def add(self,text:str): self.articles.insert(0,text); self.articles=self.articles[:50]
