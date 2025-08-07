#!/bin/bash

# ----------------------
# Configuration Loading
# ----------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.env"

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "❌ Configuration file not found: $CONFIG_FILE"
  echo "Please create the config.env file or copy from config.env.example"
  exit 1
fi

# Load configuration
echo "📋 Loading configuration from: $CONFIG_FILE"
source "$CONFIG_FILE"

# ----------------------
# Command Line Arguments Handling
# ----------------------
VERBOSE=${DEFAULT_VERBOSE:-false}
AUTH_TOKEN_OVERRIDE=""

for arg in "$@"; do
  case $arg in
    --verbose)
      VERBOSE=true
      shift
      ;;
    --token=*)
      AUTH_TOKEN_OVERRIDE="${arg#*=}"
      shift
      ;;
    -t)
      shift
      AUTH_TOKEN_OVERRIDE="$1"
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --verbose        Show detailed output"
      echo "  --token=TOKEN    Set authorization token"
      echo "  -t TOKEN         Set authorization token (short form)"
      echo "  --help, -h       Show this help message"
      exit 0
      ;;
  esac
done

log() {
  if [ "$VERBOSE" = true ]; then
    echo "$@"
  fi
}

# ----------------------
# Authorization Token Handling
# ----------------------
validate_and_set_token() {
  # Use command line override if provided
  if [[ -n "$AUTH_TOKEN_OVERRIDE" ]]; then
    AUTHORIZATION_TOKEN="$AUTH_TOKEN_OVERRIDE"
    log "Using authorization token from command line"
    return 0
  fi
  
  # Check if token is null or empty
  if [[ -z "$AUTHORIZATION_TOKEN" || "$AUTHORIZATION_TOKEN" == "null" ]]; then
    echo "⚠️  Authorization token is not set in config.env"
    echo ""
    echo "🔍 To find your JWT token:"
    echo "1. Open Charles Proxy and capture DoorDash API requests"
    echo "2. Look for the 'authorization' header in any request"
    echo "3. Copy ONLY the part after 'JWT ' (without the JWT prefix)"
    echo ""
    echo "Example: authorization: JWT eyJhbGciOiJIUzI1NiJ9..."
    echo "Copy: eyJhbGciOiJIUzI1NiJ9..."
    echo ""
    echo "(You can also use --token=YOUR_TOKEN or -t YOUR_TOKEN)"
    echo ""
    echo -n "🔑 Enter token (without JWT prefix): "
    read -r AUTHORIZATION_TOKEN
    
    if [[ -z "$AUTHORIZATION_TOKEN" ]]; then
      echo "❌ Authorization token is required. Exiting."
      exit 1
    fi
    
    echo ""
    echo "✅ Authorization token set successfully"
  fi
}

# Validate and set the authorization token
validate_and_set_token

log "----------------------------------------"
log "📡 Making request with the following headers:"
log "x-realtime-recommendation-events: $REALTIME_EVENTS"
log "user-agent: $USER_AGENT"
log "client-version: $CLIENT_VERSION"
log "x-experience-id: $EXPERIENCE_ID"
log "----------------------------------------"

# Check for gawk, install if missing
if ! command -v gawk &>/dev/null; then
  echo "🔍 gawk not found. Installing via Homebrew..."
  if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew is not installed. Please install Homebrew from https://brew.sh first."
    exit 1
  fi
  brew install gawk || { echo "❌ Failed to install gawk."; exit 1; }
else
  echo "✅ gawk is installed."
fi

# Create temp file for curl response
response=$(mktemp)

# Execute the curl request
status=$(curl -s -w "%{http_code}" -o "$response" \
  -H "Host: $API_HOST" \
  -H "Cookie: $COOKIE" \
  -H "x-facets-version: $FACETS_VERSION" \
  -H "x-facets-feature-store-cell-redesign-round-3: $FACETS_FEATURE_STORE" \
  -H "x-realtime-recommendation-events: $REALTIME_EVENTS" \
  -H "authorization: JWT $AUTHORIZATION_TOKEN" \
  -H "accept-language: $ACCEPT_LANGUAGE" \
  -H "x-session-id: $SESSION_ID" \
  -H "x-client-request-id: $CLIENT_REQUEST_ID" \
  -H "x-correlation-id: $CORRELATION_ID" \
  -H "client-version: $CLIENT_VERSION" \
  -H "user-agent: $USER_AGENT" \
  -H "x-experience-id: $EXPERIENCE_ID" \
  -H "x-support-partner-dashpass: $SUPPORT_PARTNER_DASHPASS" \
  -H "dd-ids: $DD_IDS" \
  -H "dd-user-locale: $USER_LOCALE" \
  -H "x-bff-error-format: $BFF_ERROR_FORMAT" \
  -H "dd-location-context: $DD_LOCATION_CONTEXT" \
  --compressed "https://$API_HOST/cx/v3/feed/realtime_recommendation?common_fields.lat=$LATITUDE&common_fields.lng=$LONGITUDE&common_fields.submarket_id=$SUBMARKET_ID&common_fields.district_id=$DISTRICT_ID")

# Check status code
echo "HTTP Status Code: $status"

if [[ "$VERBOSE" == true ]]; then
  echo "--- Pretty-printed response (first ${MAX_VERBOSE_LINES:-100} lines) ---"
  head -n "${MAX_VERBOSE_LINES:-100}" "$response" | jq . || cat "$response"
  echo "-----------------------------------------------"
fi

if [[ "$status" == "200" ]]; then
  echo "--- Extracted Carousel Titles ---"
  gawk '
    BEGIN {
      print "----------------------------------------"
      print "       📦 Matched Carousel Titles"
      print "----------------------------------------"
      count = 0
    }

    /"container_name":/ {
      if (match($0, /"container_name": *"([^"]+)"/, arr)) {
        count++
        printf "carousel %d: %s\n", count, arr[1]
      }
    }

    END {
      print "----------------------------------------"
    }
  ' "$response"
else
  echo "❌ Request failed or returned non-200."
  cat "$response"
fi

rm "$response" 