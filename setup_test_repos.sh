#!/bin/bash
# Setup test repositories for GitHub Repository Transfer Tool tests

# This script uses curl to interact with GitHub API
# Usage: ./setup_test_repos.sh [org1] [org2]
#   If org1 and org2 are not provided, values from .env file will be used

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

# Source environment variables from .env file if it exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env file..."
    source .env
else
    print_warning "No .env file found. You can create one from .env.template"
    print_warning "cp .env.template .env && nano .env"
fi

# Check arguments or use environment variables
if [ $# -eq 2 ]; then
    # Command-line arguments provided, use them
    ORG1=$1
    ORG2=$2
    print_status "Using organizations from command-line arguments: $ORG1 and $ORG2"
elif [ $# -eq 0 ]; then
    # No arguments provided, try to use values from .env
    ORG1=${TEST_ORG_1:-""}
    ORG2=${TEST_ORG_2:-""}
    
    if [ -z "$ORG1" ] || [ -z "$ORG2" ]; then
        print_error "Organization names not provided and not found in .env file"
        print_error "Usage: $0 [org1] [org2]"
        print_error "Or set TEST_ORG_1 and TEST_ORG_2 in .env file"
        exit 1
    fi
    
    print_status "Using organizations from .env file: $ORG1 and $ORG2"
else
    print_error "Invalid number of arguments."
    print_error "Usage: $0 [org1] [org2]"
    print_error "Or set TEST_ORG_1 and TEST_ORG_2 in .env file"
    exit 1
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install it to use this script."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "git is not installed. Please install it to use this script."
    exit 1
fi

# Get GitHub token from environment
GITHUB_TOKEN=${GITHUB_TOKEN:-""}
if [ -z "$GITHUB_TOKEN" ]; then
    print_warning "GitHub Personal Access Token not found in environment or .env file."
    print_warning "Please enter your GitHub Personal Access Token with 'repo' and 'delete_repo' scopes:"
    read -r -s GITHUB_TOKEN
    echo "" # New line after hidden input
    
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "No token provided. Exiting."
        exit 1
    fi
fi

# Test the token by getting user info
print_status "Validating GitHub token..."
USER_DATA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                 -H "Accept: application/vnd.github.v3+json" \
                 https://api.github.com/user)

if echo "$USER_DATA" | grep -q "Bad credentials"; then
    print_error "Invalid GitHub token. Please check your token and try again."
    exit 1
fi

# Get username from the API response
GITHUB_USERNAME=$(echo "$USER_DATA" | grep '"login"' | head -n 1 | cut -d'"' -f4)
if [ -z "$GITHUB_USERNAME" ]; then
    print_error "Failed to get GitHub username. Check your token permissions."
    exit 1
fi

print_status "Authenticated as GitHub user: $GITHUB_USERNAME"

# Validate organizations exist before proceeding
print_status "Validating organizations..."
for org in "$ORG1" "$ORG2"; do
    org_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                        -H "Accept: application/vnd.github.v3+json" \
                        "https://api.github.com/orgs/$org")
    
    if echo "$org_response" | grep -q "Not Found"; then
        print_error "Organization $org does not exist or you don't have access to it."
        print_error "Please check the organization name and your permissions."
        exit 1
    else
        print_status "Organization $org is valid and accessible."
    fi
done

print_status "Setting up test repositories in organizations: $ORG1 and $ORG2"

# Function to create a repository
create_repo() {
    local org=$1
    local repo=$2
    local visibility=$3
    
    print_status "Creating repository: $org/$repo ($visibility)"
    
    # Check if repository exists
    repo_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                        -H "Accept: application/vnd.github.v3+json" \
                        "https://api.github.com/repos/$org/$repo")
    
    # Delete if exists
    if ! echo "$repo_response" | grep -q "Not Found"; then
        print_warning "Repository already exists. Deleting it first..."
        delete_response=$(curl -s -X DELETE \
                              -H "Authorization: token $GITHUB_TOKEN" \
                              -H "Accept: application/vnd.github.v3+json" \
                              "https://api.github.com/repos/$org/$repo")
        
        if [ $? -ne 0 ]; then
            print_warning "Failed to delete existing repository. It might be protected or you lack permissions."
            print_warning "Attempting to continue anyway..."
        fi
    fi
    
    # Create repository with API
    create_payload="{\"name\":\"$repo\",\"private\":$([ "$visibility" == "private" ] && echo "true" || echo "false")}"
    create_response=$(curl -s -X POST \
                         -H "Authorization: token $GITHUB_TOKEN" \
                         -H "Accept: application/vnd.github.v3+json" \
                         -d "$create_payload" \
                         "https://api.github.com/orgs/$org/repos")
    
    if echo "$create_response" | grep -q "errors"; then
        print_error "Failed to create repository: $org/$repo"
        print_error "API Error: $(echo "$create_response" | grep -o '"message":"[^"]*"')"
        return 1
    fi
    
    # Clone repository
#     temp_dir=$(mktemp -d)
#     print_status "Cloning repository to temporary directory: $temp_dir"
    
#     # Use the token for git clone to avoid authentication issues
#     git clone "https://$GITHUB_TOKEN@github.com/$org/$repo.git" "$temp_dir" || {
#         print_error "Failed to clone repository. Skipping content creation."
#         return 1
#     }
    
#     cd "$temp_dir"
    
#     # Configure git (in case it's not configured)
#     if ! git config --get user.email &> /dev/null || ! git config --get user.name &> /dev/null; then
#         print_warning "Git user identity not configured. Setting up temporary identity..."
#         git config --local user.email "test@example.com"
#         git config --local user.name "Test User"
#     fi
    
#     # Add some content
#     echo "# Test Repository: $repo" > README.md
#     echo "This is a test repository for the GitHub Repository Transfer Tool." >> README.md
#     echo "Created on: $(date)" >> README.md
    
#     # Create different content based on repo type
#     case "$repo" in
#         "test-with-branches")
#             git add README.md
#             git commit -m "Initial commit" || {
#                 print_error "Failed to create initial commit. Check git configuration."
#                 cd - > /dev/null
#                 rm -rf "$temp_dir"
#                 return 1
#             }
#             git push || {
#                 print_error "Failed to push initial commit."
#                 cd - > /dev/null
#                 rm -rf "$temp_dir"
#                 return 1
#             }
            
#             # Create branches
#             print_status "Creating branches for $org/$repo"
#             git checkout -b develop
#             echo "# Develop Branch" > DEVELOP.md
#             echo "This file exists only in the develop branch" >> DEVELOP.md
#             git add DEVELOP.md
#             git commit -m "Add develop branch"
#             git push --set-upstream origin develop || print_warning "Failed to push develop branch."
            
#             git checkout -b feature
#             echo "# Feature Branch" > FEATURE.md
#             echo "This file exists only in the feature branch" >> FEATURE.md
#             git add FEATURE.md
#             git commit -m "Add feature branch"
#             git push --set-upstream origin feature || print_warning "Failed to push feature branch."
#             ;;
            
#         "test-with-issues")
#             git add README.md
#             git commit -m "Initial commit"
#             git push || {
#                 print_error "Failed to push initial commit."
#                 cd - > /dev/null
#                 rm -rf "$temp_dir"
#                 return 1
#             }
            
#             # Create issues using the GitHub API
#             print_status "Creating issues for $org/$repo"
            
#             # Issue 1
#             issue1_payload='{"title":"Test Issue 1","body":"This is a test issue."}'
#             curl -s -X POST \
#                 -H "Authorization: token $GITHUB_TOKEN" \
#                 -H "Accept: application/vnd.github.v3+json" \
#                 -d "$issue1_payload" \
#                 "https://api.github.com/repos/$org/$repo/issues" > /dev/null || print_warning "Failed to create Issue 1."
            
#             # Issue 2
#             issue2_payload='{"title":"Test Issue 2","body":"This is another test issue."}'
#             curl -s -X POST \
#                 -H "Authorization: token $GITHUB_TOKEN" \
#                 -H "Accept: application/vnd.github.v3+json" \
#                 -d "$issue2_payload" \
#                 "https://api.github.com/repos/$org/$repo/issues" > /dev/null || print_warning "Failed to create Issue 2."
#             ;;
            
#         "test-with-actions")
#             # Create a simple GitHub Actions workflow
#             print_status "Setting up GitHub Actions workflow for $org/$repo"
#             mkdir -p .github/workflows
#             cat > .github/workflows/ci.yml << 'EOF'
# name: CI

# on:
#   push:
#     branches: [ main ]
#   pull_request:
#     branches: [ main ]

# jobs:
#   test:
#     runs-on: ubuntu-latest
#     steps:
#     - uses: actions/checkout@v2
#     - name: Echo test
#       run: echo "This is a test workflow"
# EOF
#             git add README.md .github/workflows/ci.yml
#             git commit -m "Initial commit with GitHub Actions"
#             git push || {
#                 print_error "Failed to push GitHub Actions workflow."
#                 cd - > /dev/null
#                 rm -rf "$temp_dir"
#                 return 1
#             }
#             ;;
            
#         *)
#             # Default repository just with README
#             git add README.md
#             git commit -m "Initial commit"
#             git push || {
#                 print_error "Failed to push initial commit."
#                 cd - > /dev/null
#                 rm -rf "$temp_dir"
#                 return 1
#             }
#             ;;
#     esac
    
    # Clean up
    cd - > /dev/null
    rm -rf "$temp_dir"
    
    print_status "Repository created successfully: $org/$repo"
    return 0
}

# Generate a timestamp suffix for uniqueness
TIMESTAMP="20250603"
print_status "Using hardcoded timestamp suffix for unique repositories: $TIMESTAMP"

# Create repositories in first organization
print_status "Creating repositories in nova-iris..."
create_repo "nova-iris" "test-empty-org1-$TIMESTAMP" "private" || print_warning "Failed to create test-empty-org1-$TIMESTAMP in nova-iris"
create_repo "nova-iris" "test-public-org1-$TIMESTAMP" "public" || print_warning "Failed to create test-public-org1-$TIMESTAMP in nova-iris"
create_repo "nova-iris" "test-private-org1-$TIMESTAMP" "private" || print_warning "Failed to create test-private-org1-$TIMESTAMP in nova-iris"
create_repo "nova-iris" "test-with-branches-org1-$TIMESTAMP" "private" || print_warning "Failed to create test-with-branches-org1-$TIMESTAMP in nova-iris"
create_repo "nova-iris" "test-with-issues-org1-$TIMESTAMP" "private" || print_warning "Failed to create test-with-issues-org1-$TIMESTAMP in nova-iris"
create_repo "nova-iris" "test-with-actions-org1-$TIMESTAMP" "private" || print_warning "Failed to create test-with-actions-org1-$TIMESTAMP in nova-iris"

# Create repositories in second organization
print_status "Creating repositories in baohtruong..."
create_repo "baohtruong" "test-empty-org2-$TIMESTAMP" "private" || print_warning "Failed to create test-empty-org2-$TIMESTAMP in baohtruong"
create_repo "baohtruong" "test-public-org2-$TIMESTAMP" "public" || print_warning "Failed to create test-public-org2-$TIMESTAMP in baohtruong"
create_repo "baohtruong" "test-private-org2-$TIMESTAMP" "private" || print_warning "Failed to create test-private-org2-$TIMESTAMP in baohtruong"

print_status "Test repositories setup completed."
print_status "==============================================================="
print_status "IMPORTANT: The following values are being used:"
echo ""
echo "TEST_ORG_1 = \"nova-iris\"  # First organization"
echo "TEST_ORG_2 = \"baohtruong\"  # Second organization"
echo "TEST_USER = \"$GITHUB_USERNAME\"  # Your GitHub username"
echo "TEST_REPO_SUFFIX = \"$TIMESTAMP\"  # Timestamp suffix for unique repo names"
echo ""

# Ask if the user wants to update the .env file
read -p "Do you want to save these values to .env file? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f ".env" ]; then
        # Backup existing .env file
        cp .env ".env.bak.$(date +%Y%m%d%H%M%S)"
        print_status "Existing .env file backed up."
        
        # Update the values in .env file
        sed -i "s/^TEST_ORG_1=.*/TEST_ORG_1=nova-iris/" .env
        sed -i "s/^TEST_ORG_2=.*/TEST_ORG_2=baohtruong/" .env
        sed -i "s/^TEST_USER=.*/TEST_USER=$GITHUB_USERNAME/" .env
        
        # Add or update the TEST_REPO_SUFFIX in .env
        if grep -q "^TEST_REPO_SUFFIX=" .env; then
            sed -i "s/^TEST_REPO_SUFFIX=.*/TEST_REPO_SUFFIX=$TIMESTAMP/" .env
        else
            echo "TEST_REPO_SUFFIX=$TIMESTAMP" >> .env
        fi
    else
        # Create new .env file from template if it exists
        if [ -f ".env.template" ]; then
            cp .env.template .env
            sed -i "s/^TEST_ORG_1=.*/TEST_ORG_1=nova-iris/" .env
            sed -i "s/^TEST_ORG_2=.*/TEST_ORG_2=baohtruong/" .env
            sed -i "s/^TEST_USER=.*/TEST_USER=$GITHUB_USERNAME/" .env
            sed -i "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=$GITHUB_TOKEN/" .env
        else
            # Create minimal .env file
            cat > ".env" << EOF
# GitHub Repository Transfer Tool - Environment Configuration
GITHUB_TOKEN=$GITHUB_TOKEN
TEST_ORG_1=nova-iris
TEST_ORG_2=baohtruong
TEST_USER=$GITHUB_USERNAME
TEST_REPO_SUFFIX=$TIMESTAMP
TEST_REPO=test-public-org1-$TIMESTAMP
EOF
        fi
    fi
    print_status "Values saved to .env file."
fi

print_status "==============================================================="
print_status "You can now run the tests with: ./run_tests.sh"

# Create a sample CSV file for testing
SAMPLE_CSV="sample_repos.csv"
print_status "Creating sample CSV file for testing: $SAMPLE_CSV"

# Backup existing file if it exists
if [ -f "$SAMPLE_CSV" ]; then
    mv "$SAMPLE_CSV" "${SAMPLE_CSV}.bak.$(date +%Y%m%d%H%M%S)"
    print_warning "Existing $SAMPLE_CSV backed up."
fi

# Create the CSV file
cat > "$SAMPLE_CSV" << EOF
source_org,repo_name,dest_org
nova-iris,test-empty-org1-$TIMESTAMP,baohtruong
nova-iris,test-public-org1-$TIMESTAMP,baohtruong
nova-iris,test-private-org1-$TIMESTAMP,baohtruong
nova-iris,test-with-branches-org1-$TIMESTAMP,baohtruong
nova-iris,test-with-issues-org1-$TIMESTAMP,baohtruong
nova-iris,test-with-actions-org1-$TIMESTAMP,baohtruong
baohtruong,test-empty-org2-$TIMESTAMP,nova-iris
baohtruong,test-public-org2-$TIMESTAMP,nova-iris
baohtruong,test-private-org2-$TIMESTAMP,nova-iris
EOF

print_status "Sample CSV file created: $SAMPLE_CSV"
print_status "==============================================================="
