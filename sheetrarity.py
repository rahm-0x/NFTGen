import pandas as pd

def create_rarity_scale_sheet():
    # Define rarity categories and data
    rarity_data = {
        "COMMON": {
            "Total": 2888,
            "Attributes": {
                "Base": ["Brown", "Dark Brown", "Golden Brown"],
                "Clothing": [
                    "Ace Jacket", "Clover Track", "Phantom Track", "Skyline Track",
                    "Crimsonite Shirt", "Dapper Shirt", "Fleur Shirt", "Luminary Shirt",
                    "Luxuria Shirt", "Mulligan Shirt", "Oasis Shirt", "Peacemaker Shirt",
                    "Shroud Shirt", "Strategist Shirt", "Teeoff Shirt", "Thinker Shirt"
                ],
                "Eyes": ["Bored"],
                "Glasses": ["Enigma"],
                "Head": ["Cruise Control"],
                "Mouth": ["Bored", "Bored Unshaved", "Smirk"],
                "Background": ["Gray", "Blue", "Yellow"]
            }
        },
        "UNCOMMON": {
            "Total": 2500,
            "Attributes": {
                "Base": ["Crème", "Tan"],
                "Clothing": [
                    "Brawler Jacket", "Capisce Shirt", "Frostbite Coat", "Glacius Shirt",
                    "Greenside Shirt", "Handler Jacket", "Hustler Jacket", "Insider Jacket",
                    "Mirage Jacket", "Scarlet Suit", "Scholar Shirt", "Soldato Suit",
                    "Trigger Jacket", "Virgil Jacket", "Visionary Jacket", "Waves Shirt",
                    "Wildcat Jacket"
                ],
                "Eyes": ["Closed", "Curious", "Sad", "Shook"],
                "Glasses": ["Specter"],
                "Head": ["Vibe Check"],
                "Mouth": ["Brute", "Drool", "Jawbreaker"],
                "Background": ["Green"]
            }
        },
        "RARE": {
            "Total": 1500,
            "Attributes": {
                "Base": ["Pink", "White", "Red", "Blue"],
                "Clothing": [
                    "Advisor Suit", "Aspen Jacket", "Blackout Fur Jacket", "Brandy Suit",
                    "Bravado Suit", "Capitano Suit", "Empire Suit", "Cardinal Suit",
                    "Chillax Jacket", "Enforcer Jacket", "Mogul Suit", "Noir Shirt",
                    "Onyx Turtleneck", "Overseer Suit", "Philanthropist Suit",
                    "Prodigy Suit", "Prowler Suit", "Riptide Suit", "Sentinel Suit",
                    "Serpent Suit", "Shakedown Suit", "Stryker Suit", "Velora Suit"
                ],
                "Eyes": ["Bloodshot", "Locked In", "Scar", "Hypnotized"],
                "Glasses": ["Abyss", "Echelon", "Grifter"],
                "Head": [
                    "Black Highlife Club", "White Highlife Club", "White MMC",
                    "Snowline", "Nightshade", "Buster", "Wraith"
                ],
                "Mouth": [
                    "Grin", "Grin Unshaved", "Growler", "Stogie", "Picky", "Picky Unshaved",
                    "Slick", "Slick Unshaved"
                ],
                "Background": ["Aquamarine"]
            }
        },
        # Additional rarity levels omitted for brevity (EPIC, LEGENDARY, MYTHIC)...
    }

    # Prepare data for the sheet
    sheet_data = []
    for rarity, details in rarity_data.items():
        total = details["Total"]
        for attribute, values in details["Attributes"].items():
            for value in values:
                sheet_data.append([rarity, total, attribute, value])

    # Create DataFrame
    df = pd.DataFrame(sheet_data, columns=["Rarity", "Total Supply", "Attribute Type", "Attribute Value"])

    # Save to Excel
    output_file = "rarity_scale.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Rarity scale sheet saved as {output_file}")

# Run the script
create_rarity_scale_sheet()