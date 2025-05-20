#!/usr/bin/env python3
import os
import requests
import logging
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nonogram_downloader")

class WebpbnDownloader:
    """Simple API for downloading nonogram puzzles from webpbn.com"""
    
    def __init__(self, output_dir=None):
        """
        Initialize the downloader with an optional output directory.
        
        Args:
            output_dir: Directory to save puzzles to (defaults to current directory)
        """
        self.output_dir = output_dir or os.getcwd()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def download(self, puzzle_id, include_solution=False, format='non'):
        """
        Download a nonogram puzzle from webpbn.com.
        
        Args:
            puzzle_id: The ID of the puzzle to download
            include_solution: Whether to include the intended solution
            format: Format to download ('non' or 'xml')
            
        Returns:
            The path to the downloaded file or None if download failed
        """        
        # Format puzzle_id with leading zeros to match webpbn format
        formatted_id = f"{puzzle_id:08d}"
        
        # Determine format code
        if format == 'xml':
            form = 'xml'
        elif format == 'non':
            form = 'ss'
            
        url = f"https://webpbn.com/export.cgi/webpbn{formatted_id}.{format}"
        
        # Set up the form data for GET request
        params = {
            'go': '1',
            'sid': '',
            'id': str(puzzle_id),
            'fmt': form,
        }
   
        if include_solution:
            params[f"{form}_soln"] = 'on'

        
        logger.info(f"Downloading puzzle {puzzle_id} from webpbn.com in {format.upper()} format...")
        
        try:
            # Use the same headers as the browser request
            headers = {
                'Referer': 'https://webpbn.com/export.cgi'
            }
            
            # Using GET request instead of POST based on working example
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Error downloading puzzle {puzzle_id}: HTTP {response.status_code}")
                return None
            
            # Check if the response content is a valid nonogram
            if not self._is_valid_nonogram(response.text, format):
                logger.error(f"Downloaded content for puzzle {puzzle_id} does not appear to be a valid nonogram")
                return None
            
            filename = f"{puzzle_id}.{format}"
            file_path = os.path.join(self.output_dir, filename)

            with open(file_path, 'w') as f:
                f.write(response.text)
            
            logger.info(f"Puzzle {puzzle_id} downloaded to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading puzzle {puzzle_id}: {str(e)}")
            return None
        
    def _is_valid_nonogram(self, content, format):
        """
        Verify if the downloaded content is a valid nonogram puzzle.
        
        Args:
            content: The downloaded content as text
            format: Format of the content ('non' or 'xml')
            
        Returns:
            True if the content appears to be a valid nonogram, False otherwise
        """
        try:
            # Check for error messages from webpbn
            if "No such puzzle" in content or ("Error" in content and len(content) < 500):
                return False
                
            # Check if content is too short to be valid
            if len(content.strip()) < 20:
                return False
            
            if format == 'xml':
                # For XML, try to parse it and check for required elements
                try:
                    root = ET.fromstring(content)
                    # Check if it has the expected puzzle structure
                    puzzle = root.find('.//puzzle')
                    if puzzle is None:
                        return False
                    
                    # Check for required elements
                    clues = root.findall('.//clues')
                    return len(clues) >= 2  # Should have row and column clues
                except ET.ParseError:
                    return False
            
            elif format == 'non':
                # For NON format, check for essential elements
                lines = content.split('\n')
                # Check for dimensions
                width_found = False
                height_found = False
                rows_section_found = False
                columns_section_found = False
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('width '):
                        width_found = True
                    elif line.startswith('height '):
                        height_found = True
                    elif line == 'rows':
                        rows_section_found = True
                    elif line == 'columns':
                        columns_section_found = True
                
                return width_found and height_found and rows_section_found and columns_section_found
            
            return False
        except Exception as e:
            logger.error(f"Error validating nonogram content: {str(e)}")
            return False

class NonogramsOrgDownloader:
    """Simple API for scraping nonogram puzzles from nonograms.org"""
    
    def __init__(self, output_dir=None):
        """
        Initialize the downloader with an optional output directory.
        
        Args:
            output_dir: Directory to save puzzles to (defaults to current directory)
        """
        self.output_dir = output_dir or os.getcwd()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def download(self, puzzle_id, include_solution=None, format='non'):
        """
        Scrape a nonogram puzzle from nonograms.org.
        
        Args:
            puzzle_id: The ID of the puzzle to download
            include_solution: Whether to include the intended solution
            format: Format to download ('non' or 'xml')
            
        Returns:
            The path to the downloaded file or None if download failed
        """
        logger.info(f"Scraping puzzle {puzzle_id} from nonograms.org in {format.upper()} format...")
        
        try:
            # Scrape the puzzle data
            nonogram_data = self.extract_nonogram_data(puzzle_id)
            if not nonogram_data:
                logger.error(f"Failed to scrape puzzle {puzzle_id}")
                return None
            
            # Verify if the extracted data appears to be a valid nonogram
            if not self._is_valid_nonogram_data(nonogram_data):
                logger.error(f"Extracted data for puzzle {puzzle_id} does not appear to be a valid nonogram")
                return None
            
            # Generate content based on requested format
            if format.lower() == 'xml':
                content = self.generate_xml(nonogram_data)
            else:  # Default to NON format
                content = self.generate_non(nonogram_data)
            
            # Save to file
            filename = f"{puzzle_id}.{format.lower()}"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Puzzle {puzzle_id} downloaded and saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading puzzle {puzzle_id}: {str(e)}")
            return None
    
    def extract_nonogram_data(self, puzzle_id):
        """
        Extract nonogram data from nonograms.org using Playwright.
        """
        url = f"https://www.nonograms.org/nonograms/i/{puzzle_id}"
        logger.info(f"Attempting to scrape: {url}")

        try:
            with sync_playwright() as p:
                logger.info(f"Launching browser to scrape puzzle {puzzle_id}...")
                browser = p.chromium.launch(headless=True)  # Production mode
                page = browser.new_page()
                page.goto(url)
                
                # Check if puzzle exists
                error_selector = "div.error_block"
                try:
                    # Check if error message is present
                    error_element = page.query_selector(error_selector)
                    if error_element:
                        error_text = error_element.inner_text().strip()
                        logger.error(f"Puzzle {puzzle_id} not found: {error_text}")
                        browser.close()
                        return None
                except:
                    # No error element, continue
                    pass
                    
                # Wait for the nonogram table to load
                try:
                    page.wait_for_selector("#nonogram_table", timeout=5000)
                except:
                    logger.error(f"Could not find nonogram table for puzzle {puzzle_id}")
                    browser.close()
                    return None
                
                # Extract column clues
                col_clues_table = page.query_selector("#nonogram_table .nmtt table")
                col_rows = col_clues_table.query_selector_all("tr") if col_clues_table else []
                num_columns = len(col_rows[0].query_selector_all("td")) if col_rows else 0
                
                column_clues = [[] for _ in range(num_columns)]
                for row in col_rows:
                    cells = row.query_selector_all("td")
                    for i, cell in enumerate(cells):
                        text = cell.inner_text().strip()
                        if text:
                            try:
                                column_clues[i].append(int(text))
                            except ValueError:
                                logger.warning(f"Could not convert column clue '{text}' to int. Using as string.")
                                column_clues[i].append(text)
                
                # Extract row clues
                row_clues_table = page.query_selector("#nonogram_table .nmtl table")
                row_rows = row_clues_table.query_selector_all("tr") if row_clues_table else []
                row_clues = []
                for row in row_rows:
                    cells = row.query_selector_all("td")
                    clues = []
                    for cell in cells:
                        text = cell.inner_text().strip()
                        if text:
                            try:
                                clues.append(int(text))
                            except ValueError:
                                logger.warning(f"Could not convert row clue '{text}' to int. Using as string.")
                                clues.append(text)
                    row_clues.append(clues)
                
                # Extract additional puzzle data
                title_element = page.query_selector("#nonogram_title")
                title = title_element.inner_text().strip() if title_element else f"Nonogram {puzzle_id}"
                
                # Get answer image URL
                answer_element = page.query_selector("#nonogram_answer")
                answer_image_url = answer_element.get_attribute("href") if answer_element else ""
                
                # Get puzzle size from info table
                info_table = page.query_selector("xpath=//h1/following-sibling::table[1]")
                info_table_text = info_table.inner_text() if info_table else ""
                size_match = re.search(r"Size:\s*([\d]+x[\d]+)", info_table_text)
                size_str = size_match.group(1) if size_match else None
                
                # Set width and height from size match or from clues dimensions
                if size_str:
                    width, height = map(int, size_str.split("x"))
                else:
                    width = num_columns
                    height = len(row_rows)
                
                browser.close()
                
                return {
                    "title": title,
                    "author": "Unknown",
                    "authorid": "unknown",
                    "copyright": "(c) nonograms.org",
                    "id": str(puzzle_id),
                    "width": width,
                    "height": height,
                    "row_clues": row_clues,
                    "column_clues": column_clues,
                    "file": answer_image_url,
                    "description": f"Nonogram puzzle from nonograms.org, ID: {puzzle_id}",
                    "note": ""
                }

        except Exception as e:
            logger.error(f"An error occurred during scraping puzzle {puzzle_id}: {str(e)}")
            if 'browser' in locals() and 'page' in locals():
                try:
                    page.screenshot(path=os.path.join(self.output_dir, f"error_{puzzle_id}.png"))
                    browser.close()
                except:
                    pass
            return None
    
    def generate_non(self, nonogram_data, include_solution=False):
        """
        Generate NON format content from nonogram data.
        """
        lines = []
        
        # Add header information
        lines.append(f"catalogue \"nonograms.org #{nonogram_data['id']}\"")
        lines.append(f"title \"{nonogram_data['title']}\"")
        lines.append(f"by \"{nonogram_data['author']}\"")
        lines.append(f"copyright \"{nonogram_data['copyright']}\"")
        lines.append(f"width {nonogram_data['width']}")
        lines.append(f"height {nonogram_data['height']}")
        lines.append("")
        
        # Add row clues
        lines.append("rows")
        for row in nonogram_data['row_clues']:
            lines.append(",".join(str(clue) for clue in row))
        lines.append("")
        
        # Add column clues
        lines.append("columns")
        for col in nonogram_data['column_clues']:
            lines.append(",".join(str(clue) for clue in col))
        
        return "\n".join(lines)
    
    def generate_xml(self, nonogram_data, include_solution=False):
        """
        Generate XML format content from nonogram data.
        """
        puzzleset = ET.Element("puzzleset")
        puzzle = ET.SubElement(puzzleset, "puzzle", type="grid", defaultcolor="black")
        
        title = ET.SubElement(puzzle, "title")
        title.text = nonogram_data.get("title", "Nonogram")
        
        author = ET.SubElement(puzzle, "author")
        author.text = nonogram_data.get("author", "Unknown")
        
        authorid = ET.SubElement(puzzle, "authorid")
        authorid.text = nonogram_data.get("authorid", "unknown")
        
        copyright_elem = ET.SubElement(puzzle, "copyright")
        copyright_elem.text = nonogram_data.get("copyright", "(c) nonograms.org")
        
        pid_elem = ET.SubElement(puzzle, "id")
        pid_elem.text = f"#{nonogram_data.get('id', '0')} (v.1)"
        
        description = ET.SubElement(puzzle, "description")
        description.text = nonogram_data.get("description", "")
        
        note = ET.SubElement(puzzle, "note")
        note.text = nonogram_data.get("note", "")
        
        # Set color definitions
        color_white = ET.SubElement(puzzle, "color", name="white", char=".")
        color_white.text = "FFFFFF"
        color_black = ET.SubElement(puzzle, "color", name="black", char="X")
        color_black.text = "000000"

        # Column clues
        clues_columns = ET.SubElement(puzzle, "clues", type="columns")
        for col in nonogram_data.get("column_clues", []):
            line = ET.SubElement(clues_columns, "line")
            for count in col:
                count_elem = ET.SubElement(line, "count")
                count_elem.text = str(count)        # Row clues
        clues_rows = ET.SubElement(puzzle, "clues", type="rows")
        for row in nonogram_data.get("row_clues", []):
            line = ET.SubElement(clues_rows, "line")
            for count in row:
                count_elem = ET.SubElement(line, "count")
                count_elem.text = str(count)

        # Convert to string and format nicely
        rough_string = ET.tostring(puzzleset, encoding="unicode")
        dom = xml.dom.minidom.parseString(rough_string)
        pretty_xml_as_string = dom.toprettyxml(indent="  ")
        
        # Remove automatically added XML declaration (we'll add our own)
        pretty_xml_as_string = pretty_xml_as_string.replace('<?xml version="1.0" ?>\n', '')
        
        # Add XML declaration and DOCTYPE
        xml_header = '<?xml version="1.0"?>\n<!DOCTYPE pbn SYSTEM "https://webpbn.com/pbn-0.3.dtd">\n'
        
        return xml_header + pretty_xml_as_string
    
    def _is_valid_nonogram_data(self, nonogram_data):
        """
        Verify if the extracted data is a valid nonogram puzzle.
        
        Args:
            nonogram_data: Dictionary containing nonogram data
            
        Returns:
            True if the data appears to be a valid nonogram, False otherwise
        """
        try:
            # Check for required keys
            required_keys = ['width', 'height', 'row_clues', 'column_clues']
            if not all(key in nonogram_data for key in required_keys):
                return False
            
            # Check if dimensions are valid
            if nonogram_data['width'] <= 0 or nonogram_data['height'] <= 0:
                return False
            
            # Check if clues match the specified dimensions
            if len(nonogram_data['row_clues']) != nonogram_data['height']:
                return False
            if len(nonogram_data['column_clues']) != nonogram_data['width']:
                return False
            
            # Check if we have actual clue data (not empty lists)
            if not any(any(clue) for clue in nonogram_data['row_clues']):
                return False
            if not any(any(clue) for clue in nonogram_data['column_clues']):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating nonogram data: {str(e)}")
            return False
