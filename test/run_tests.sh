#!/bin/bash
# Run all tests and generate an HTML report
#
# Usage:
#   ./run_tests.sh             # Run unit tests only
#   ./run_tests.sh -i          # Run integration tests only
#   ./run_tests.sh -r          # Run real execution tests only
#   ./run_tests.sh -f          # Run unit tests and integration tests
#   ./run_tests.sh --all       # Run all tests (unit, integration, real)

# Source environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    source .env
    
    # Export variables for pytest
    export TEST_ORG_1
    export TEST_ORG_2
    export TEST_USER
    export TEST_REPO
    export TEST_REPO_SUFFIX
else
    echo "No .env file found. You might need to create one from the template:"
    echo "cp .env.template .env && nano .env"
    
    # Check if we're running in CI environment where env vars might be set differently
    if [ -z "$CI" ]; then
        if [ ! -f "test/conftest.py" ]; then
            print_error "No .env file and no conftest.py found. Cannot proceed."
            exit 1
        fi
    fi
fi

# Default is to run unit tests only
RUN_UNIT_TESTS=1
RUN_INTEGRATION_TESTS=0
RUN_REAL_EXECUTION=0

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--integration)
            RUN_UNIT_TESTS=0
            RUN_INTEGRATION_TESTS=1
            RUN_REAL_EXECUTION=0
            shift
            ;;
        -r|--real-execution)
            RUN_UNIT_TESTS=0
            RUN_INTEGRATION_TESTS=0
            RUN_REAL_EXECUTION=1
            shift
            ;;
        -f|--full)
            RUN_UNIT_TESTS=1
            RUN_INTEGRATION_TESTS=1
            RUN_REAL_EXECUTION=0
            shift
            ;;
        --all)
            RUN_UNIT_TESTS=1
            RUN_INTEGRATION_TESTS=1
            RUN_REAL_EXECUTION=1
            shift
            ;;
        -h|--help)
            echo "Usage:"
            echo "  ./run_tests.sh             # Run unit tests only"
            echo "  ./run_tests.sh -i          # Run integration tests only"
            echo "  ./run_tests.sh -r          # Run real execution tests only"
            echo "  ./run_tests.sh -f          # Run unit tests and integration tests"
            echo "  ./run_tests.sh --all       # Run all tests (unit, integration, real)"
            echo "  ./run_tests.sh -h          # Show this help message"
            exit 0
            ;;
        *)
            # Unknown option
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
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

# Configure test environment variables
if [ "$RUN_INTEGRATION_TESTS" -eq 1 ]; then
    print_status "Integration tests enabled..."
    export GITHUB_TEST_INTEGRATION=1
else
    export GITHUB_TEST_INTEGRATION=0
fi

# Set paths for test results
mkdir -p test_results

# Function to run tests and collect results
run_tests() {
    local test_path=$1
    local test_name=$2
    
    print_status "Running $test_name tests..."
    $PYTHON_CMD -m pytest $test_path \
        --html=test_results/report_${test_name}.html \
        --cov=$MODULE_NAME \
        --cov-report=html:test_results/coverage_${test_name} \
        --cov-append \
        -v || {
        print_error "Some $test_name tests failed."
        TEST_STATUS=1  # Set error status but continue to show report
    }
}

# Clear coverage data before starting
coverage erase 2>/dev/null || true

# Run unit tests if enabled
if [ "$RUN_UNIT_TESTS" -eq 1 ]; then
    run_tests "test/unit" "unit"
fi

# Run integration tests if enabled
if [ "$RUN_INTEGRATION_TESTS" -eq 1 ]; then
    run_tests "test/integration" "integration"
fi

# Check if real execution tests are enabled
if [ "$RUN_REAL_EXECUTION" -eq 1 ]; then
    print_warning "=========================================================================="
    print_warning "CAUTION: You are about to run REAL EXECUTION tests"
    print_warning "These tests will perform ACTUAL repository transfers between organizations"
    print_warning "Make sure you have run setup_test_repos.sh to create the test repositories"
    print_warning "=========================================================================="
    
    # Confirm with the user before proceeding
    read -p "Do you want to continue? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Aborted by user."
        exit 0
    fi
    
    # Check if GITHUB_TOKEN environment variable is set
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN environment variable is required for real execution tests."
        print_error "Please set it in your .env file or export it before running the tests."
        exit 1
    fi
    
    # Check if the test organizations are properly configured
    if [ -z "$TEST_ORG_1" ] || [ -z "$TEST_ORG_2" ] || [ -z "$TEST_USER" ]; then
        print_error "TEST_ORG_1, TEST_ORG_2, and TEST_USER must be set for real execution tests."
        print_error "Please set them in your .env file or export them before running the tests."
        exit 1
    fi
    
    export GITHUB_TEST_REAL_EXECUTION=1
    run_tests "test/real_execution" "real_execution"
else
    export GITHUB_TEST_REAL_EXECUTION=0
fi

# Generate combined report
if [ -d "test_results/coverage_unit" ] || [ -d "test_results/coverage_integration" ] || [ -d "test_results/coverage_real_execution" ]; then
    # Combine coverage data
    $PYTHON_CMD -m coverage html -d test_results/coverage_combined
    
    # Check if the coverage report was generated
    if [ -f "test_results/coverage_combined/index.html" ]; then
        coverage_percentage=$(grep -o "total.*%" test_results/coverage_combined/index.html | grep -o "[0-9]\+%" | head -1)
        print_status "Test coverage: $coverage_percentage"
    else
        print_warning "Combined coverage report was not generated."
    fi
else
    print_warning "No coverage reports were generated."
fi

# Deactivate virtual environment
deactivate

if [ -n "$TEST_STATUS" ]; then
    print_warning "Testing completed with some failures. Reports available in test_results directory."
else
    print_status "Testing completed successfully. Reports available in test_results directory."
fi

# List all generated reports
print_status "Generated test reports:"
if [ "$RUN_UNIT_TESTS" -eq 1 ]; then
    print_status "- Unit tests HTML report: test_results/report_unit.html"
fi
if [ "$RUN_INTEGRATION_TESTS" -eq 1 ]; then
    print_status "- Integration tests HTML report: test_results/report_integration.html"
fi
if [ "$RUN_REAL_EXECUTION" -eq 1 ]; then
    print_status "- Real execution tests HTML report: test_results/report_real_execution.html"
fi
print_status "- Combined coverage report: test_results/coverage_combined/index.html"

# Exit with the test status
exit ${TEST_STATUS:-0}
