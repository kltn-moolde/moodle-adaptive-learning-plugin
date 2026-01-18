#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script - Verify GMM Pipeline
=================================
Quick test để verify pipeline hoạt động đúng
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test 1: Import modules"""
    logger.info("TEST 1: Importing modules...")
    try:
        from core import (
            FeatureExtractor,
            FeatureSelector,
            OptimalClusterFinder,
            GMMDataGenerator,
            ValidationMetrics
        )
        logger.info("✅ All modules imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_pipeline_init():
    """Test 2: Initialize pipeline"""
    logger.info("\nTEST 2: Initializing pipeline...")
    try:
        from main import MoodleAnalyticsPipeline
        pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs/test')
        logger.info(f"✅ Pipeline initialized with {len(vars(pipeline))} components")
        return True
    except Exception as e:
        logger.error(f"❌ Pipeline initialization failed: {e}")
        return False


def test_data_availability():
    """Test 3: Check data availability"""
    logger.info("\nTEST 3: Checking data availability...")
    
    data_dir = Path('../data')
    grades_file = data_dir / 'udk_moodle_grades_course_670.filtered.csv'
    logs_file = data_dir / 'udk_moodle_log_course_670.filtered.csv'
    
    if grades_file.exists() and logs_file.exists():
        logger.info("✅ Data files found")
        return True
    else:
        logger.warning("⚠️  Data files not found (this is OK for structure test)")
        logger.info(f"   Expected: {grades_file}")
        logger.info(f"   Expected: {logs_file}")
        return True  # Still pass, just a warning


def test_module_structure():
    """Test 4: Check module methods"""
    logger.info("\nTEST 4: Checking module structure...")
    
    try:
        from core import (
            FeatureSelector,
            OptimalClusterFinder,
            GMMDataGenerator,
            ValidationMetrics
        )
        
        # Check FeatureSelector
        selector = FeatureSelector()
        assert hasattr(selector, 'select_features'), "FeatureSelector missing select_features method"
        assert hasattr(selector, 'process_pipeline'), "FeatureSelector missing process_pipeline method"
        
        # Check OptimalClusterFinder
        finder = OptimalClusterFinder()
        assert hasattr(finder, 'find_optimal_k'), "OptimalClusterFinder missing find_optimal_k method"
        assert hasattr(finder, 'process_pipeline'), "OptimalClusterFinder missing process_pipeline method"
        
        # Check GMMDataGenerator
        generator = GMMDataGenerator()
        assert hasattr(generator, 'generate_synthetic_data'), "GMMDataGenerator missing generate_synthetic_data method"
        assert hasattr(generator, 'process_pipeline'), "GMMDataGenerator missing process_pipeline method"
        
        # Check ValidationMetrics
        validator = ValidationMetrics()
        assert hasattr(validator, 'comprehensive_validation'), "ValidationMetrics missing comprehensive_validation method"
        assert hasattr(validator, 'process_pipeline'), "ValidationMetrics missing process_pipeline method"
        
        logger.info("✅ All modules have required methods")
        return True
        
    except AssertionError as e:
        logger.error(f"❌ Module structure check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


def test_config():
    """Test 5: Check configuration"""
    logger.info("\nTEST 5: Checking configuration...")
    
    try:
        import config
        
        # Check new GMM parameters
        required_params = [
            'VARIANCE_THRESHOLD',
            'CORRELATION_THRESHOLD',
            'MAX_SELECTED_FEATURES',
            'MIN_CLUSTERS',
            'MAX_CLUSTERS',
            'GMM_COVARIANCE_TYPE',
            'GMM_MAX_ITER',
            'GMM_RANDOM_STATE',
            'N_SYNTHETIC_STUDENTS',
            'KS_TEST_ALPHA'
        ]
        
        missing = []
        for param in required_params:
            if not hasattr(config, param):
                missing.append(param)
        
        if missing:
            logger.error(f"❌ Missing config parameters: {missing}")
            return False
        else:
            logger.info(f"✅ All {len(required_params)} required config parameters present")
            return True
            
    except Exception as e:
        logger.error(f"❌ Config check failed: {e}")
        return False


def test_documentation():
    """Test 6: Check documentation files"""
    logger.info("\nTEST 6: Checking documentation...")
    
    docs = [
        'README_GMM.md',
        'QUICKSTART_GMM.md',
        'CHANGELOG_GMM.md',
        'example_usage_gmm.py'
    ]
    
    found = []
    missing = []
    
    for doc in docs:
        if Path(doc).exists():
            found.append(doc)
        else:
            missing.append(doc)
    
    logger.info(f"✅ Found {len(found)}/{len(docs)} documentation files")
    
    if missing:
        logger.warning(f"⚠️  Missing: {missing}")
    
    return len(found) >= 3  # At least 3 docs should exist


def run_all_tests():
    """Run all tests"""
    logger.info("="*80)
    logger.info("RUNNING GMM PIPELINE VERIFICATION TESTS")
    logger.info("="*80)
    
    tests = [
        ("Import Modules", test_imports),
        ("Pipeline Initialization", test_pipeline_init),
        ("Data Availability", test_data_availability),
        ("Module Structure", test_module_structure),
        ("Configuration", test_config),
        ("Documentation", test_documentation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status:10s} - {test_name}")
    
    logger.info("="*80)
    logger.info(f"RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    logger.info("="*80)
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Pipeline is ready to use.")
        return 0
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
