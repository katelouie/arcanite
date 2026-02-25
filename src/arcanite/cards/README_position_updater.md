# Tarot Card Position Updater

A Python script for batch updating tarot card JSON files with new position categories and subcategories.

## Overview

This tool allows you to add new position interpretations to all 78 tarot card files efficiently. Instead of manually editing each file, you can provide a structured JSON input and the script will distribute the interpretations across the relevant card files.

## Usage

### Basic Usage
```bash
python update_card_positions.py input_file.json
```

### Command Line Options
- `--dry-run`: Preview changes without applying them
- `--backup-dir DIR`: Specify custom backup directory
- `--verbose`: Enable detailed logging
- `--cards-dir DIR`: Specify custom cards directory (default: ./generated_cards)

#### Duplicate Handling Options (mutually exclusive)
- `--skip-existing`: Skip cards that already have the interpretation (default)
- `--overwrite`: Overwrite existing interpretations
- `--interactive`: Prompt user for each duplicate found
- `--report-only`: Just report duplicates without making changes

### Examples
```bash
# Preview changes without applying
python update_card_positions.py new_positions.json --dry-run

# Check for duplicates without making changes
python update_card_positions.py new_positions.json --report-only

# Skip existing interpretations (default behavior)
python update_card_positions.py new_positions.json --skip-existing

# Overwrite existing interpretations with warning
python update_card_positions.py new_positions.json --overwrite

# Prompt for each duplicate found
python update_card_positions.py new_positions.json --interactive

# Run with verbose logging and custom backup location
python update_card_positions.py new_positions.json --verbose --backup-dir /path/to/backups
```

## Input File Format

The input must be a JSON file with the following structure:

```json
[
  {
    "category_name": "relationship_dynamics",
    "subcategory_name": "romantic_potential",
    "card_interpretations": {
      "m00": {
        "upright": "Upright interpretation for The Fool",
        "reversed": "Reversed interpretation for The Fool",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"]
      },
      "c01": {
        "upright": "Upright interpretation for Ace of Cups",
        "reversed": "Reversed interpretation for Ace of Cups",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"]
      }
    }
  }
]
```

### Field Descriptions

- **category_name**: The main position category (e.g., "relationship_dynamics", "career_insights")
- **subcategory_name**: The specific position within the category (e.g., "romantic_potential", "leadership_style")
- **card_interpretations**: Dictionary mapping card filenames to their interpretations
  - **Key**: Card filename without .json extension (e.g., "m00", "c01", "w14")
  - **Value**: Object containing upright/reversed interpretations and keywords

### Card Filename Reference

| Card Type | Pattern | Examples |
|-----------|---------|----------|
| Major Arcana | m## | m00 (The Fool), m01 (The Magician), m21 (The World) |
| Cups | c## | c01 (Ace of Cups), c14 (King of Cups) |
| Pentacles | p## | p01 (Ace of Pentacles), p14 (King of Pentacles) |
| Swords | s## | s01 (Ace of Swords), s14 (King of Swords) |
| Wands | w## | w01 (Ace of Wands), w14 (King of Wands) |

Numbers 01-14 for each suit: Ace, 2-10, Page, Knight, Queen, King

## Features

### Safety Features
- **Automatic Backups**: Creates timestamped backup before any changes
- **Dry Run Mode**: Preview changes without applying them
- **Duplicate Detection**: Identifies existing interpretations before processing
- **Input Validation**: Comprehensive validation of input structure and file references
- **Error Handling**: Continues processing even if individual files fail

### Duplicate Handling
- **Smart Detection**: Automatically identifies existing category/subcategory combinations
- **Flexible Options**: Choose how to handle duplicates (skip, overwrite, interactive, report-only)
- **Safe Defaults**: Skips existing interpretations by default to prevent accidental overwrites
- **Detailed Reporting**: Shows which cards already have interpretations and provides summaries

### Logging
- **Progress Tracking**: Shows which cards and categories are being processed
- **Detailed Reporting**: Summary of successful vs failed updates
- **Error Details**: Clear error messages for troubleshooting

### File Structure Preservation
- Maintains existing JSON formatting and structure
- Adds new categories without affecting existing position interpretations
- Preserves all other card data (core_meanings, symbols, etc.)

## Examples

### Adding New Category
To add a completely new position category across multiple cards:

```json
[
  {
    "category_name": "creative_expression",
    "subcategory_name": "artistic_talent",
    "card_interpretations": {
      "m00": {
        "upright": "Raw creative potential ready to manifest in unexpected ways",
        "reversed": "Creative blocks or fear of artistic expression",
        "keywords": ["creative potential", "artistic freedom", "creative blocks", "expression fear"]
      }
    }
  }
]
```

### Adding Subcategory to Existing Category
To add a new subcategory to an existing position category:

```json
[
  {
    "category_name": "guidance_and_action",
    "subcategory_name": "next_steps",
    "card_interpretations": {
      "m00": {
        "upright": "Take the leap with faith and trust in the journey ahead",
        "reversed": "Pause to consider consequences before making major moves",
        "keywords": ["faithful leap", "trust journey", "consider consequences", "thoughtful pause"]
      }
    }
  }
]
```

## Error Handling

The script includes comprehensive error handling:

- **File Not Found**: Reports missing card files
- **Invalid JSON**: Clear messages for malformed input
- **Structure Validation**: Ensures all required fields are present
- **Backup Failures**: Reports backup creation issues
- **Partial Failures**: Continues processing other files if one fails

## Best Practices

1. **Always use --dry-run first** to preview changes
2. **Backup important data** before running batch updates
3. **Validate input files** with small test sets
4. **Use consistent naming** for categories and subcategories
5. **Include all relevant cards** for comprehensive coverage

## Troubleshooting

### Common Issues

**"Card file not found"**
- Check that filenames in input match actual JSON files
- Ensure card files exist in the specified directory

**"Input validation failed"**
- Verify JSON structure matches expected format
- Check that all required fields are present

**"Backup creation failed"**
- Ensure sufficient disk space
- Check write permissions in backup directory

### Recovery

If something goes wrong:
1. Restore from the automatically created backup
2. Check the backup directory (shown in logs)
3. Copy backup files back to generated_cards directory

## Contributing

When modifying the script:
1. Test with --dry-run mode first
2. Validate against small test datasets
3. Ensure backward compatibility with existing files
4. Update documentation for any new features