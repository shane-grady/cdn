# Inner Explorer Practice File Downloader

Download audio files from Monday.com Current Practices board by series, directly from your Mac Terminal.

## Quick Start

### 1. Get Your Monday.com API Token

1. Go to https://monday.com
2. Click your avatar (top right) → **Admin** → **API**
3. Click **Generate** to create a new API token
4. Copy the token (you'll need it for step 3)

### 2. Install Python Dependencies

Open Terminal and run:

```bash
pip3 install requests
```

### 3. Run the Downloader

Navigate to where you saved `download_practices.py`, then run:

```bash
python3 download_practices.py --series high_school_core --token YOUR_API_TOKEN_HERE
```

Replace `YOUR_API_TOKEN_HERE` with the token you copied in step 1.

## Series Options

Choose from these series:

```bash
# High School Core (179 practices)
python3 download_practices.py --series high_school_core --token YOUR_TOKEN

# Middle School Core
python3 download_practices.py --series middle_school_core --token YOUR_TOKEN

# Elementary Core
python3 download_practices.py --series elementary_core --token YOUR_TOKEN

# Early Learning Core
python3 download_practices.py --series early_learning_core --token YOUR_TOKEN

# Transition Practices
python3 download_practices.py --series transition --token YOUR_TOKEN

# School Safety Series
python3 download_practices.py --series school_safety --token YOUR_TOKEN

# Counselor Series
python3 download_practices.py --series counselor_series --token YOUR_TOKEN

# Sound Practices
python3 download_practices.py --series sound_practices --token YOUR_TOKEN
```

## Custom Output Directory

By default, files download to `practice_files/` in your current directory. To change this:

```bash
python3 download_practices.py \
  --series high_school_core \
  --token YOUR_TOKEN \
  --output ~/Documents/IE_Practices
```

## What Gets Downloaded

For each practice, the script downloads available files from these columns:

- **Short English** - 5-minute English audio
- **Short Spanish** - 5-minute Spanish audio
- **Long English** - 10-minute English audio
- **Long Spanish** - 10-minute Spanish audio
- **Cover Photo** - Cover image (if available)

## File Naming Convention

Files use a standardized naming format:

```
{number}_{practice_name}_{duration}_{language}.ext
```

**Examples:**
```
001_Introduction_to_Mindfulness_Short_English.mp3
001_Introduction_to_Mindfulness_Long_English.mp3
001_Introduction_to_Mindfulness_Short_Spanish.mp3
001_Introduction_to_Mindfulness_Long_Spanish.mp3
001_Introduction_to_Mindfulness_Cover_Photo.jpg
002_Questions_to_Consider_Short_English.mp3
...
```

**Format Breakdown:**
- `001` - Practice number in series (padded to 3 digits)
- `Introduction_to_Mindfulness` - Practice name (cleaned)
- `Short` or `Long` - Duration (5min or 10min)
- `English` or `Spanish` - Language
- `.mp3` or `.jpg` - File extension

## Example Output

```
Fetching practices from Monday.com...
Page 1: Fetched 100 practices (Total: 100)
Page 2: Fetched 79 practices (Total: 179)

✓ Found 179 total practices

Downloading files to: practice_files/High_School_Core
============================================================

[001_Introduction to Mindfulness]

[002_Questions to Consider]

[003_How Mindfulness Helps Students and Mountain Practice]

[006_Getting Started With a Mindfulness Practice]
  ↓ 5min_EN: Downloading... ✓
  ↓ 10min_EN: Downloading... ✓

...

============================================================
DOWNLOAD SUMMARY
============================================================
Total files found:     358
Downloaded:            358
Skipped (exist):       0
Failed:                0

Files saved to: /Users/yourname/practice_files/High_School_Core
```

## Tips

### Running Multiple Downloads

Download all series in sequence:

```bash
python3 download_practices.py --series high_school_core --token YOUR_TOKEN
python3 download_practices.py --series middle_school_core --token YOUR_TOKEN
python3 download_practices.py --series elementary_core --token YOUR_TOKEN
```

### Resume Interrupted Downloads

The script automatically skips files that already exist, so you can safely re-run it to resume interrupted downloads.

### Check What You Have

After downloading, check your files:

```bash
# Count total files
find practice_files -name "*.mp3" | wc -l

# List practices in a series
ls -lh practice_files/High_School_Core/

# Check file sizes
du -sh practice_files/*/
```

## Troubleshooting

### "No module named 'requests'"

Install the requests library:

```bash
pip3 install requests
```

### "Error fetching data: 401"

Your API token is invalid or expired. Generate a new token from Monday.com.

### "Error fetching data: 403"

Your API token doesn't have permission to access this board. Make sure you're using an account that has access to the Inner Explorer V2 workspace.

### Files downloading but showing as 0 bytes

This usually means the API token doesn't have file access permissions. Try regenerating your token with full API access.

## Board Information

- **Board Name**: Current Practices
- **Board ID**: 18393634822
- **Workspace**: Inner Explorer V2 (13709949)
- **Total Practices**: 924

## File Columns

The script downloads from these Monday.com columns:

| Column | ID | File Type |
|--------|-----|-----------|
| 5 Min (EN) | file_mkza76s9 | 5-minute English MP3 |
| 5 Min (ES) | file_mkzapzwb | 5-minute Spanish MP3 |
| 10 Min (EN) | file_mkzanc1b | 10-minute English MP3 |
| 10 Min (ES) | file_mkzacaj0 | 10-minute Spanish MP3 |
| Cover Photo | file_mkzan21e | Cover image |

## Support

For issues or questions about the downloader, contact Shane.

For Monday.com API issues, see: https://developer.monday.com/api-reference
