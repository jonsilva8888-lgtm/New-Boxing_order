"""Sponsor offers."""
from dataclasses import dataclass
@dataclass
class Sponsor:
    category: str; name: str; weekly_pay: int; min_popularity: int
SPONSORS=[Sponsor("Shoes","FleetStep",150,10),Sponsor("Equipment","Ironhide Gloves",300,20),Sponsor("Nutrition","Clean Cut Fuel",650,35),Sponsor("Sportswear","Victory Thread",1500,55),Sponsor("Luxury","Crown & Chrome",5000,80)]
