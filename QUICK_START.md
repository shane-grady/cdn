# 🚀 Quick Start Guide - LIAM API User Management

## TL;DR - The Answer

**YES, you can now auto-generate user keys!** 🎉

Users don't need to provide ANY keys. The API automatically generates a `userkey` when you create their profile.

---

## 5-Minute Setup

### Step 1: Choose Your Language

Pick one:
- **Node.js**: Fast and familiar
- **Python**: Simple and clean
- **Browser**: Visual demo (testing only!)

### Step 2: Install Dependencies

**Node.js**:
```bash
cd signing-examples
npm install
```

**Python**:
```bash
cd signing-examples
pip install -r requirements.txt
```

**Browser**:
```bash
# No installation needed!
open browser-signer.html
```

### Step 3: Update Your Credentials

Open the file you chose and update these two lines:

```javascript
const API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0';  // Your API key
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
...your private key here...
-----END PRIVATE KEY-----`;
```

### Step 4: Run It!

**Node.js**:
```bash
node nodejs-signer.js
```

**Python**:
```bash
python python-signer.py
```

**Browser**:
```bash
# Just open browser-signer.html in your browser
```

---

## How It Works

### Your Application Setup (One Time)

```javascript
// These are YOUR credentials (application-level)
const API_KEY = 'your_api_key';
const PRIVATE_KEY = 'your_private_key';
```

### Create Users (Automatic Keys)

```javascript
// Call this when a new user signs up
const userKey = await createUserProfile(
  'John Doe',           // User's name
  'unique_user_123',    // Unique identifier
  API_KEY,              // Your API key
  PRIVATE_KEY           // Your private key
);

// API returns auto-generated userkey:
// "c0312641aade88080be0c7f0801bc4dc6edbeb2752cb1530ae0483728e6a4f81"

// Store this userkey in your database for this user
saveToDatabase(userId, userKey);
```

### Use Userkey for Operations

```javascript
// Get userkey from your database
const userKey = getFromDatabase(userId);

// Create memory
await createMemory(
  userKey,
  'I love Italian food',
  'preferences',
  sessionId
);

// List memories
const memories = await listMemories(userKey, 'food');
```

---

## Complete Example (Node.js)

```javascript
const { createUserProfile, createMemory, listMemories } = require('./nodejs-signer');

const API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0';
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----`;

async function demo() {
  try {
    // 1. Create a new user (auto-generates userkey)
    console.log('Creating user...');
    const userKey = await createUserProfile(
      'Jane Smith',
      'user_jane_001',
      API_KEY,
      PRIVATE_KEY
    );
    console.log('✅ User created! UserKey:', userKey);

    // 2. Create a memory for this user
    console.log('\nCreating memory...');
    await createMemory(
      userKey,
      'I love hiking in the mountains',
      'hobbies',
      Date.now().toString(),
      API_KEY,
      PRIVATE_KEY
    );
    console.log('✅ Memory created!');

    // 3. List memories
    console.log('\nListing memories...');
    const memories = await listMemories(
      userKey,
      'hiking',
      [],
      API_KEY,
      PRIVATE_KEY
    );
    console.log('✅ Found', memories.data.memories.length, 'memories');
    console.log(JSON.stringify(memories, null, 2));

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

demo();
```

---

## Complete Example (Python)

```python
from python_signer import createUserProfile, createMemory, listMemories
import json

API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0'
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----"""

def demo():
    try:
        # 1. Create a new user (auto-generates userkey)
        print('Creating user...')
        user_key = createUserProfile(
            'Jane Smith',
            'user_jane_001',
            API_KEY,
            PRIVATE_KEY
        )
        print(f'✅ User created! UserKey: {user_key}')

        # 2. Create a memory for this user
        print('\nCreating memory...')
        createMemory(
            user_key,
            'I love hiking in the mountains',
            'hobbies',
            str(int(time.time())),
            API_KEY,
            PRIVATE_KEY
        )
        print('✅ Memory created!')

        # 3. List memories
        print('\nListing memories...')
        memories = listMemories(
            user_key,
            'hiking',
            [],
            API_KEY,
            PRIVATE_KEY
        )
        print(f'✅ Found {len(memories["data"]["memories"])} memories')
        print(json.dumps(memories, indent=2))

    except Exception as e:
        print(f'❌ Error: {str(e)}')

if __name__ == '__main__':
    demo()
```

---

## API Endpoints

| Endpoint | Purpose | Auto-generates |
|----------|---------|----------------|
| `/api/auth/create-profile` | Create user | ✅ userkey |
| `/api/memory/create` | Create memory | - |
| `/api/memory/list` | List memories | - |
| `/api/memory/forget` | Delete memory | - |
| `/api/memory/list-tag` | List tags | - |
| `/api/memory/by-tag` | Get by tag | - |
| `/api/memory/change-tag` | Change tag | - |
| `/api/memory/chat` | Chat with AI | - |

---

## FAQ

### Q: Do users need to provide keys?
**A:** NO! The API generates the userkey automatically.

### Q: What do I need to store?
**A:** Just your API Key and Private Key (application level).

### Q: What do I store per user?
**A:** Just the auto-generated userkey from the API.

### Q: Is it secure?
**A:** YES! Uses ECDSA signature authentication.

### Q: Can I test it now?
**A:** YES! Run any of the example scripts.

### Q: Does the API work?
**A:** YES! The base URL is `https://api.liam.netxd.com`

---

## Troubleshooting

### Issue: "Invalid signature"
**Solution**: Check that your private key is in correct PEM format with proper line breaks.

### Issue: "Profile not found"
**Solution**: Make sure you created the user first and are using the correct userkey.

### Issue: "Identification already exists"
**Solution**: Each user needs a unique identification. Try a different ID.

---

## Next Steps

1. ✅ You've learned how it works
2. ✅ You have working code examples
3. ✅ You know the API is ready
4. **Now**: Integrate into your application!

---

## Files You Need

| File | Purpose |
|------|---------|
| `ANSWER_TO_YOUR_QUESTIONS.md` | Direct answers to your questions |
| `USER_MANAGEMENT_GUIDE.md` | Complete documentation |
| `signing-examples/nodejs-signer.js` | Node.js implementation |
| `signing-examples/python-signer.py` | Python implementation |
| `signing-examples/browser-signer.html` | Browser demo |
| `signing-examples/README.md` | Examples documentation |

---

## Summary

✅ **Auto-generate keys**: YES, it works!
✅ **User setup**: NONE required
✅ **Your setup**: API Key + Private Key (once)
✅ **Documentation**: Complete
✅ **Code examples**: Node.js, Python, Browser
✅ **API status**: Ready to use
✅ **Base URL**: https://api.liam.netxd.com

**Everything you need is ready!** 🎉

---

## One-Line Summary

**Your app uses API Key + Private Key → API auto-generates userkey → Store userkey → Done!**
