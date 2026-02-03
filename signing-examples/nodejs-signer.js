/**
 * Node.js ECDSA Signature Implementation for LIAM API
 *
 * This script provides functions to sign requests using ECDSA SHA256
 * for authentication with the LIAM API.
 */

const crypto = require('crypto');

/**
 * Sign a request body with ECDSA SHA256
 *
 * @param {Object|string} requestBody - The request body to sign
 * @param {string} privateKeyPem - PEM formatted private key
 * @returns {string} Base64 encoded DER signature
 */
function signRequest(requestBody, privateKeyPem) {
  // Convert request body to JSON string if it's an object
  const payload = typeof requestBody === 'string'
    ? requestBody
    : JSON.stringify(requestBody);

  // Create signer with SHA256
  const sign = crypto.createSign('SHA256');
  sign.update(payload);
  sign.end();

  // Sign with private key and output as DER format
  const signature = sign.sign({
    key: privateKeyPem,
    dsaEncoding: 'der'  // This ensures DER format output
  });

  // Convert to base64
  return signature.toString('base64');
}

/**
 * Make an authenticated request to LIAM API
 *
 * @param {string} endpoint - API endpoint (e.g., 'memory/create')
 * @param {Object} payload - Request payload
 * @param {string} apiKey - Your API key
 * @param {string} privateKey - Your private key (PEM format)
 * @returns {Promise<Object>} API response
 */
async function makeAuthenticatedRequest(endpoint, payload, apiKey, privateKey) {
  const axios = require('axios');

  // Sign the request
  const signature = signRequest(payload, privateKey);

  try {
    const response = await axios.post(
      `https://api.liam.netxd.com/api/${endpoint}`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          'apiKey': apiKey,
          'signature': signature
        }
      }
    );

    return response.data;
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Create a new user profile
 */
async function createUserProfile(name, identification, apiKey, privateKey) {
  const payload = {
    name: name,
    identification: identification,
    identificationType: "UNIQUE_ID"
  };

  const result = await makeAuthenticatedRequest(
    'auth/create-profile',
    payload,
    apiKey,
    privateKey
  );

  return result.data.userkey;  // Returns the auto-generated userkey
}

/**
 * Create a memory for a user
 */
async function createMemory(userKey, content, tag, sessionId, apiKey, privateKey) {
  const payload = {
    userKey: userKey,
    content: content,
    tag: tag || "",
    sessionId: sessionId
  };

  return await makeAuthenticatedRequest(
    'memory/create',
    payload,
    apiKey,
    privateKey
  );
}

/**
 * List memories for a user
 */
async function listMemories(userKey, query, tokens, apiKey, privateKey) {
  const payload = {
    userKey: userKey,
    query: query || "",
    tokens: tokens || []
  };

  return await makeAuthenticatedRequest(
    'memory/list',
    payload,
    apiKey,
    privateKey
  );
}

// Export functions
module.exports = {
  signRequest,
  makeAuthenticatedRequest,
  createUserProfile,
  createMemory,
  listMemories
};

// Example usage (uncomment to test)
/*
const API_KEY = 'BnTtll7mOpDttM0Ppa8LgHyr0RH5jYyACV2GxD4x0';
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgtYaEwoY1wr+d2X6c
FuydV4o6DV2RA37PrpquRuZXDR6hRANCAAR1O1/66cVQ+kRrBi3AnI1rayZRMigy
DHNr9J6DLZOCESgu6N/dDdPTYTMLwDBrkwKJAILAXQxrMajPQmk3fFhd
-----END PRIVATE KEY-----`;

(async () => {
  try {
    // Create a user
    console.log('Creating user...');
    const userKey = await createUserProfile(
      'John Doe',
      'unique_user_123',
      API_KEY,
      PRIVATE_KEY
    );
    console.log('User created! UserKey:', userKey);

    // Create a memory
    console.log('\nCreating memory...');
    const memoryResult = await createMemory(
      userKey,
      'I love Italian food',
      'preferences',
      '2025020300001',
      API_KEY,
      PRIVATE_KEY
    );
    console.log('Memory created:', memoryResult);

    // List memories
    console.log('\nListing memories...');
    const memories = await listMemories(
      userKey,
      'food',
      [],
      API_KEY,
      PRIVATE_KEY
    );
    console.log('Memories:', JSON.stringify(memories, null, 2));

  } catch (error) {
    console.error('Error:', error.message);
  }
})();
*/
