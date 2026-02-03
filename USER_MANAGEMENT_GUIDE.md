# XDB User Management - Auto-Generate Keys Guide

## Overview

**Yes, you can now programmatically generate user keys!** Users no longer need to manually provide keys. The system automatically generates a `userkey` when you create their profile.

## Base URL
```
https://api.liam.netxd.com
```

## Authentication

### Application-Level Credentials (You manage these)
- **API Key**: `BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0`
- **Private Key**: Your ECDSA private key (SHA256withECDSA)

These credentials are for **your application**, not end users.

## How It Works

### Old Way (Manual)
❌ Users had to provide:
- User Key
- API Key
- Private Key

### New Way (Automatic) ✅
1. Your app uses its API Key + Private Key
2. Call `create-profile` endpoint
3. API automatically generates a `userkey`
4. Store the `userkey` for that user
5. Use the `userkey` for all user-specific operations

---

## API Endpoints

### 1. Create User Profile (Auto-generates userkey)

**Endpoint**: `POST /api/auth/create-profile`

**Purpose**: Creates a new user and automatically generates their userkey

**Request Headers**:
```
Content-Type: application/json
apiKey: <Your API Key>
signature: <ECDSA signature of request body>
```

**Request Body**:
```json
{
  "name": "John Doe",
  "identification": "unique_user_id_12345",
  "identificationType": "UNIQUE_ID"
}
```

**Success Response** (200):
```json
{
  "status": "Success",
  "message": "User registered successfully.",
  "data": {
    "userkey": "c0312641aade88080be0c7f0801bc4dc6edbeb2752cb1530ae0483728e6a4f81",
    "name": "John Doe",
    "identification": "unique_user_id_12345",
    "profileId": 20
  },
  "timestamp": "2025-03-26T06:51:13.089936+00:00",
  "processId": "b4ba607f0a0e11f0bf26e880883aad51"
}
```

**Error Response** (400):
```json
{
  "status": "Failed",
  "message": "Invalid identification",
  "details": {
    "identification": "Identification already exists"
  },
  "timestamp": "2025-03-26T06:51:53.408641+00:00",
  "processId": "cd0550820a0e11f09e24e880883aad51"
}
```

---

### 2. Register LLM for User

**Endpoint**: `POST /api/user/register-llm`

**Purpose**: Register an LLM API key for a user

**Request Body**:
```json
{
  "apiKey": "s5Lh8TFKDRUH59FZ4LwqLu6GoZD6PRlqbD7XpQGS58",
  "model": "gpt-4",
  "identifier": "ID123456789",
  "key": "sk-proj-..."
}
```

---

## Request Signing

All requests must be signed with your ECDSA private key.

### Signing Algorithm
- **Algorithm**: SHA256withECDSA
- **Process**:
  1. Stringify the request body (JSON)
  2. Sign with your private key
  3. Convert signature to base64
  4. Add as `signature` header

### JavaScript Example (Using jsrsasign)
```javascript
const KJUR = require('jsrsasign');

function signRequest(requestBody, privateKey) {
  const sig = new KJUR.crypto.Signature({
    alg: 'SHA256withECDSA'
  });

  sig.init(privateKey);
  const payloadStr = JSON.stringify(requestBody);
  sig.updateString(payloadStr);

  const sigValueHex = sig.sign();
  const sigBase64 = KJUR.hextob64(sigValueHex);

  return sigBase64;
}

// Usage
const requestBody = {
  name: "John Doe",
  identification: "unique_user_id_12345",
  identificationType: "UNIQUE_ID"
};

const signature = signRequest(requestBody, YOUR_PRIVATE_KEY);
```

### Python Example (Using cryptography)
```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import json
import base64

def sign_request(request_body, private_key_pem):
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )

    # Convert body to JSON string
    payload = json.dumps(request_body, separators=(',', ':'))

    # Sign
    signature = private_key.sign(
        payload.encode(),
        ec.ECDSA(hashes.SHA256())
    )

    # Convert to base64
    return base64.b64encode(signature).decode()

# Usage
request_body = {
    "name": "John Doe",
    "identification": "unique_user_id_12345",
    "identificationType": "UNIQUE_ID"
}

signature = sign_request(request_body, YOUR_PRIVATE_KEY_PEM)
```

---

## Complete Integration Example

### Node.js with Axios
```javascript
const axios = require('axios');
const KJUR = require('jsrsasign');

const API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0';
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----`;

async function createUser(name, identification) {
  const requestBody = {
    name: name,
    identification: identification,
    identificationType: "UNIQUE_ID"
  };

  // Sign the request
  const sig = new KJUR.crypto.Signature({ alg: 'SHA256withECDSA' });
  sig.init(PRIVATE_KEY);
  sig.updateString(JSON.stringify(requestBody));
  const signature = KJUR.hextob64(sig.sign());

  try {
    const response = await axios.post(
      'https://api.liam.netxd.com/api/auth/create-profile',
      requestBody,
      {
        headers: {
          'Content-Type': 'application/json',
          'apiKey': API_KEY,
          'signature': signature
        }
      }
    );

    console.log('User created successfully!');
    console.log('Generated userkey:', response.data.data.userkey);
    return response.data.data.userkey;

  } catch (error) {
    console.error('Error creating user:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
createUser('John Doe', 'unique_user_123')
  .then(userkey => {
    console.log('Store this userkey for the user:', userkey);
  });
```

---

## Memory Operations (Using Generated Userkey)

Once you have a `userkey`, use it for all user-specific operations:

### Create Memory
```javascript
POST /api/memory/create

{
  "userKey": "<generated_userkey>",
  "tag": "notes",
  "content": "Meeting notes from today",
  "sessionId": "2025060400001"
}
```

### List Memories
```javascript
POST /api/memory/list

{
  "userKey": "<generated_userkey>",
  "tokens": [],
  "query": "meeting notes"
}
```

---

## Migration Guide

### If you have existing hardcoded keys:

1. **For new users**: Use the `create-profile` endpoint
2. **For existing users**: You'll need to either:
   - Keep their existing userkeys (if they already have them)
   - Or create new profiles and migrate their data

### Example Migration Function
```javascript
async function migrateUser(oldUserKey, userName, userIdentifier) {
  // Create new profile (generates new userkey)
  const newUserKey = await createUser(userName, userIdentifier);

  // Migrate data from old userkey to new userkey
  // (You'll need to implement data migration based on your needs)

  return newUserKey;
}
```

---

## Summary

### What You Need to Know:

✅ **API Key & Private Key** = Your application credentials (you manage once)
✅ **UserKey** = Auto-generated per user (API creates it)
✅ **Users don't need to provide any keys**
✅ **Workflow**:
   1. Call create-profile with user info
   2. Receive auto-generated userkey
   3. Store userkey for that user
   4. Use userkey in all subsequent requests for that user

### What's Still Missing?

Based on your Postman collection, you have everything you need! The system is fully functional for:
- ✅ Creating users with auto-generated keys
- ✅ Managing memories
- ✅ Tagging and organizing data
- ✅ LLM integration

---

## Testing the API

### Test with cURL (if you have the signing implemented)
```bash
# You'll need to implement the signature generation
# This is a template:

curl -X POST https://api.liam.netxd.com/api/auth/create-profile \
  -H "Content-Type: application/json" \
  -H "apiKey: BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0" \
  -H "signature: <calculated_signature>" \
  -d '{
    "name": "Test User",
    "identification": "test_user_001",
    "identificationType": "UNIQUE_ID"
  }'
```

---

## Security Best Practices

1. **Never expose your API Key or Private Key** in client-side code
2. **Keep Private Key secure** - store in environment variables
3. **Use HTTPS** for all API calls (the API uses https)
4. **Store userkeys securely** in your database
5. **Validate user identification** to prevent duplicates
6. **Implement rate limiting** on your side to prevent abuse

---

## Need Help?

If you encounter any issues:
1. Check the signature is correctly calculated
2. Verify the API Key is correct
3. Ensure the private key format is correct
4. Check the request body matches the expected format
5. Review the error response for specific details

---

## Example Full Implementation

See the Node.js example above for a complete working implementation that:
- Signs requests correctly
- Creates users with auto-generated keys
- Handles errors properly
- Returns the generated userkey for storage
