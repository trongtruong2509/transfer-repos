## Repository Transfer Validation Results

The following repositories were validated for transfer:

| Source Org | Repository | Destination Org | Status |
|------------|------------|-----------------|--------|
| nova-iris | test-empty-org1-20250603 | baohtru | ❌ Failed - Destination org invalid |
| nova-iris | test-public-org1-20250603 | baohtruong | ✅ Passed |
| nova-iris | test-private-org1-50603 | baohtruong | ❌ Failed - Repository not found |
| nova-iris | test-with-branches-org1-20250603 | baohtruong | ✅ Passed |
| nova-iris | test-with-issues-org1-20250603 | baohtruong | ✅ Passed |
| nova-s | test-with-actions-org1-20250603 | baohtruong | ❌ Failed - Source org invalid |
| baohtruong | test-empty-org2-20250603 | nova-iris | ✅ Passed |
| baohtruong | test-public-org2-20250603 | nova-iris | ✅ Passed |
| baohtruong | test-private-org2-20250603 | nova-iris | ✅ Passed |

### Error Details

- **nova-iris/test-empty-org1-20250603 → baohtru**: Destination organization not accessible: baohtru
- **nova-iris/test-private-org1-50603 → baohtruong**: Repository not accessible: nova-iris/test-private-org1-50603
- **nova-s/test-with-actions-org1-20250603 → baohtruong**: Source organization not accessible: nova-s

### Summary

- ✅ **Ready to transfer**: 6 repositories
- ❌ **Failed validation**: 3 repositories
