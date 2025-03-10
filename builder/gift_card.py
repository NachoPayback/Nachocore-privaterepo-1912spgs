import os
import sys
import json
import random

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_data_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(get_project_root(), relative_path)

def load_config():
    config_path = get_data_path(os.path.join("builder", "config.json"))
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print("Error loading config: {}".format(e))
        return {}

def save_config(config):
    config_path = get_data_path(os.path.join("builder", "config.json"))
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        print("Config saved successfully.")
    except Exception as e:
        print("Error saving config: {}".format(e))

def load_gift_cards():
    gift_card_path = get_data_path(os.path.join("builder", "data", "gift_cards"))
    gift_cards = {}
    if os.path.exists(gift_card_path):
        for file in os.listdir(gift_card_path):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(gift_card_path, file), "r") as f:
                        data = json.load(f)
                    if isinstance(data, dict) and "name" in data:
                        gift_cards[data["name"]] = data
                    else:
                        print("Skipping {}: Missing or invalid 'name' field.".format(file))
                except Exception as e:
                    print("Error loading {}: {}".format(file, e))
    else:
        print("Gift card folder not found: {}".format(gift_card_path))
    return gift_cards

def generate_random_code(card_data):
    formats = card_data.get("format", "4-4-4-4")
    fmt = random.choice(formats) if isinstance(formats, list) else formats
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
    starts_with_list = card_data.get("starts_with", [])
    if starts_with_list:
        prefix = random.choice(starts_with_list)
        raw_code = generated_code.replace("-", "")
        if len(prefix) <= len(raw_code):
            new_raw = prefix + raw_code[len(prefix):]
            group_lengths = [int(g) for g in groups if g.isdigit()]
            new_code = ""
            idx = 0
            for length in group_lengths:
                new_code += new_raw[idx:idx+length] + "-"
                idx += length
            generated_code = new_code.rstrip("-")
    return generated_code

def generate_random_pin(card_data):
    try:
        pin_length = int(card_data.get("pin_format", "4"))
    except ValueError:
        pin_length = 4
    if card_data.get("pin_required", True) and pin_length > 0:
        return "".join(random.choice("0123456789") for _ in range(pin_length))
    return ""

def update_final_gift_card(selected_name, custom_data=None):
    # If frozen, use the static manifest for gift cards.
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import GIFT_CARD_STATIC
            return GIFT_CARD_STATIC
        except Exception as e:
            print("Error loading static gift card from manifest: {}".format(e))
    config = load_config()
    if selected_name == "Custom Gift Card":
        if custom_data is None:
            custom_data = {"name": "Custom Gift Card", "code": "", "pin": ""}
        config["selected_gift_card"] = custom_data
    else:
        gift_cards = load_gift_cards()
        card_data = gift_cards.get(selected_name)
        if not card_data:
            print("Gift card '{}' not found. Using default parameters.".format(selected_name))
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
    gift_cards = load_gift_cards()
    print("Loaded gift cards:", gift_cards)
    final = update_final_gift_card("Amazon")
    print("Final gift card details:", final)
