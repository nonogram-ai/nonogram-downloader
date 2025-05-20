#!/usr/bin/env python3
import os
import sys
from downloader import WebpbnDownloader, NonogramsOrgDownloader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_downloader")

def test_webpbn_downloader():
    """Test WebpbnDownloader with valid and invalid puzzle IDs"""
    downloader = WebpbnDownloader("./test_output")
    
    # Test with valid puzzle ID
    logger.info("Testing with valid puzzle ID...")
    valid_file = downloader.download(662, format='non')
    if valid_file:
        logger.info(f"Successfully downloaded valid puzzle to {valid_file}")
    else:
        logger.error("Failed to download valid puzzle")
    
    # Test with invalid puzzle ID
    logger.info("Testing with invalid puzzle ID...")
    invalid_file = downloader.download(99999999, format='non')
    if invalid_file is None:
        logger.info("Correctly reported invalid puzzle ID")
    else:
        logger.error(f"Should have failed for invalid ID but returned {invalid_file}")

def test_nonograms_org_downloader():
    """Test NonogramsOrgDownloader with valid and invalid puzzle IDs"""
    downloader = NonogramsOrgDownloader("./test_output")
    
    # Test with valid puzzle ID
    logger.info("Testing with valid puzzle ID...")
    valid_file = downloader.download(5001, format='non')
    if valid_file:
        logger.info(f"Successfully downloaded valid puzzle to {valid_file}")
    else:
        logger.error("Failed to download valid puzzle")
    
    # Test with invalid puzzle ID
    logger.info("Testing with invalid puzzle ID...")
    invalid_file = downloader.download(99999999, format='non')
    if invalid_file is None:
        logger.info("Correctly reported invalid puzzle ID")
    else:
        logger.error(f"Should have failed for invalid ID but returned {invalid_file}")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("./test_output", exist_ok=True)

    test_nonograms_org_downloader()

    test_webpbn_downloader()
