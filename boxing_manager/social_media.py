"""Social media feed."""
from dataclasses import dataclass, field
import random
@dataclass
class SocialFeed:
    posts:list[str]=field(default_factory=list)
    def react(self,result):
        base=random.choice(["Fans are debating", "Boxing Twitter explodes over", "Memes are flying after"])
        self.posts.insert(0,f"{base} {result.method}: {result.winner or 'nobody'} leaves with the headline."); self.posts=self.posts[:50]
