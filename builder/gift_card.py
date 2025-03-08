import os
import json
import random

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_config():
    """Load builder configuration from builder/config.json."""
    PROJECT_ROOT = get_project_root()
    CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    """Save builder configuration to builder/config.json."""
    PROJECT_ROOT = get_project_root()
    CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        print("Config saved successfully.")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_gift_cards():
    """
    Load all predefined gift card JSON files from builder/data/gift_cards.
    Each file must be valid JSON and contain a "name" key.
    """
    PROJECT_ROOT = get_project_root()
    GIFT_CARD_PATH = os.path.join(PROJECT_ROOT, "builder", "data", "gift_cards")
    gift_cards = {}
    if os.path.exists(GIFT_CARD_PATH):
        for file in os.listdir(GIFT_CARD_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(GIFT_CARD_PATH, file), "r") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "name" in data:
                            gift_cards[data["name"]] = data
                        else:
                            print(f"Skipping {file}: Missing or invalid 'name' field.")
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    return gift_cards

def generate_random_code(card_data):
    """
    Generate a random gift card code based on parameters in card_data.
    Expects card_data to include:
      - "format": a string (e.g., "4-6-4") or list of strings.
      - "char_set": string of allowed characters.
      - Optionally, "starts_with": a list of prefixes to enforce.
    """
    formats = card_data.get("format", "4-4-4-4")
    if isinstance(formats, list):
        fmt = random.choice(formats)
    else:
        fmt = formats
    groups = fmt.split("-")
    char_set = card_data.get("char_set", "ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
    code_parts = []
    for group in groups:
        try:
            count = int(group)
        except ValueError:
            count = 0
        part = "".join(random.choice(char_set) for _ in range(count))
        code_parts.append(part)
    generated_code = "-".join(code_parts)
    # Enforce prefix if "starts_with" is provided.
    starts_with_list = card_data.get("starts_with", [])
    if starts_with_list:
        prefix = random.choice(starts_with_list)
        raw_code = generated_code.replace("-", "")
        if len(prefix) <= len(raw_code):
            new_raw = prefix + raw_code[len(prefix):]
            # Reinsert dashes as per original format.
            group_lengths = [int(g) for g in groups if g.isdigit()]
            new_code = ""
            idx = 0
            for length in group_lengths:
                new_code += new_raw[idx:idx+length] + "-"
                idx += length
            generated_code = new_code.rstrip("-")
    return generated_code

def generate_random_pin(card_data):
    """
    Generate a random PIN using the 'pin_format' and 'pin_required' fields from card_data.
    If pin_required is False or pin_format is 0, return an empty string.
    """
    try:
        pin_length = int(card_data.get("pin_format", "4"))
    except ValueError:
        pin_length = 4
    if card_data.get("pin_required", True) and pin_length > 0:
        return "".join(random.choice("0123456789") for _ in range(pin_length))
    return ""

def update_final_gift_card(selected_name, custom_data=None):
    """
    Updates the builder configuration with the final gift card details.
    If selected_name is "Custom Gift Card", use custom_data (a dict with keys "name", "code", "pin").
    Otherwise, load the corresponding gift card rules from the JSON files,
    generate a final code and PIN, save these details into config.json, and return the final card details.
    """
    config = load_config()
    if selected_name == "Custom Gift Card":
        if custom_data is None:
            custom_data = {"name": "Custom Gift Card", "code": "", "pin": ""}
        config["selected_gift_card"] = custom_data
    else:
        gift_cards = load_gift_cards()
        card_data = gift_cards.get(selected_name)
        if not card_data:
            print(f"Gift card '{selected_name}' not found. Using default parameters.")
            card_data = {
                "format": "4-4-4-4",
                "pin_format": "4",
                "char_set": "ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
                "name": selected_name,
                "pin_required": True
            }
        final_code = generate_random_code(card_data)
        final_pin = generate_random_pin(card_data)
        final_card = {
            "name": selected_name,
            "code": final_code,
            "pin": final_pin,
            "pin_required": (final_pin != "")
        }
        config["selected_gift_card"] = final_card
    save_config(config)
    return config.get("selected_gift_card", {})

if __name__ == "__main__":
    # For testing purposes.
    gift_cards = load_gift_cards()
    print("Loaded gift cards:", gift_cards)
    # Update final gift card for a selected card (e.g., "Amazon").
    final = update_final_gift_card("Amazon")
    print("Final gift card details:", final)
