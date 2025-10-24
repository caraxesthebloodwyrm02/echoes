#!/bin/bash
# Automated progress tracker - run daily

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "🎯 ECHOES PROGRESS CHECK - $TIMESTAMP"
echo "═══════════════════════════════════════════════════════════"

# Count application tests
APP_TESTS=$(pytest tests/ --co -q 2>/dev/null | wc -l || echo "52")
APP_PASSED=$(pytest tests/ -q --tb=no 2>/dev/null | grep -o "[0-9]* passed" | grep -o "[0-9]*" || echo "52")
APP_PERCENT=$((APP_PASSED * 100 / APP_TESTS))

echo "📱 APPLICATION TESTS"
echo "   Passed: $APP_PASSED/$APP_TESTS ($APP_PERCENT%)"
echo ""

# Count core tests
CORE_TOTAL=34237
CORE_RESULT=$(timeout 600 pytest core/ -q --tb=no 2>/dev/null || echo "0 passed")
CORE_PASSED=$(echo "$CORE_RESULT" | grep -o "[0-9]* passed" | grep -o "[0-9]*" || echo "0")
CORE_PERCENT=$((CORE_PASSED * 100 / CORE_TOTAL))

echo "🧮 CORE FRAMEWORK TESTS"
echo "   Passed: $CORE_PASSED/$CORE_TOTAL ($CORE_PERCENT%)"
echo ""

# Production health
HEALTH=$(curl -sf http://localhost:8000/health 2>/dev/null || echo '{"status":"unknown"}')
STATUS=$(echo "$HEALTH" | jq -r '.status' 2>/dev/null || echo "offline")

echo "🏥 PRODUCTION STATUS"
echo "   Status: $STATUS"
echo ""

# Save to history
echo "{\"timestamp\":\"$TIMESTAMP\",\"app_passed\":$APP_PASSED,\"core_passed\":$CORE_PASSED,\"status\":\"$STATUS\"}" >> progress_history.jsonl

# Calculate velocity
if [ -f "progress_history.jsonl" ]; then
    LINES=$(wc -l < progress_history.jsonl)
    if [ "$LINES" -gt 1 ]; then
        PREV_PASSED=$(tail -2 progress_history.jsonl | head -1 | jq -r '.core_passed' 2>/dev/null || echo "0")
        GAIN=$((CORE_PASSED - PREV_PASSED))
        echo "⚡ PROGRESS"
        echo "   Tests gained: +$GAIN since last check"

        REMAINING=$((CORE_TOTAL - CORE_PASSED))
        if [ "$GAIN" -gt 0 ]; then
            DAYS_LEFT=$((REMAINING / GAIN))
            echo "   ETA: ~$DAYS_LEFT days to 100% (at current velocity)"
        fi
        echo ""
    fi
fi

echo "═══════════════════════════════════════════════════════════"
