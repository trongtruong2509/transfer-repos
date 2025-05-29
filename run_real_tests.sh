#!/bin/bash
# Run real execution tests for GitHub Repository Transfer Tool

# Source environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    source .env
    
    # Export variables for pytest
    export TEST_ORG_1
    export TEST_ORG_2
    export TEST_USER
    export TEST_REPO
else
    echo "No .env file found. You can create one from .env.template"
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    print_error "GITHUB_TOKEN environment variable is required."
    print_error "Please set it in your .env file or export it before running the tests."
    exit 1
fi

# Check if the test organizations are properly configured
if [ -z "$TEST_ORG_1" ] || [ -z "$TEST_ORG_2" ] || [ -z "$TEST_USER" ]; then
    print_error "TEST_ORG_1, TEST_ORG_2, and TEST_USER must be set for real execution tests."
    print_error "Please set them in your .env file or export them before running the tests."
    exit 1
fi

print_status "Using the following configuration:"
print_status "  - Source organization: $TEST_ORG_1"
print_status "  - Destination organization: $TEST_ORG_2"
print_status "  - GitHub username: $TEST_USER"

# Print header
print_status "==============================================================="
print_status "   GitHub Repository Transfer Tool - Real Execution Tests"
print_status "==============================================================="

# Confirm with the user
print_warning "This will perform ACTUAL repository transfers between your organizations."
print_warning "Make sure you have run setup_test_repos.sh to create the test repositories."
echo ""
read -p "Do you want to continue? [y/N] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Aborted by user."
    exit 0
fi

# Determine the Python command to use
PYTHON_CMD="python"
if ! command -v python &> /dev/null && command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Run the real execution tests
print_status "Running real execution tests..."
export GITHUB_TEST_REAL_EXECUTION=1

$PYTHON_CMD -m pytest test/real_execution -v

# Print completion message
if [ $? -eq 0 ]; then
    print_status "==============================================================="
    print_status "   Real execution tests completed successfully!"
    print_status "==============================================================="
    exit 0
else
    print_error "==============================================================="
    print_error "   Real execution tests failed!"
    print_error "==============================================================="
    exit 1
fi
