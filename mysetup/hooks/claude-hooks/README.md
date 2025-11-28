
## Optional Dependencies

### jq (JSON processor)

Some commands in this project use `jq` for JSON processing. While not required for basic functionality, it's recommended for better output formatting.

**Installation:**
- macOS: `brew install jq`
- Ubuntu/Debian: `sudo apt-get install jq`
- Windows: Download from https://stedolan.github.io/jq/

**Alternatives:**
If `jq` is not available, you can use:
- Python: `python -m json.tool < input.json`
- Node.js: `node -p "JSON.stringify(JSON.parse(require('fs').readFileSync(0)), null, 2)" < input.json`
