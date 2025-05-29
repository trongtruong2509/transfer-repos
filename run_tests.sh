#!/bin/bash
# Run all tests and generate an HTML report

# Source environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    source .env
fi

# Default is to skip real integration tests
RUN_FULL_TESTS=0
# Default is to skip real execution tests 
RUN_REAL_EXECUTION=0

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--full)
            RUN_FULL_TESTS=1
            shift
            ;;
        -r|--real-execution)
            RUN_REAL_EXECUTION=1
            shift
            ;;
        *)
            # Unknown option
            shift
            ;;
    esac
done

set -e  # Exit on error

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

# Check if we're on a Debian/Ubuntu system
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" == "debian" || "$ID" == "ubuntu" || "$ID_LIKE" == *"debian"* ]]; then
        print_status "Detected Debian/Ubuntu-based system"
        
        # Check if python3-venv is installed
        if ! dpkg -l python3-venv 2>/dev/null | grep -q "^ii"; then
            print_warning "python3-venv is not installed. Installing now..."
            print_warning "You may be prompted for your password."
            sudo apt update || { print_error "Failed to update package lists"; exit 1; }
            sudo apt install -y python3-venv python3-pip || { 
                print_error "Failed to install python3-venv. Please install it manually:"; 
                print_error "sudo apt install python3-venv python3-pip"; 
                exit 1; 
            }
        fi
    else
        print_status "Non-Debian system detected, assuming Python environment is already set up"
    fi
else
    print_status "Cannot determine OS type, assuming Python environment is already set up"
fi

# Clean up any partially created venv
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    print_warning "Found incomplete virtual environment. Removing it..."
    rm -rf venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    
    # Try Python 3.10 explicitly first if available
    if command -v python3.10 &> /dev/null; then
        print_status "Using Python 3.10 to create the virtual environment..."
        python3.10 -m venv venv
    # Then try Python 3.8
    elif command -v python3.8 &> /dev/null; then
        print_status "Using Python 3.8 to create the virtual environment..."
        python3.8 -m venv venv
    # Then try the default python3
    else
        print_status "Using default Python 3 to create the virtual environment..."
        python3 -m venv venv
    fi
    
    # Check if activation script was created
    if [ ! -f "venv/bin/activate" ]; then
        print_error "Failed to create a proper virtual environment (activate script not found)."
        print_error "Let's try an alternative approach..."
        
        # Remove the failed venv directory
        rm -rf venv
        
        # Try with the --without-pip option and install pip manually
        print_status "Attempting to create venv without pip (will install pip later)..."
        python3 -m venv --without-pip venv
        
        if [ ! -f "venv/bin/activate" ]; then
            print_error "Virtual environment creation failed completely."
            print_error "Try running these commands manually:"
            print_error "rm -rf venv"
            print_error "python3 -m venv venv"
            exit 1
        fi
    fi
fi

# Verify activation script exists
if [ ! -f "venv/bin/activate" ]; then
    print_error "Virtual environment activate script not found at venv/bin/activate"
    print_error "This indicates a problem with your Python installation or venv module."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment."
    exit 1
fi

# Verify the activation worked
if [ -z "$VIRTUAL_ENV" ]; then
    print_error "Virtual environment activation didn't set VIRTUAL_ENV variable."
    print_error "This indicates an issue with your venv or shell compatibility."
    exit 1
fi

print_status "Successfully activated virtual environment: $VIRTUAL_ENV"

# Install required packages
print_status "Installing required packages..."

# Check if pip is available in the virtual environment
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    print_warning "pip not found in virtual environment. Installing pip..."
    curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
fi

# Determine which pip command to use
PIP_CMD="pip"
if ! command -v pip &> /dev/null && command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

# Upgrade pip
print_status "Upgrading pip..."
$PIP_CMD install --upgrade pip || {
    print_warning "Failed to upgrade pip, but continuing anyway..."
}

# Install requirements
if [ -f "requirements.txt" ]; then
    print_status "Installing requirements from requirements.txt..."
    $PIP_CMD install -r requirements.txt || {
        print_error "Failed to install requirements from requirements.txt."
        print_error "Trying to continue with minimal requirements..."
    }
else
    print_warning "requirements.txt not found, creating a minimal one."
    echo "pytest==7.3.1
pytest-html==3.2.0
pytest-cov==4.1.0
pytest-mock==3.10.0
requests==2.28.2" > requirements.txt
    $PIP_CMD install -r requirements.txt || {
        print_error "Failed to install minimal requirements."
        exit 1
    }
fi

# Ensure test dependencies are installed
print_status "Installing test dependencies..."
$PIP_CMD install pytest pytest-html pytest-cov pytest-mock || {
    print_error "Failed to install test dependencies."
    exit 1
}

# Create test results directory
print_status "Creating test results directory..."
mkdir -p test_results

# Determine the Python command to use
PYTHON_CMD="python"
if ! command -v python &> /dev/null && command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Determine the module to test
MODULE_NAME="repo_transfer"
if [ ! -d "$MODULE_NAME" ]; then
    # Try to auto-detect the module name
    for dir in */; do
        if [ -f "${dir}__init__.py" ]; then
            MODULE_NAME=${dir%/}
            print_warning "Auto-detected module name as: $MODULE_NAME"
            break
        fi
    done
fi

# Run tests with coverage and generate HTML report
print_status "Running tests..."

# Set up the environment variable for integration tests if full tests are requested
if [ "$RUN_FULL_TESTS" -eq 1 ]; then
    print_status "Running FULL tests including real integration tests..."
    export GITHUB_TEST_INTEGRATION=1
else
    print_status "Running standard tests (skipping real integration tests)..."
    export GITHUB_TEST_INTEGRATION=0
fi

# Set up the environment variable for real execution tests if requested
if [ "$RUN_REAL_EXECUTION" -eq 1 ]; then
    print_status "Running REAL EXECUTION tests that perform actual repository transfers..."
    export GITHUB_TEST_REAL_EXECUTION=1
    
    # Check if GITHUB_TOKEN environment variable is set
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN environment variable is required for real execution tests."
        print_error "Please set it in your .env file or export it before running the tests."
        exit 1
    fi
    
    # Check if the test organizations are configured in conftest.py
    if grep -q "\"Replace with your actual" test/conftest.py; then
        print_error "The test organizations in test/conftest.py need to be configured."
        print_error "Please update TEST_ORG_1, TEST_ORG_2, and TEST_USER in test/conftest.py."
        exit 1
    fi
else
    export GITHUB_TEST_REAL_EXECUTION=0
fi

$PYTHON_CMD -m pytest test/ \
    --html=test_results/report.html \
    --cov=$MODULE_NAME \
    --cov-report=html:test_results/coverage \
    -v \
    -k "not test_logging" || {
    print_error "Some tests failed."
    TEST_STATUS=1  # Set error status but continue to show report
}

# Check if the coverage report was generated
if [ -f "test_results/coverage/index.html" ]; then
    coverage_percentage=$(grep -o "total.*%" test_results/coverage/index.html | grep -o "[0-9]\+%" | head -1)
    print_status "Test coverage: $coverage_percentage"
else
    print_warning "Coverage report was not generated."
fi

# Deactivate virtual environment
deactivate

if [ -n "$TEST_STATUS" ]; then
    print_warning "Testing completed with some failures. Reports available in test_results directory."
else
    print_status "Testing completed successfully. Reports available in test_results directory."
fi

print_status "HTML report: test_results/report.html"
print_status "Coverage report: test_results/coverage/index.html"

# Exit with the test status
exit ${TEST_STATUS:-0}
