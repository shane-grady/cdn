# LIAM API Signing Examples

This folder contains complete working examples of how to sign requests for the LIAM API using different programming languages.

## Available Examples

### 1. Node.js (`nodejs-signer.js`)
**Requirements**: `npm install axios`

Complete Node.js implementation with:
- Request signing using native crypto module
- Helper functions for all common operations
- Example usage code

**Quick Start**:
```bash
npm install axios
node nodejs-signer.js
```

### 2. Python (`python-signer.py`)
**Requirements**: `pip install cryptography requests`

Complete Python implementation with:
- Request signing using cryptography library
- Helper functions for all common operations
- Example usage code

**Quick Start**:
```bash
pip install cryptography requests
python python-signer.py
```

### 3. Browser JavaScript (`browser-signer.html`)
Interactive browser-based demo with:
- No external dependencies (uses Web Crypto API)
- User-friendly interface
- Real-time testing

**Quick Start**:
```bash
# Just open in a browser
open browser-signer.html
# or
python -m http.server 8000  # Then visit http://localhost:8000/browser-signer.html
```

## How It Works

### Authentication Flow

1. **Application Credentials** (One-time setup)
   - You have an API Key and Private Key (ECDSA P-256)
   - These are for YOUR application, not end users

2. **Create Users** (Automatic key generation)
   ```
   Your App → [API Key + Signed Request] → API
   API → [Generates userkey] → Your App
   ```

3. **User Operations** (Use generated userkey)
   ```
   Your App → [API Key + Signed Request + userkey] → API
   ```

### Signature Generation

All examples follow the same process:

1. **Prepare payload**: Convert to JSON string
2. **Sign**: Use ECDSA SHA256 with P-256 curve
3. **Encode**: Output as DER-encoded Base64
4. **Send**: Include in `signature` header

### Example Request Flow

```javascript
// 1. Create user (generates userkey automatically)
const userKey = await createUser("John Doe", "unique_id_123");
// Returns: "c0312641aade88080be0c7f0801bc4dc6edbeb2752cb1530ae0483728e6a4f81"

// 2. Use userkey for operations
await createMemory(userKey, "I love pizza", "preferences");
const memories = await listMemories(userKey);
```

## API Key & Private Key

Your credentials (update these in each file):

```javascript
const API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0';
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----`;
```

## Common Operations

### Create User Profile
```javascript
// Automatically generates userkey
const userKey = await createUserProfile(
  'John Doe',
  'unique_user_123',
  API_KEY,
  PRIVATE_KEY
);
```

### Create Memory
```javascript
await createMemory(
  userKey,
  'I love Italian food',
  'preferences',
  '2025020300001',  // session ID
  API_KEY,
  PRIVATE_KEY
);
```

### List Memories
```javascript
const memories = await listMemories(
  userKey,
  'food',  // search query
  [],      // tokens
  API_KEY,
  PRIVATE_KEY
);
```

### Forget Memory
```javascript
await forgetMemory(
  userKey,
  'query_hash_here',
  API_KEY,
  PRIVATE_KEY
);
```

## Troubleshooting

### Common Issues

1. **"Invalid signature" error**
   - Check that your private key is in correct PEM format
   - Ensure no extra whitespace in the key
   - Verify the payload is being stringified correctly

2. **"Profile not found" error**
   - Make sure you're using the correct userkey
   - Verify the user was created successfully

3. **"Identification already exists" error**
   - The identification must be unique per user
   - Use a different identification or check existing users

### Testing Connection

Try this simple test (Node.js):
```javascript
const crypto = require('crypto');

// Test signing
const payload = { test: "data" };
const sign = crypto.createSign('SHA256');
sign.update(JSON.stringify(payload));
sign.end();

const signature = sign.sign({
  key: PRIVATE_KEY,
  dsaEncoding: 'der'
});

console.log('Signature:', signature.toString('base64'));
```

## Security Best Practices

⚠️ **IMPORTANT SECURITY NOTES**:

1. **Never expose private keys in client-side code** (browser)
   - The browser example is for DEMO purposes only
   - Always sign on your server

2. **Store credentials securely**
   - Use environment variables
   - Never commit keys to git
   - Use secrets management in production

3. **Validate user input**
   - Sanitize identification fields
   - Validate content before sending

4. **Use HTTPS**
   - The API uses HTTPS by default
   - Never make requests over HTTP

## Need Help?

- Check the main [USER_MANAGEMENT_GUIDE.md](../USER_MANAGEMENT_GUIDE.md)
- Review error messages carefully
- Test with the browser demo first to verify credentials
- Check that your private key matches the public key registered with your API account

## Example Output

### Successful User Creation:
```json
{
  "status": "Success",
  "message": "User registered successfully.",
  "data": {
    "userkey": "c0312641aade88080be0c7f0801bc4dc6edbeb2752cb1530ae0483728e6a4f81",
    "name": "John Doe",
    "identification": "unique_user_123",
    "profileId": 20
  },
  "timestamp": "2025-03-26T06:51:13.089936+00:00",
  "processId": "b4ba607f0a0e11f0bf26e880883aad51"
}
```

### Successful Memory Creation:
```json
{
  "status": "Success",
  "message": "Your memory has been recorded successfully.",
  "data": {},
  "timestamp": "2025-03-26T07:37:25.314532+00:00",
  "processId": "295492e00a1511f0a7eee880883aad51"
}
```

## License

These examples are provided as-is for educational purposes.
