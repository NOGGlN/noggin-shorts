# 50 puzzles: 17 "how many holes", 17 "what is this" silhouettes, 16 "odd one out"

HOLES = [
    # (kind, payload, title hint)  - answer is computed automatically from the drawing
    ("text", "B"),
    ("button", 4),
    ("text", "BOOK"),
    ("text", "1986"),
    ("donut", None),
    ("text", "HELLO"),
    ("text", "ABBA"),
    ("cheese", None),
    ("text", "888"),
    ("glasses", None),
    ("text", "QUIZ"),
    ("text", "2026"),
    ("pegboard", (4, 3)),
    ("text", "ROBOT"),
    ("text", "PAPA"),
    ("button", 2),
    ("text", "GOOD\nBOOK"),
]

SILHOUETTES = [
    # (emoji, answer, [distractors])
    ("🦒", "Giraffe", ["Camel", "Horse", "Llama"]),
    ("✂️", "Scissors", ["Pliers", "Glasses", "Tongs"]),
    ("🐘", "Elephant", ["Rhino", "Hippo", "Bear"]),
    ("🚲", "Bicycle", ["Motorbike", "Scooter", "Wheelchair"]),
    ("☂️", "Umbrella", ["Mushroom", "Lamp", "Jellyfish"]),
    ("🐙", "Octopus", ["Squid", "Jellyfish", "Spider"]),
    ("🦕", "Dinosaur", ["Giraffe", "Dragon", "Lizard"]),
    ("🍍", "Pineapple", ["Carrot", "Palm Tree", "Strawberry"]),
    ("🐇", "Rabbit", ["Kangaroo", "Cat", "Mouse"]),
    ("🦀", "Crab", ["Spider", "Lobster", "Scorpion"]),
    ("🚁", "Helicopter", ["Airplane", "Drone", "Submarine"]),
    ("🦩", "Flamingo", ["Swan", "Heron", "Ostrich"]),
    ("🐌", "Snail", ["Turtle", "Hedgehog", "Slug"]),
    ("🔑", "Key", ["Spoon", "Wrench", "Lock"]),
    ("🐢", "Turtle", ["Frog", "Crab", "Armadillo"]),
    ("🦋", "Butterfly", ["Bat", "Bird", "Flower"]),
    ("🎸", "Guitar", ["Violin", "Banjo", "Tennis Racket"]),
]

ODD = [
    # ([(emoji, name) x4], index of odd one, reason)
    ([("🍎", "Apple"), ("🍌", "Banana"), ("🥕", "Carrot"), ("🍇", "Grapes")], 2, "Carrot is a vegetable!"),
    ([("🐶", "Dog"), ("🐱", "Cat"), ("🐟", "Fish"), ("🐰", "Rabbit")], 2, "Fish isn't a mammal!"),
    ([("🚗", "Car"), ("🚌", "Bus"), ("✈️", "Plane"), ("🚲", "Bike")], 2, "Plane is the only one that flies!"),
    ([("⚽", "Football"), ("🏀", "Basketball"), ("🎲", "Dice"), ("🎾", "Tennis Ball")], 2, "Dice isn't a ball!"),
    ([("🐧", "Penguin"), ("🦅", "Eagle"), ("🦉", "Owl"), ("🐬", "Dolphin")], 3, "Dolphin isn't a bird!"),
    ([("🌞", "Sun"), ("🌳", "Tree"), ("🌙", "Moon"), ("⭐", "Star")], 1, "Tree isn't in the sky!"),
    ([("🎸", "Guitar"), ("🎹", "Piano"), ("📚", "Books"), ("🥁", "Drum")], 2, "Books aren't an instrument!"),
    ([("🍕", "Pizza"), ("🧦", "Sock"), ("🍔", "Burger"), ("🌭", "Hot Dog")], 1, "You can't eat a sock!"),
    ([("🦁", "Lion"), ("🐯", "Tiger"), ("🐘", "Elephant"), ("🐆", "Leopard")], 2, "Elephant isn't a big cat!"),
    ([("🌹", "Rose"), ("🌻", "Sunflower"), ("🌷", "Tulip"), ("🍁", "Leaf")], 3, "Leaf isn't a flower!"),
    ([("✏️", "Pencil"), ("🥄", "Spoon"), ("🖍️", "Crayon"), ("🖊️", "Pen")], 1, "You can't write with a spoon!"),
    ([("🐝", "Bee"), ("🦋", "Butterfly"), ("🐞", "Ladybug"), ("🐍", "Snake")], 3, "Snake isn't an insect!"),
    ([("☕", "Coffee"), ("🔥", "Fire"), ("🧊", "Ice"), ("🌶️", "Chili")], 2, "Ice is the only cold one!"),
    ([("🦈", "Shark"), ("🐪", "Camel"), ("🐙", "Octopus"), ("🐠", "Fish")], 1, "Camel doesn't live in the sea!"),
    ([("👟", "Sneaker"), ("👢", "Boot"), ("👠", "Heel"), ("🧤", "Gloves")], 3, "Gloves aren't worn on your feet!"),
    ([("🍋", "Lemon"), ("🍆", "Eggplant"), ("🌽", "Corn"), ("🍌", "Banana")], 1, "Eggplant isn't yellow!"),
]
