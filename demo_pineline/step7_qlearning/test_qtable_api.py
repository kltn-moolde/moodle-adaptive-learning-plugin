#!/usr/bin/env python3
"""
Test Q-Table Information APIs
"""

import requests
import json

API_BASE = "http://localhost:8080/api"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_qtable_info():
    """Test GET /api/qtable/info"""
    print_section("1. Q-TABLE INFO (Metadata)")
    
    response = requests.get(f"{API_BASE}/qtable/info")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📦 Q-TABLE METADATA:")
        meta = data['qtable_metadata']
        print(f"   Total states: {meta['total_states']:,}")
        print(f"   Total actions: {meta['total_actions']}")
        print(f"   State dimension: {meta['state_dimension']}")
        print(f"   Total state-action pairs: {meta['total_state_action_pairs']:,}")
        print(f"   Sparsity: {meta['sparsity']:.2%}")
        print(f"   Estimated memory: {meta['estimated_memory_mb']:.2f} MB")
        
        print("\n🎯 STATE SPACE:")
        state = data['state_space']
        print(f"   Dimension: {state['dimension']}")
        print(f"   Total states: {state['total_states']:,}")
        print(f"   Format: {state['state_format']}")
        print(f"   Discretization: {state['discretization']}")
        print(f"   Features ({len(state['features'])}):")
        for i, feat in enumerate(state['features'], 1):
            print(f"      {i}. {feat}")
        
        print("\n🎬 ACTION SPACE:")
        action = data['action_space']
        print(f"   Total actions: {action['total_actions']}")
        print(f"   Action IDs: {action['action_ids'][:10]}..." if len(action['action_ids']) > 10 else f"   Action IDs: {action['action_ids']}")
        print(f"   Format: {action['action_format']}")
        
        print("\n⚙️ HYPERPARAMETERS:")
        for key, value in data['hyperparameters'].items():
            print(f"   {key}: {value}")
        
        print("\n📈 TRAINING INFO:")
        for key, value in data['training_info'].items():
            print(f"   {key}: {value:,}" if isinstance(value, int) else f"   {key}: {value}")
        
        print("\n✅ Q-Table info retrieved successfully")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False


def test_qtable_summary():
    """Test GET /api/qtable/summary"""
    print_section("1. Q-TABLE SUMMARY")
    
    response = requests.get(f"{API_BASE}/qtable/summary")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📊 MODEL INFO:")
        for key, value in data['model_info'].items():
            print(f"   {key}: {value}")
        
        print("\n📈 TRAINING STATS:")
        for key, value in data['training_stats'].items():
            print(f"   {key}: {value:,}" if isinstance(value, int) else f"   {key}: {value}")
        
        print("\n📋 Q-TABLE STATS:")
        qtable = data['qtable_stats']
        print(f"   Total states: {qtable['total_states']:,}")
        print(f"   States with Q>0: {qtable['states_with_nonzero_q']:,}")
        print(f"   State dimension: {qtable['state_dimension']}")
        
        print("\n   Q-Value Distribution:")
        dist = qtable['q_value_distribution']
        print(f"     Positive: {dist['positive_count']:,} ({dist['positive_percentage']:.1f}%)")
        print(f"     Zero: {dist['zero_count']:,} ({dist['zero_percentage']:.1f}%)")
        print(f"     Range: [{dist['min']:.4f}, {dist['max']:.4f}]")
        print(f"     Mean: {dist['mean']:.4f}, Std: {dist['std']:.4f}")
        
        print("\n   Dimension Stats (first 3):")
        for dim in data['dimension_stats'][:3]:
            print(f"     Dim {dim['dimension']}: {dim['unique_values']} unique values, "
                  f"range [{dim['min']:.2f}, {dim['max']:.2f}]")
        
        print("\n✅ Summary retrieved successfully")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")


def test_positive_states():
    """Test GET /api/qtable/states/positive"""
    print_section("2. STATES WITH POSITIVE Q-VALUES")
    
    response = requests.get(f"{API_BASE}/qtable/states/positive?top_n=5")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Found {data['total_states']} states")
        print(f"\nTOP 5 STATES (Q-value > 0):\n")
        
        for state in data['states']:
            print(f"#{state['rank']} — Q-value: {state['q_info']['max_q_value']:.4f}")
            print(f"   Best action: {state['q_info']['best_action_id']}")
            print(f"   Features: {json.dumps(state['features'], indent=6)}\n")
        
        # Save first state for copy-paste
        if data['states']:
            first_state = data['states'][0]
            print("💡 COPY-PASTE READY (First state):")
            print(json.dumps(first_state['features'], indent=2))
    else:
        print(f"❌ Error {response.status_code}: {response.text}")


def test_diverse_samples():
    """Test GET /api/qtable/states/diverse"""
    print_section("3. DIVERSE STATE SAMPLES")
    
    response = requests.get(f"{API_BASE}/qtable/states/diverse?n_samples=10")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Retrieved {data['total_samples']} diverse samples\n")
        
        for i, sample in enumerate(data['samples'], 1):
            print(f"{i}. Q-value: {sample['max_q_value']:.4f} (Percentile: {sample['percentile']})")
            print(f"   Features: {json.dumps(sample['features'], indent=6)}\n")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")


def test_basic_stats():
    """Test GET /api/qtable/stats"""
    print_section("4. BASIC Q-TABLE STATISTICS")
    
    response = requests.get(f"{API_BASE}/qtable/stats")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📊 BASIC STATS:")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value:,}")
        
        print("\n✅ Stats retrieved successfully")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")


def test_with_state():
    """Test recommendation with a state from Q-table"""
    print_section("5. TEST RECOMMENDATION WITH Q-TABLE STATE")
    
    # First get a state with positive Q
    response = requests.get(f"{API_BASE}/qtable/states/positive?top_n=1")
    
    if response.status_code != 200:
        print(f"❌ Failed to get test state: {response.text}")
        return
    
    data = response.json()
    if not data['states']:
        print("❌ No states with positive Q found")
        return
    
    test_state = data['states'][0]
    features = test_state['features']
    expected_q = test_state['q_info']['max_q_value']
    
    print(f"\n📤 Testing with state (Expected Q: {expected_q:.4f})")
    print(f"Features: {json.dumps(features, indent=2)}")
    
    # Make recommendation request
    recommend_request = {
        "student_id": 99999,
        "features": features,
        "top_k": 3
    }
    
    response = requests.post(f"{API_BASE}/recommend", json=recommend_request)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Recommendation received:")
        print(f"   Cluster: {result['cluster_name']} (ID: {result['cluster_id']})")
        
        print(f"\n   Top 3 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec['name']} (Q-value: {rec['q_value']:.4f})")
            print(f"      Type: {rec['type']}, Difficulty: {rec['difficulty']}")
        
        # Compare Q-values
        if result['recommendations']:
            actual_q = result['recommendations'][0]['q_value']
            print(f"\n   Expected Q: {expected_q:.4f}")
            print(f"   Actual Q:   {actual_q:.4f}")
            
            if abs(expected_q - actual_q) < 0.01:
                print("   ✅ Q-values match!")
            else:
                print(f"   ⚠️  Q-values differ by {abs(expected_q - actual_q):.4f}")
    else:
        print(f"❌ Recommendation failed: {response.text}")


def generate_test_file():
    """Generate JSON file with ready-to-use test cases"""
    print_section("6. GENERATE TEST CASES FILE")
    
    response = requests.get(f"{API_BASE}/qtable/states/positive?top_n=10")
    
    if response.status_code != 200:
        print(f"❌ Failed to get states: {response.text}")
        return
    
    data = response.json()
    
    # Create test cases
    test_cases = []
    for state in data['states']:
        test_cases.append({
            "test_name": f"state_rank_{state['rank']}",
            "description": f"State with Q-value {state['q_info']['max_q_value']:.4f}",
            "features": state['features'],
            "expected_q_value": state['q_info']['max_q_value'],
            "expected_best_action": state['q_info']['best_action_id']
        })
    
    # Save to file
    output_file = "qtable_test_cases.json"
    with open(output_file, 'w') as f:
        json.dump(test_cases, f, indent=2)
    
    print(f"\n✅ Generated {len(test_cases)} test cases")
    print(f"   Saved to: {output_file}")
    
    # Print first case as example
    if test_cases:
        print(f"\n💡 Example test case:")
        print(json.dumps(test_cases[0], indent=2))


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  🧪 Q-TABLE INFORMATION API TESTS")
    print("=" * 80)
    print("\n📡 API Base URL:", API_BASE)
    
    try:
        # Test all endpoints
        test_qtable_info()          # NEW: Test Q-table metadata
        test_qtable_summary()
        test_positive_states()
        test_diverse_samples()
        test_basic_stats()
        test_with_state()
        generate_test_file()
        
        print("\n" + "=" * 80)
        print("  ✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
        print("\n💡 Available Endpoints:")
        print("   GET  /api/qtable/info              - Q-table metadata & structure")
        print("   GET  /api/qtable/summary           - Full Q-table analysis")
        print("   GET  /api/qtable/states/positive   - States with Q>0")
        print("   GET  /api/qtable/states/diverse    - Diverse samples")
        print("   GET  /api/qtable/stats             - Basic statistics")
        
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 80)
        print("  ❌ CONNECTION ERROR")
        print("=" * 80)
        print("\nCannot connect to API. Please start the server first:")
        print("  uvicorn api_service:app --reload --port 8080")


if __name__ == '__main__':
    main()
