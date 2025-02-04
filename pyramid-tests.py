import os
import re
import math

def count_tests(directory, file_patterns=None, file_content_patterns=None, test_patterns=None):
    test_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file_patterns is None or any(re.match(pattern, file) for pattern in file_patterns):
                file_path = os.path.join(root, file)
                if file_content_patterns:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if not any(re.search(pattern, content) for pattern in file_content_patterns):
                            continue
                if test_patterns:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in test_patterns:
                            test_count += len(re.findall(pattern, content, re.MULTILINE))
                else:
                    test_count += 1
    return test_count

def generate_test_pyramid(repo):
    total_tests = 0
    test_counts = {}
    
    for layer in repo['layers']:
        count = count_tests(
            layer['path'], 
            layer.get('file_patterns'),
            layer.get('file_content_patterns'), 
            layer.get('test_patterns')
        )
        test_counts[layer['name']] = count
        total_tests += count

    print(f"\n{repo['name']}:")
    print("\n")

    max_width = 60
    layer_count = len(repo['layers'])
    
    for i, layer in enumerate(reversed(repo['layers'])):
        layer_name = layer['name']
        count = test_counts[layer_name]
        percentage = (count / total_tests) * 100 if total_tests > 0 else 0
        width = math.ceil(percentage / 100 * max_width)
        
        print(f"{'#' * width:^60} | {count:4d} {layer_name}")
        if i < layer_count - 1:
            print(f"{'-' * 60}")

    print(f"\nTotal tests: {total_tests}")
    for layer in repo['layers']:
        layer_name = layer['name']
        count = test_counts[layer_name]
        percentage = (count / total_tests) * 100 if total_tests > 0 else 0
        print(f"{layer_name}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    repos = [
        {
            'name': 'user-service',
            'layers': [
                {
                    'name': 'Unit',
                    'path': './user-service/api/src/test/java/com/sample/userservice',
                    'file_patterns': [r'.*\.java$',],
                    'test_patterns': [r'@Test', r'@ParameterizedTest']
                },
                {
                    'name': 'Component',
                    'path': './user-service/api/src/test/java/com/sample/userservice',
                    'file_patterns': [r'.*\.java$',],
                    'file_content_patterns': [r'@SpringBootTest', r'@WebMvcTest', r'@RestClientTest', r'@DataMongoTest',  r'@DataJpaTest'],
                    'test_patterns': [r'@Test']
                },
                {
                    'name': 'Integration',
                    'path': './user-service/integration-tests/src/test/java/com/sample/integration/userservice/wiremock',
                    'file_patterns': [r'.*\.feature$'],
                    'test_patterns': [r'^\s*Scenario:']
                },
                {
                    'name': 'E2E',
                    'path': './user-e2e-tests/e2e-newman/tests'
                }
            ]
        }
    ]

    for repo in repos:
        generate_test_pyramid(repo)