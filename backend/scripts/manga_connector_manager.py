#!/usr/bin/env python3
"""
Manga Connector Manager
- Scans for manga connectors with 'english' tag
- Tests connectivity to manga sites
- Infers API URIs for each connector
- Stores results in PostgreSQL database
"""

import os
import re
import json
import time
import argparse
import requests
import psycopg2
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# ========================
# Database Configuration
# ========================

DB_CONFIG = {
    'dbname': 'manga_connectors',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

def init_database(config=DB_CONFIG, drop_existing=False):
    """Initialize database schema for storing manga connector information"""
    conn = None
    try:
        # Connect to PostgreSQL server - first to postgres db to create our db if needed
        connect_params = config.copy()
        connect_params['dbname'] = 'postgres'  # Connect to default postgres db first
        conn = psycopg2.connect(**connect_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if our target database exists, create it if not
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config['dbname'],))
        if not cursor.fetchone():
            print(f"Creating database '{config['dbname']}'...")
            cursor.execute(f"CREATE DATABASE {config['dbname']}")
        
        # Close connection to postgres db
        cursor.close()
        conn.close()

        # Connect to our manga database
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()

        # Drop existing tables if requested
        if drop_existing:
            print("Dropping existing tables...")
            cursor.execute("DROP TABLE IF EXISTS connector_api_urls CASCADE")
            cursor.execute("DROP TABLE IF EXISTS connector_status_history CASCADE")
            cursor.execute("DROP TABLE IF EXISTS connectors CASCADE")

        # Create connectors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connectors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                base_url TEXT NOT NULL,
                tags TEXT[] NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (name)
            )
        """)

        # Create connector_status_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connector_status_history (
                id SERIAL PRIMARY KEY,
                connector_id INTEGER REFERENCES connectors(id),
                status_code INTEGER,
                response_time FLOAT,
                error_message TEXT,
                successful BOOLEAN NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create connector_api_urls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connector_api_urls (
                id SERIAL PRIMARY KEY,
                connector_id INTEGER REFERENCES connectors(id),
                api_url TEXT NOT NULL,
                api_type TEXT NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Database schema initialized successfully")
        return True

    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# ========================
# Connector Discovery
# ========================

def find_english_connectors(connectors_path):
    """
    Find all .mjs files in the connectors folder that have 'english' in this.tags
    
    Args:
        connectors_path: Path to the connectors directory
    
    Returns:
        List of connector info dictionaries
    """
    english_connectors = []
    
    print(f"Scanning {connectors_path} for English connectors...")
    
    # Walk through the connectors directory
    for root, dirs, files in os.walk(connectors_path):
        for file in files:
            if file.endswith('.mjs'):
                file_path = os.path.join(root, file)
                
                try:
                    # Read the file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract connector information
                    connector_info = extract_connector_info(content, file_path, file)
                    
                    # Check if this connector has the 'english' tag
                    if connector_info and 'english' in [tag.lower() for tag in connector_info['tags']]:
                        english_connectors.append(connector_info)
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Found {len(english_connectors)} English connectors")
    return english_connectors

def extract_connector_info(content, file_path, file_name):
    """Extract connector information from the file content"""
    info = {
        'name': file_name,
        'file_path': file_path,
        'url': None,
        'tags': []
    }
    
    # Extract URL
    url_pattern = r'this\.url\s*=\s*[\'"]([^\'"]+)[\'"]'
    url_match = re.search(url_pattern, content)
    if url_match:
        info['url'] = url_match.group(1)
    
    # Extract tags
    tags_pattern = r'this\.tags\s*=\s*\[(.*?)\]'
    tags_match = re.search(tags_pattern, content, re.DOTALL)
    if tags_match:
        tags_content = tags_match.group(1)
        # Extract each tag string within quotes
        tag_strings = re.findall(r'[\'"]([^\'"]*)[\'"]', tags_content)
        info['tags'] = tag_strings
    
    # Skip if we couldn't extract the URL
    if not info['url']:
        return None
        
    return info

# ========================
# Connectivity Testing
# ========================

def test_url_connection(connector, timeout=10):
    """Test connectivity to a URL"""
    url = connector['url']
    name = connector['name']
    file_path = connector['file_path']
    
    # Make sure URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc or parsed_url.path
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Host': domain
        }
        
        # Try to connect to the URL
        start_time = time.time()
        response = requests.get(url, timeout=timeout, headers=headers)
        elapsed_time = time.time() - start_time
        
        result = {
            'name': name,
            'file_path': file_path,
            'url': url,
            'status': response.status_code,
            'time': elapsed_time,
            'success': 200 <= response.status_code < 400,
            'error': None
        }
        
    except requests.RequestException as e:
        result = {
            'name': name,
            'file_path': file_path,
            'url': url,
            'status': 'Error',
            'time': 0,
            'success': False,
            'error': str(e)
        }
    
    # Print progress indicator
    status_color = '\033[92m' if result['success'] else '\033[91m'  # Green for success, red for failure
    reset_color = '\033[0m'
    print(f"{status_color}Testing {name}: {'✓' if result['success'] else '✗'}{reset_color}")
    
    return result

def test_connections(connectors, threads=10, timeout=10):
    """Test connections to all connectors in parallel"""
    print(f"Testing connectivity to {len(connectors)} URLs using {threads} threads...")
    results = []
    
    # Use ThreadPoolExecutor to test connections in parallel
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(test_url_connection, connector, timeout) for connector in connectors]
        
        for i, future in enumerate(futures):
            results.append(future.result())
            print(f"Progress: {i+1}/{len(futures)} URLs tested", end='\r')
    
    print("\nConnectivity testing completed")
    return results

# ========================
# API URI Generation
# ========================

def generate_api_uris(connector_results):
    """Generate likely API URIs for each connector"""
    # Common API patterns
    api_patterns = {
        'standard_api': '/api',
        'api_v1': '/api/v1',
        'api_v2': '/api/v2',
        'graphql': '/graphql',
        'json': '/json',
        'manga_api': '/manga/api',
        'comics_api': '/comics/api',
        'content_api': '/content/api',
        'search_api': '/api/search',
        'series_api': '/api/series',
        'chapters_api': '/api/chapters',
        'wp_admin_ajax': '/wp-admin/admin-ajax.php',
        'ajax_search': '/ajax/manga/search',
    }
    
    # Special cases for known sites
    special_cases = {
        'viz.com': [
            {'url': '/api/manga_data', 'type': 'manga_data'},
            {'url': '/api/manga_list', 'type': 'manga_list'}
        ],
        'webtoons.com': [
            {'url': '/en/api/episodes', 'type': 'episodes'},
            {'url': '/en/api/content', 'type': 'content'}
        ],
        'mangaplus.shueisha.co.jp': [
            {'url': '/api/title_detailV3', 'type': 'title_detail'},
            {'url': '/api/title_list', 'type': 'title_list'}
        ],
        'tappytoon.com': [
            {'url': '/api/comics', 'type': 'comics'}
        ],
        'tapas.io': [
            {'url': '/api/v2/story', 'type': 'story'},
            {'url': '/api/v2/series', 'type': 'series'}
        ],
        'lezhinus.com': [
            {'url': '/api/v2/comics', 'type': 'comics'},
            {'url': '/api/v2/episodes', 'type': 'episodes'}
        ],
        'webnovel.com': [
            {'url': '/apiajax/chapter/GetChapterList', 'type': 'chapters'}
        ],
        'manga4life.com': [
            {'url': '/search/search.php', 'type': 'search'},
            {'url': '/manga', 'type': 'manga_page'}
        ],
        'mangareader.to': [
            {'url': '/ajax/manga/search', 'type': 'search'},
            {'url': '/ajax/manga/list', 'type': 'list'}
        ],
        'manganato.gg': [
            {'url': '/ajax/manga/search', 'type': 'search'},
            {'url': '/ajax/manga/list', 'type': 'list'}
        ],
        'mangakakalot.gg': [
            {'url': '/ajax/manga/search', 'type': 'search'}
        ],
        'toonily.com': [
            {'url': '/wp-admin/admin-ajax.php', 'type': 'wp_ajax'}
        ],
    }

    enhanced_results = []
    
    for result in connector_results:
        api_uris = []
        url = result['url']
        
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check for special cases first
        for site_domain, endpoints in special_cases.items():
            if site_domain in domain:
                for endpoint in endpoints:
                    api_uris.append({
                        'url': f"{base_url}{endpoint['url']}",
                        'type': endpoint['type']
                    })
        
        # If no special case matched, use general patterns
        if not api_uris:
            # Generate APIs based on domain keywords
            site_type = None
            if 'manga' in domain.lower():
                site_type = 'manga'
                api_uris.append({
                    'url': f"{base_url}{api_patterns['manga_api']}",
                    'type': 'manga_api'
                })
            elif 'comic' in domain.lower():
                site_type = 'comics'
                api_uris.append({
                    'url': f"{base_url}{api_patterns['comics_api']}",
                    'type': 'comics_api'
                })
            elif any(x in domain.lower() for x in ['hentai', 'xxx', 'porn']):
                site_type = 'adult'
                api_uris.append({
                    'url': f"{base_url}{api_patterns['content_api']}",
                    'type': 'content_api'
                })
            
            # Always add standard API endpoints
            api_uris.append({
                'url': f"{base_url}{api_patterns['standard_api']}",
                'type': 'standard_api'
            })
            
            # Add WordPress ajax for common CMS sites
            if result['success']:
                api_uris.append({
                    'url': f"{base_url}{api_patterns['wp_admin_ajax']}",
                    'type': 'wp_ajax'
                })
        
        # Add APIs to result
        result['api_uris'] = api_uris
        enhanced_results.append(result)
        
    return enhanced_results

# ========================
# Database Operations
# ========================

def store_results_in_db(connectors, test_results, db_config=DB_CONFIG):
    """Store connector information and test results in the database"""
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        connectors_added = 0
        statuses_added = 0
        apis_added = 0
        
        # Process each test result
        for result in test_results:
            # Find the connector info for this result
            connector_info = next((c for c in connectors if c['name'] == result['name']), None)
            if not connector_info:
                print(f"Warning: No connector info found for {result['name']}")
                continue
                
            # Insert or update connector info
            cursor.execute("""
                INSERT INTO connectors (name, file_path, base_url, tags)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) 
                DO UPDATE SET 
                    file_path = EXCLUDED.file_path,
                    base_url = EXCLUDED.base_url,
                    tags = EXCLUDED.tags
                RETURNING id
            """, (
                result['name'],
                result['file_path'],
                result['url'],
                connector_info['tags']
            ))
            connector_id = cursor.fetchone()[0]
            connectors_added += 1
            
            # Insert connectivity test result
            status_code = result['status'] if isinstance(result['status'], int) else None
            cursor.execute("""
                INSERT INTO connector_status_history 
                (connector_id, status_code, response_time, error_message, successful)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                connector_id,
                status_code,
                result['time'],
                result['error'] if 'error' in result and result['error'] else None,
                result['success']
            ))
            statuses_added += 1
            
            # Insert API URLs if this result was successful
            if 'api_uris' in result:
                for api in result['api_uris']:
                    cursor.execute("""
                        INSERT INTO connector_api_urls
                        (connector_id, api_url, api_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        connector_id,
                        api['url'],
                        api['type']
                    ))
                    apis_added += 1
        
        print(f"Database updated: {connectors_added} connectors, {statuses_added} status records, {apis_added} API URLs")
        return True
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# ========================
# Main Functions
# ========================

def generate_report(test_results, output_file=None):
    """Generate a human-readable report of the test results"""
    # Sort results with successful connections first, then by response time
    sorted_results = sorted(test_results, key=lambda x: (not x['success'], x.get('time', float('inf'))))
    
    # Calculate statistics
    successful = sum(1 for r in test_results if r['success'])
    total = len(test_results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    # Build report
    report = []
    report.append("English Connector Status Report")
    report.append(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("-" * 100)
    report.append(f"{'Connector Name':<30} {'Status':<10} {'Time (s)':<10} {'URL':<50}")
    report.append("-" * 100)
    
    report.append("\nSUCCESSFUL CONNECTIONS:")
    for result in sorted_results:
        if result['success']:
            status = result['status']
            status_str = f"{status}" if isinstance(status, int) else status
            report.append(f"{result['name'][:30]:<30} {status_str:<10} {result['time']:.2f}s{' ':<6} {result['url'][:50]}")
    
    report.append("\nFAILED CONNECTIONS:")
    for result in sorted_results:
        if not result['success']:
            status = result['status']
            status_str = f"{status}" if isinstance(status, int) else status
            report.append(f"{result['name'][:30]:<30} {status_str:<10} {result['time']:.2f}s{' ':<6} {result['url'][:50]}")
            if 'error' in result and result['error']:
                report.append(f"    Error: {result['error']}")
    
    report.append("\n" + "-" * 100)
    report.append(f"Summary: {successful}/{total} connectors accessible ({success_rate:.1f}%)")
    
    # Write report to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in report:
                f.write(line + "\n")
        print(f"Report saved to {output_file}")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Manga Connector Manager")
    parser.add_argument('--path', '-p', required=True, help='Path to the connectors directory')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of threads for parallel testing')
    parser.add_argument('--timeout', type=int, default=15, help='Timeout in seconds for each request')
    parser.add_argument('--output', '-o', help='Output file for results (optional)')
    parser.add_argument('--db-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--db-port', default=5432, type=int, help='PostgreSQL port')
    parser.add_argument('--db-name', default='manga_connectors', help='PostgreSQL database name')
    parser.add_argument('--db-user', default='postgres', help='PostgreSQL username')
    parser.add_argument('--db-password', default='postgres', help='PostgreSQL password')
    parser.add_argument('--reset-db', action='store_true', help='Reset database schema')
    parser.add_argument('--no-db', action='store_true', help='Skip database operations')
    
    args = parser.parse_args()
    
    # Configure database connection
    db_config = {
        'dbname': args.db_name,
        'user': args.db_user,
        'password': args.db_password,
        'host': args.db_host,
        'port': args.db_port
    }
    
    # Initialize database if needed
    if not args.no_db:
        if not init_database(db_config, args.reset_db):
            print("Database initialization failed")
            if not args.output:  # If no output file is specified, exit
                return

    # Find English connectors
    connectors = find_english_connectors(args.path)
    
    if not connectors:
        print("No English connectors found. Exiting.")
        return
    
    # Test connections
    test_results = test_connections(connectors, args.threads, args.timeout)
    
    # Generate API URIs
    enhanced_results = generate_api_uris(test_results)
    
    # Store results in database
    if not args.no_db:
        if store_results_in_db(connectors, enhanced_results, db_config):
            print("Results stored in database")
        else:
            print("Failed to store results in database")
    
    # Generate and display report
    report = generate_report(test_results, args.output)
    print("\n" + report)

if __name__ == "__main__":
    main()
