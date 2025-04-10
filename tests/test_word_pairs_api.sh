#!/bin/bash

# Basic integration test script for the Word Pairs API
# Requires curl and jq to be installed

set -e # Exit immediately if a command exits with a non-zero status.
# set -x # Uncomment for debugging (prints each command before execution)

BASE_URL="http://127.0.0.1:8000/word-pairs"
HEADERS=(-H "Content-Type: application/json")

echo "--- Starting Word Pairs API Test ---"

# Ensure the server is potentially running (add a small delay if needed)
sleep 1

# 1. Create a new word pair
echo "1. Testing POST ${BASE_URL}/"
# Perform the request and capture both status and response
# Use a temporary file for the response to avoid issues with command substitution and newlines
TEMP_RESPONSE_FILE=$(mktemp)
CREATE_STATUS=$(curl -s -w "%{http_code}" -o "$TEMP_RESPONSE_FILE" -X POST "${BASE_URL}/" "${HEADERS[@]}" -d '{"source_word": "test_src", "target_word": "test_tgt", "category": "test", "example_sentence": "This is a test."}')
CREATE_RESPONSE=$(cat "$TEMP_RESPONSE_FILE")
rm "$TEMP_RESPONSE_FILE" # Clean up temp file

if [ "$CREATE_STATUS" -ne 201 ]; then
    echo "   ERROR: Expected status 201 from POST, got $CREATE_STATUS"
    echo "   Response: $CREATE_RESPONSE"
    exit 1
fi

# Extract ID using jq
WORD_PAIR_ID=$(echo "$CREATE_RESPONSE" | jq -r '._id')

if [ -z "$WORD_PAIR_ID" ] || [ "$WORD_PAIR_ID" == "null" ]; then
    echo "   ERROR: Could not extract _id from POST response."
    echo "   Response: $CREATE_RESPONSE"
    exit 1
fi
echo "   SUCCESS: Created word pair with ID: $WORD_PAIR_ID"


# 2. List all word pairs
echo "2. Testing GET ${BASE_URL}/"
LIST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${BASE_URL}/")
if [ "$LIST_STATUS" -ne 200 ]; then
    echo "   ERROR: Expected status 200 from GET list, got $LIST_STATUS"
    exit 1
fi
echo "   SUCCESS: GET list returned status 200."

# 3. Get the created word pair by ID
echo "3. Testing GET ${BASE_URL}/${WORD_PAIR_ID}"
GET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${BASE_URL}/${WORD_PAIR_ID}")
GET_RESPONSE=$(curl -s -X GET "${BASE_URL}/${WORD_PAIR_ID}")
if [ "$GET_STATUS" -ne 200 ]; then
    echo "   ERROR: Expected status 200 from GET single, got $GET_STATUS"
    exit 1
fi
# Validate content
GET_ID=$(echo "$GET_RESPONSE" | jq -r '._id')
if [ "$GET_ID" != "$WORD_PAIR_ID" ]; then
     echo "   ERROR: GET request returned wrong ID ($GET_ID) or malformed JSON."
     echo "   Response: $GET_RESPONSE"
     exit 1
fi
echo "   SUCCESS: GET single returned status 200 and correct ID."

# 4. Update the word pair
echo "4. Testing PUT ${BASE_URL}/${WORD_PAIR_ID}"
UPDATE_PAYLOAD='{"source_word": "test_src_updated", "target_word": "test_tgt_updated", "category": "test_updated", "example_sentence": "This is an updated test."}'
TEMP_RESPONSE_FILE=$(mktemp)
UPDATE_STATUS=$(curl -s -w "%{http_code}" -o "$TEMP_RESPONSE_FILE" -X PUT "${BASE_URL}/${WORD_PAIR_ID}" "${HEADERS[@]}" -d "$UPDATE_PAYLOAD")
UPDATE_RESPONSE=$(cat "$TEMP_RESPONSE_FILE")
rm "$TEMP_RESPONSE_FILE"

if [ "$UPDATE_STATUS" -ne 200 ]; then
    echo "   ERROR: Expected status 200 from PUT, got $UPDATE_STATUS"
    echo "   Response: $UPDATE_RESPONSE"
    exit 1
fi
# Validate update
UPDATED_CATEGORY=$(echo "$UPDATE_RESPONSE" | jq -r '.category')
if [ "$UPDATED_CATEGORY" != "test_updated" ]; then
     echo "   ERROR: PUT request did not return updated category ('test_updated'). Expected 'test_updated'."
     echo "   Response: $UPDATE_RESPONSE"
     exit 1
fi
echo "   SUCCESS: PUT returned status 200 and updated data."

# 5. Delete the word pair
echo "5. Testing DELETE ${BASE_URL}/${WORD_PAIR_ID}"
DELETE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE_URL}/${WORD_PAIR_ID}")
if [ "$DELETE_STATUS" -ne 204 ]; then
    echo "   ERROR: Expected status 204 from DELETE, got $DELETE_STATUS"
    exit 1
fi
echo "   SUCCESS: DELETE returned status 204."

# 6. Verify deletion by trying to get the word pair again
echo "6. Verifying DELETE with GET ${BASE_URL}/${WORD_PAIR_ID}"
VERIFY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${BASE_URL}/${WORD_PAIR_ID}")
if [ "$VERIFY_STATUS" -ne 404 ]; then
    echo "   ERROR: Expected status 404 after delete, got $VERIFY_STATUS"
    exit 1
fi
echo "   SUCCESS: GET after DELETE returned status 404."

echo "--- Word Pairs API Test Completed Successfully ---"

exit 0 