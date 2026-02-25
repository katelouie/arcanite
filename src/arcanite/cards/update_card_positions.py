#!/usr/bin/env python3
"""
Batch update script for adding new position categories/subcategories to tarot card JSON files.

This script reads a JSON input file containing new position interpretations and distributes
them across the corresponding tarot card files in the generated_cards directory.

Usage:
    python update_card_positions.py input_file.json [--dry-run] [--backup-dir DIR] [--verbose]
                                     [--skip-existing | --overwrite | --interactive | --report-only]

Input JSON format:
[
  {
    "category_name": "relationship_dynamics",
    "subcategory_name": "romantic_potential",
    "card_interpretations": {
      "m00": {
        "upright": "Interpretation text...",
        "reversed": "Interpretation text...",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"]
      }
    }
  }
]
"""

import json
import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum


class DuplicateHandling(Enum):
    """Options for handling duplicate interpretations."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    INTERACTIVE = "interactive"
    REPORT_ONLY = "report"


class CardPositionUpdater:
    """Handles batch updates of tarot card position interpretations."""

    def __init__(self, cards_dir: Path, backup_dir: Optional[Path] = None,
                 dry_run: bool = False, duplicate_handling: DuplicateHandling = DuplicateHandling.SKIP):
        self.cards_dir = Path(cards_dir)
        self.backup_dir = backup_dir
        self.dry_run = dry_run
        self.duplicate_handling = duplicate_handling
        self.logger = self._setup_logger()

        # Validate cards directory exists
        if not self.cards_dir.exists():
            raise FileNotFoundError(f"Cards directory not found: {self.cards_dir}")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('card_updater')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def validate_input_data(self, input_data: List[Dict[str, Any]]) -> bool:
        """Validate the structure and content of input data."""
        if not isinstance(input_data, list):
            self.logger.error("Input data must be a list")
            return False

        for i, entry in enumerate(input_data):
            if not isinstance(entry, dict):
                self.logger.error(f"Entry {i} must be a dictionary")
                return False

            required_fields = ["category_name", "subcategory_name", "card_interpretations"]
            for field in required_fields:
                if field not in entry:
                    self.logger.error(f"Entry {i} missing required field: {field}")
                    return False

            # Validate card interpretations structure
            interpretations = entry["card_interpretations"]
            if not isinstance(interpretations, dict):
                self.logger.error(f"Entry {i}: card_interpretations must be a dictionary")
                return False

            for filename, interp in interpretations.items():
                if not isinstance(interp, dict):
                    self.logger.error(f"Entry {i}, card {filename}: interpretation must be a dictionary")
                    return False

                required_card_fields = ["upright", "reversed", "keywords"]
                for field in required_card_fields:
                    if field not in interp:
                        self.logger.error(f"Entry {i}, card {filename}: missing field {field}")
                        return False

                if not isinstance(interp["keywords"], list):
                    self.logger.error(f"Entry {i}, card {filename}: keywords must be a list")
                    return False

                # Check if card file exists
                card_file = self.cards_dir / f"{filename}.json"
                if not card_file.exists():
                    self.logger.error(f"Card file not found: {card_file}")
                    return False

        self.logger.info(f"Input validation passed for {len(input_data)} entries")
        return True

    def check_duplicates(self, input_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for existing interpretations that would be duplicated."""
        duplicates = {
            "by_category": {},  # category.subcategory -> [filenames]
            "by_file": {},      # filename -> [category.subcategory]
            "total_duplicates": 0,
            "total_cards": 0,
            "summary": []
        }

        for entry in input_data:
            category = entry["category_name"]
            subcategory = entry["subcategory_name"]
            interpretations = entry["card_interpretations"]

            category_key = f"{category}.{subcategory}"
            duplicates["by_category"][category_key] = []

            for filename in interpretations.keys():
                duplicates["total_cards"] += 1
                card_file = self.cards_dir / f"{filename}.json"

                try:
                    with open(card_file, 'r', encoding='utf-8') as f:
                        card_data = json.load(f)

                    # Check if this category.subcategory already exists
                    exists = (
                        "position_interpretations" in card_data and
                        category in card_data["position_interpretations"] and
                        subcategory in card_data["position_interpretations"][category]
                    )

                    if exists:
                        duplicates["total_duplicates"] += 1
                        duplicates["by_category"][category_key].append(filename)

                        if filename not in duplicates["by_file"]:
                            duplicates["by_file"][filename] = []
                        duplicates["by_file"][filename].append(category_key)

                except Exception as e:
                    self.logger.warning(f"Could not check duplicates in {filename}: {e}")

        # Generate summary
        for category_key, filenames in duplicates["by_category"].items():
            if filenames:
                duplicates["summary"].append(
                    f"{category_key}: {len(filenames)} existing ({', '.join(filenames[:5])}"
                    f"{'...' if len(filenames) > 5 else ''})"
                )

        return duplicates

    def handle_duplicate_interactive(self, filename: str, category: str, subcategory: str) -> bool:
        """Interactively ask user how to handle a duplicate."""
        while True:
            response = input(
                f"\n{filename} already has {category}.{subcategory}\n"
                "Options: (s)kip, (o)verwrite, (q)uit: "
            ).lower().strip()

            if response in ['s', 'skip']:
                return False  # Skip this update
            elif response in ['o', 'overwrite']:
                return True   # Proceed with update
            elif response in ['q', 'quit']:
                self.logger.info("User requested to quit")
                sys.exit(0)
            else:
                print("Please enter 's' for skip, 'o' for overwrite, or 'q' for quit")

    def create_backup(self) -> Optional[Path]:
        """Create a timestamped backup of the cards directory."""
        if self.dry_run:
            self.logger.info("Dry run mode: skipping backup creation")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.backup_dir:
            backup_path = self.backup_dir / f"cards_backup_{timestamp}"
        else:
            backup_path = self.cards_dir.parent / f"cards_backup_{timestamp}"

        try:
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy all JSON files
            for json_file in self.cards_dir.glob("*.json"):
                shutil.copy2(json_file, backup_path)

            self.logger.info(f"Backup created: {backup_path}")
            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise

    def update_card_file(self, filename: str, category: str, subcategory: str,
                        interpretation: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a single card file with new position interpretation.

        Returns:
            Tuple of (success: bool, status: str) where status is one of:
            "updated", "skipped_existing", "failed"
        """
        card_file = self.cards_dir / f"{filename}.json"

        try:
            # Read existing card data
            with open(card_file, 'r', encoding='utf-8') as f:
                card_data = json.load(f)

            # Check if interpretation already exists
            exists = (
                "position_interpretations" in card_data and
                category in card_data["position_interpretations"] and
                subcategory in card_data["position_interpretations"][category]
            )

            # Handle duplicates based on policy
            if exists:
                if self.duplicate_handling == DuplicateHandling.SKIP:
                    self.logger.debug(f"Skipping {filename}: {category}.{subcategory} already exists")
                    return True, "skipped_existing"

                elif self.duplicate_handling == DuplicateHandling.REPORT_ONLY:
                    self.logger.info(f"REPORT: {filename} has existing {category}.{subcategory}")
                    return True, "skipped_existing"

                elif self.duplicate_handling == DuplicateHandling.INTERACTIVE:
                    if not self.handle_duplicate_interactive(filename, category, subcategory):
                        return True, "skipped_existing"

                # For OVERWRITE or interactive "overwrite", continue to update

            # Ensure position_interpretations structure exists
            if "position_interpretations" not in card_data:
                card_data["position_interpretations"] = {}

            # Ensure category exists
            if category not in card_data["position_interpretations"]:
                card_data["position_interpretations"][category] = {}

            # Add/update subcategory
            card_data["position_interpretations"][category][subcategory] = {
                "upright": interpretation["upright"],
                "reversed": interpretation["reversed"],
                "keywords": interpretation["keywords"]
            }

            if self.dry_run:
                action = "overwrite" if exists else "add"
                self.logger.info(f"DRY RUN: Would {action} {filename} with {category}.{subcategory}")
                return True, "updated"

            # Write updated data back to file
            with open(card_file, 'w', encoding='utf-8') as f:
                json.dump(card_data, f, indent=2, ensure_ascii=False)

            action = "overwrote" if exists else "added"
            self.logger.debug(f"Successfully {action} {filename} with {category}.{subcategory}")
            return True, "updated"

        except Exception as e:
            self.logger.error(f"Failed to update {filename}: {e}")
            return False, "failed"

    def process_updates(self, input_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process all updates from input data."""
        stats = {
            "processed": 0,
            "updated": 0,
            "skipped_existing": 0,
            "failed": 0
        }

        for entry in input_data:
            category = entry["category_name"]
            subcategory = entry["subcategory_name"]
            interpretations = entry["card_interpretations"]

            self.logger.info(f"Processing {category}.{subcategory} for {len(interpretations)} cards")

            for filename, interpretation in interpretations.items():
                stats["processed"] += 1

                success, status = self.update_card_file(filename, category, subcategory, interpretation)

                if success:
                    stats[status] += 1
                else:
                    stats["failed"] += 1

        return stats

    def run(self, input_file: Path) -> bool:
        """Main execution method."""
        try:
            # Load input data
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)

            # Validate input
            if not self.validate_input_data(input_data):
                return False

            # Check for duplicates and report
            duplicates = self.check_duplicates(input_data)
            if duplicates["total_duplicates"] > 0:
                self.logger.info(f"Found {duplicates['total_duplicates']} existing interpretations "
                               f"out of {duplicates['total_cards']} total")

                if duplicates["summary"]:
                    self.logger.info("Existing interpretations by category:")
                    for summary in duplicates["summary"]:
                        self.logger.info(f"  {summary}")

                # Handle report-only mode
                if self.duplicate_handling == DuplicateHandling.REPORT_ONLY:
                    self.logger.info("Report-only mode: no changes will be made")
                    return True

                # Warn about overwrites
                if self.duplicate_handling == DuplicateHandling.OVERWRITE:
                    self.logger.warning(f"Will overwrite {duplicates['total_duplicates']} existing interpretations")

            # Create backup (skip for report-only mode)
            backup_path = None
            if self.duplicate_handling != DuplicateHandling.REPORT_ONLY:
                backup_path = self.create_backup()

            # Process updates
            mode_desc = "(DRY RUN)" if self.dry_run else f"({self.duplicate_handling.value} mode)"
            self.logger.info(f"Starting updates {mode_desc}")
            stats = self.process_updates(input_data)

            # Report results
            self.logger.info(
                f"Update complete: {stats['updated']} updated, {stats['skipped_existing']} skipped, "
                f"{stats['failed']} failed (out of {stats['processed']} processed)"
            )

            if backup_path and stats['failed'] > 0:
                self.logger.info(f"Backup available at: {backup_path}")

            return stats['failed'] == 0

        except Exception as e:
            self.logger.error(f"Update process failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update tarot card position interpretations")
    parser.add_argument("input_file", type=Path, help="JSON file with new position interpretations")
    parser.add_argument("--cards-dir", type=Path,
                       default=Path(__file__).parent / "generated_cards",
                       help="Directory containing card JSON files")
    parser.add_argument("--backup-dir", type=Path, help="Directory for backups")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without applying them")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Duplicate handling options
    duplicate_group = parser.add_mutually_exclusive_group()
    duplicate_group.add_argument("--skip-existing", action="store_const",
                               dest="duplicate_handling", const=DuplicateHandling.SKIP,
                               help="Skip cards that already have the interpretation (default)")
    duplicate_group.add_argument("--overwrite", action="store_const",
                               dest="duplicate_handling", const=DuplicateHandling.OVERWRITE,
                               help="Overwrite existing interpretations")
    duplicate_group.add_argument("--interactive", action="store_const",
                               dest="duplicate_handling", const=DuplicateHandling.INTERACTIVE,
                               help="Prompt user for each duplicate found")
    duplicate_group.add_argument("--report-only", action="store_const",
                               dest="duplicate_handling", const=DuplicateHandling.REPORT_ONLY,
                               help="Just report duplicates without making changes")

    # Set default for duplicate handling
    parser.set_defaults(duplicate_handling=DuplicateHandling.SKIP)

    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.getLogger('card_updater').setLevel(logging.DEBUG)

    # Validate input file exists
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)

    # Create updater and run
    try:
        updater = CardPositionUpdater(
            cards_dir=args.cards_dir,
            backup_dir=args.backup_dir,
            dry_run=args.dry_run,
            duplicate_handling=args.duplicate_handling
        )

        success = updater.run(args.input_file)
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()