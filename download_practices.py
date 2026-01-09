#!/usr/bin/env python3
"""
Inner Explorer Practice File Downloader

Download audio files from Monday.com Current Practices board by series.
"""

import argparse
import os
import sys
import re
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests


# Board configuration
BOARD_ID = "18393634822"
WORKSPACE_ID = "13709949"
API_URL = "https://api.monday.com/v2"

# File column IDs
FILE_COLUMNS = {
    "file_mkza76s9": {"name": "Short_English", "type": "5min_EN"},
    "file_mkzapzwb": {"name": "Short_Spanish", "type": "5min_ES"},
    "file_mkzanc1b": {"name": "Long_English", "type": "10min_EN"},
    "file_mkzacaj0": {"name": "Long_Spanish", "type": "10min_ES"},
    "file_mkzan21e": {"name": "Cover_Photo", "type": "Cover"},
}

# Series mapping (matches Monday.com group titles)
SERIES_MAP = {
    "high_school_core": "Core High School",
    "middle_school_core": "Core Middle School",
    "elementary_core": "Elementary Core",
    "early_learning_core": "Core Early Learning",
    "transition": "Transition",
    "school_safety": "School Safety",
    "counselor_series": "Counselor Series",
    "sound_practices": "Sound Practices",
}


class MondayAPIClient:
    """Client for interacting with Monday.com GraphQL API."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }

    def query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query against Monday.com API."""
        data = {"query": query}
        if variables:
            data["variables"] = variables

        response = requests.post(API_URL, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(
                f"Error fetching data: {response.status_code}\n{response.text}"
            )

        result = response.json()

        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})

    def fetch_board_items(
        self, board_id: str, limit: int = 100, cursor: Optional[str] = None
    ) -> Tuple[List[Dict], Optional[str]]:
        """Fetch items from a Monday.com board with cursor-based pagination."""
        query = """
        query ($boardId: [ID!], $limit: Int!, $cursor: String) {
          boards(ids: $boardId) {
            items_page(limit: $limit, cursor: $cursor) {
              cursor
              items {
                id
                name
                group {
                  id
                  title
                }
                column_values {
                  id
                  value
                  text
                  type
                }
              }
            }
          }
        }
        """

        variables = {"boardId": board_id, "limit": limit}
        if cursor:
            variables["cursor"] = cursor

        data = self.query(query, variables)
        items_page = data.get("boards", [{}])[0].get("items_page", {})
        return items_page.get("items", []), items_page.get("cursor")

    def fetch_asset_url(self, asset_id: int) -> Optional[str]:
        """Fetch the download URL for an asset by its ID."""
        query = """
        query ($assetIds: [ID!]!) {
          assets(ids: $assetIds) {
            id
            name
            public_url
          }
        }
        """

        variables = {"assetIds": [asset_id]}

        try:
            data = self.query(query, variables)
            assets = data.get("assets", [])
            if assets:
                return assets[0].get("public_url")
        except Exception:
            pass

        return None


class PracticeDownloader:
    """Downloads practice files from Monday.com board."""

    def __init__(
        self,
        api_token: str,
        series: str,
        output_dir: str = "practice_files",
    ):
        self.client = MondayAPIClient(api_token)
        self.series = series
        self.series_name = SERIES_MAP.get(series, series)
        self.output_dir = Path(output_dir) / self._sanitize_filename(self.series_name)
        self.stats = {
            "total_files": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
        }
        self.download_records = []  # Track all download attempts for CSV report

    def _sanitize_filename(self, name: str) -> str:
        """Convert a string to a safe filename."""
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        # Remove or replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', "", name)
        # Remove extra underscores
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

    def _extract_file_info(self, column_value: str) -> Optional[Dict]:
        """Extract file information from Monday.com column value."""
        try:
            if not column_value or column_value == "null" or column_value == "None":
                return None

            data = json.loads(column_value)
            if not data or "files" not in data:
                return None

            files = data.get("files", [])
            if not files:
                return None

            # Get the first file
            file_info = files[0]
            asset_id = file_info.get("assetId")
            if not asset_id:
                return None

            return {
                "assetId": asset_id,
                "name": file_info.get("name"),
            }
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            return None

    def _get_file_extension(self, filename: str, url: str) -> str:
        """Determine file extension from filename or URL."""
        if filename and "." in filename:
            return Path(filename).suffix
        elif url and "." in url:
            # Try to extract extension from URL
            url_path = url.split("?")[0]  # Remove query params
            return Path(url_path).suffix
        return ""

    def _download_file(self, url: str, filepath: Path) -> bool:
        """Download a file from URL to filepath."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Create parent directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True
        except Exception as e:
            print(f"    ✗ Error downloading: {e}")
            return False

    def fetch_practices(self) -> List[Dict]:
        """Fetch all practices from the board, filtered by series."""
        print("Fetching practices from Monday.com...")

        all_items = []
        cursor = None
        limit = 100
        page = 1

        while True:
            items, cursor = self.client.fetch_board_items(BOARD_ID, limit=limit, cursor=cursor)

            if not items:
                break

            # Filter by series (group title)
            filtered_items = [
                item
                for item in items
                if item.get("group", {}).get("title") == self.series_name
            ]

            all_items.extend(filtered_items)

            print(
                f"Page {page}: Fetched {len(filtered_items)} practices (Total: {len(all_items)})"
            )

            # If no cursor returned, we've reached the end
            if not cursor:
                break

            page += 1

        print(f"\n✓ Found {len(all_items)} total practices\n")
        return all_items

    def download_practice_files(self, practice: Dict, practice_number: int) -> None:
        """Download all files for a single practice."""
        practice_name = practice.get("name", "Unknown")
        sanitized_name = self._sanitize_filename(practice_name)

        print(f"\n[{practice_number:03d}_{practice_name}]")

        column_values = {
            col["id"]: col.get("value") for col in practice.get("column_values", [])
        }

        files_found = False

        for col_id, col_info in FILE_COLUMNS.items():
            if col_id not in column_values:
                continue

            file_info = self._extract_file_info(column_values[col_id])

            if not file_info or not file_info.get("assetId"):
                continue

            files_found = True
            self.stats["total_files"] += 1

            # Fetch the download URL from Monday.com using the asset ID
            file_url = self.client.fetch_asset_url(file_info["assetId"])

            if not file_url:
                print(f"  ✗ {col_info['type']}: Could not fetch download URL")
                self.stats["failed"] += 1
                # Record failed URL fetch
                self.download_records.append({
                    "practice_number": practice_number,
                    "practice_name": practice_name,
                    "file_type": col_info['type'],
                    "original_filename": file_info.get("name", "N/A"),
                    "downloaded_filename": "N/A",
                    "status": "Failed - Could not fetch URL",
                    "file_size_mb": "N/A",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                continue

            # Determine file extension
            extension = self._get_file_extension(
                file_info.get("name", ""), file_url
            )

            # Build filename
            filename = f"{practice_number:03d}_{sanitized_name}_{col_info['name']}{extension}"
            filepath = self.output_dir / filename

            # Check if file already exists
            if filepath.exists():
                print(f"  ○ {col_info['type']}: Already exists, skipping")
                self.stats["skipped"] += 1
                file_size_mb = round(filepath.stat().st_size / (1024 * 1024), 2)
                # Record skipped file
                self.download_records.append({
                    "practice_number": practice_number,
                    "practice_name": practice_name,
                    "file_type": col_info['type'],
                    "original_filename": file_info.get("name", "N/A"),
                    "downloaded_filename": filename,
                    "status": "Skipped - Already exists",
                    "file_size_mb": file_size_mb,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                continue

            # Download file
            print(f"  ↓ {col_info['type']}: Downloading...", end=" ")
            if self._download_file(file_url, filepath):
                print("✓")
                self.stats["downloaded"] += 1
                file_size_mb = round(filepath.stat().st_size / (1024 * 1024), 2)
                # Record successful download
                self.download_records.append({
                    "practice_number": practice_number,
                    "practice_name": practice_name,
                    "file_type": col_info['type'],
                    "original_filename": file_info.get("name", "N/A"),
                    "downloaded_filename": filename,
                    "status": "Downloaded",
                    "file_size_mb": file_size_mb,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                self.stats["failed"] += 1
                # Record failed download
                self.download_records.append({
                    "practice_number": practice_number,
                    "practice_name": practice_name,
                    "file_type": col_info['type'],
                    "original_filename": file_info.get("name", "N/A"),
                    "downloaded_filename": filename,
                    "status": "Failed - Download error",
                    "file_size_mb": "N/A",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        if not files_found:
            print("  (no files available)")

    def run(self) -> None:
        """Main download process."""
        print(f"Downloading files to: {self.output_dir}")
        print("=" * 60)

        # Fetch practices
        practices = self.fetch_practices()

        if not practices:
            print(f"No practices found for series: {self.series_name}")
            return

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Download files for each practice
        for idx, practice in enumerate(practices, start=1):
            self.download_practice_files(practice, idx)

        # Print summary
        self.print_summary()

        # Generate CSV report
        self.generate_csv_report()

    def generate_csv_report(self) -> None:
        """Generate a CSV report of all download attempts."""
        if not self.download_records:
            return

        # Create CSV filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"download_report_{self._sanitize_filename(self.series_name)}_{timestamp}.csv"
        csv_filepath = self.output_dir / csv_filename

        try:
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Practice Number",
                    "Practice Name",
                    "File Type",
                    "Original Filename (Monday.com)",
                    "Downloaded Filename",
                    "Status",
                    "File Size (MB)",
                    "Timestamp"
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for record in self.download_records:
                    writer.writerow({
                        "Practice Number": record["practice_number"],
                        "Practice Name": record["practice_name"],
                        "File Type": record["file_type"],
                        "Original Filename (Monday.com)": record["original_filename"],
                        "Downloaded Filename": record["downloaded_filename"],
                        "Status": record["status"],
                        "File Size (MB)": record["file_size_mb"],
                        "Timestamp": record["timestamp"]
                    })

            print(f"\n✓ Download report saved: {csv_filepath.name}")

        except Exception as e:
            print(f"\n✗ Error generating CSV report: {e}")

    def print_summary(self) -> None:
        """Print download summary."""
        print("\n" + "=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Total files found:     {self.stats['total_files']}")
        print(f"Downloaded:            {self.stats['downloaded']}")
        print(f"Skipped (exist):       {self.stats['skipped']}")
        print(f"Failed:                {self.stats['failed']}")
        print(f"\nFiles saved to: {self.output_dir.absolute()}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download Inner Explorer practice files from Monday.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Series options:
  high_school_core     High School Core
  middle_school_core   Middle School Core
  elementary_core      Elementary Core
  early_learning_core  Early Learning Core
  transition           Transition Practices
  school_safety        School Safety Series
  counselor_series     Counselor Series
  sound_practices      Sound Practices

Example usage:
  python3 download_practices.py --series high_school_core --token YOUR_TOKEN
  python3 download_practices.py --series middle_school_core --token YOUR_TOKEN --output ~/Documents/IE
        """,
    )

    parser.add_argument(
        "--series",
        required=True,
        choices=list(SERIES_MAP.keys()),
        help="Practice series to download",
    )

    parser.add_argument(
        "--token",
        required=True,
        help="Monday.com API token",
    )

    parser.add_argument(
        "--output",
        default="practice_files",
        help="Output directory for downloaded files (default: practice_files)",
    )

    args = parser.parse_args()

    try:
        downloader = PracticeDownloader(
            api_token=args.token,
            series=args.series,
            output_dir=args.output,
        )
        downloader.run()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
