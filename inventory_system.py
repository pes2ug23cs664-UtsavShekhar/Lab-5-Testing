"""Inventory Management System.
Performs item addition, removal, saving, and loading using JSON files.
Demonstrates clean code, static analysis, and safe I/O practices.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

__version__ = "1.0.3"

# Configure logging early
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

# Global inventory storage (acceptable for this small script)
stock_data: Dict[str, int] = {}


def add_item(item: str = "default", qty: int = 0,
             logs: Optional[List[str]] = None) -> None:
    """Add qty of item to stock_data, with input validation."""
    if not isinstance(item, str) or not item:
        raise TypeError("Item must be a non-empty string.")
    if not isinstance(qty, int):
        raise TypeError("Quantity must be an integer.")
    if qty < 0:
        raise ValueError("Quantity must be non-negative.")

    stock_data[item] = stock_data.get(item, 0) + qty
    if logs is not None:
        logs.append(f"{datetime.now().isoformat()}: Added {qty} of {item}")
    logging.info("Added %d of %s", qty, item)


def remove_item(item: str, qty: int) -> bool:
    """Remove qty of item from stock_data. Return True if successful."""
    if not isinstance(item, str) or not item:
        raise TypeError("Item must be a non-empty string.")
    if not isinstance(qty, int):
        raise TypeError("Quantity must be an integer.")
    if qty < 0:
        raise ValueError("Quantity must be non-negative.")

    if item not in stock_data:
        logging.warning("Item '%s' not found in stock.", item)
        return False

    if qty >= stock_data[item]:
        del stock_data[item]
    else:
        stock_data[item] -= qty
    logging.info("Removed %d of %s", qty, item)
    return True


def get_qty(item: str) -> int:
    """Return quantity of item in stock (0 if missing)."""
    if not isinstance(item, str) or not item:
        raise TypeError("Item must be a non-empty string.")
    return stock_data.get(item, 0)


def load_data(file_path: str = "inventory.json") -> None:
    """Load stock_data from a JSON file (safe, validated)."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.info("File '%s' not found. Starting with empty stock.",
                     file_path)
        return
    except json.JSONDecodeError as err:
        logging.error("Failed to parse JSON: %s", err)
        return
    except OSError as err:
        logging.error("I/O error reading '%s': %s", file_path, err)
        return

    if not isinstance(data, dict):
        logging.error("Invalid data format: expected dict[str, int].")
        return

    sanitized: Dict[str, int] = {}
    for key, val in data.items():
        if not isinstance(key, str):
            logging.warning("Skipping invalid key: %r", key)
            continue
        try:
            quantity = int(val)
        except (TypeError, ValueError):
            logging.warning(
                "Skipping '%s': invalid quantity %r",
                key,
                val,
            )
            continue
        if quantity < 0:
            logging.warning(
                "Skipping '%s': negative quantity %d",
                key,
                quantity,
            )
            continue
        sanitized[key] = quantity

    # Mutate the existing dict to avoid reassigning the module variable
    stock_data.clear()
    stock_data.update(sanitized)
    logging.info("Data loaded successfully from %s", file_path)


def save_data(file_path: str = "inventory.json") -> None:
    """Save current stock_data to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(stock_data, file, indent=2, sort_keys=True)
        logging.info("Data saved successfully to %s", file_path)
    except OSError as err:
        logging.error("Failed to save file '%s': %s", file_path, err)


def print_data() -> None:
    """Display current inventory to stdout."""
    print("Items Report:")
    for item, qty in sorted(stock_data.items()):
        print(f"{item} -> {qty}")


def check_low_items(threshold: int = 5) -> List[str]:
    """Return items with quantity below the given threshold."""
    if not isinstance(threshold, int):
        raise TypeError("Threshold must be an integer.")
    if threshold < 0:
        raise ValueError("Threshold must be non-negative.")
    return [item for item, qty in stock_data.items() if qty < threshold]


def demo_operations() -> None:
    """Demonstrate a sample inventory run."""
    logs: List[str] = []

    for entry in [("apple", 10), ("banana", 2), ("grape", 12)]:
        try:
            add_item(entry[0], entry[1], logs)
        except (TypeError, ValueError) as err:
            logging.error("Error adding %s: %s", entry[0], err)

    remove_item("apple", 3)
    remove_item("orange", 1)

    print(f"Apple stock: {get_qty('apple')}")
    print(f"Low items: {check_low_items()}")

    save_data()
    load_data()
    print_data()

    if logs:
        print("\nOperation logs:")
        for entry in logs:
            print(entry)


def main() -> None:
    """Main entry point."""
    demo_operations()


if __name__ == "__main__":
    main()
