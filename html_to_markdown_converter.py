#!/usr/bin/env python3
"""
HTML to Markdown Converter for LLM-friendly documentation

Converts HTML files in the 'sources' directory to clean, readable markdown
files in a new 'markdown' directory, optimized for LLM consumption.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag


class HTMLToMarkdownConverter:
    def __init__(self, sources_dir="sources", output_dir="markdown"):
        self.sources_dir = Path(sources_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive whitespace within line
            line = re.sub(r'\s+', ' ', line.strip())
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        # Join lines with proper spacing
        result = '\n\n'.join(cleaned_lines) if cleaned_lines else ""
        return result
    
    def extract_title(self, soup):
        """Extract page title from HTML."""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Remove common suffixes
            title = re.sub(r'\s*-\s*(RegimaRegima|Regima|RegimaZone).*$', '', title)
            return title
        return "Untitled"
    
    def html_to_markdown_simple(self, element):
        """Convert HTML element to simple markdown."""
        if isinstance(element, NavigableString):
            text = str(element).strip()
            return text if text else ""
        
        if not isinstance(element, Tag):
            return ""
        
        # Handle different HTML tags
        tag_name = element.name.lower()
        
        # Skip certain elements entirely
        if tag_name in ['script', 'style', 'nav', 'header', 'footer', 'aside']:
            return ""
        
        # Process children recursively
        children_content = []
        for child in element.children:
            child_content = self.html_to_markdown_simple(child)
            if child_content:
                children_content.append(child_content)
        
        content = ' '.join(children_content).strip()
        
        if not content:
            return ""
        
        # Convert tags to markdown with proper spacing
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            return f"\n\n{'#' * level} {content}\n\n"
        elif tag_name in ['p']:
            return f"\n\n{content}\n\n"
        elif tag_name in ['div']:
            # Only add spacing for divs that seem to be content blocks
            if len(content) > 50:  # Likely a content block
                return f"\n\n{content}\n\n"
            else:
                return content
        elif tag_name in ['strong', 'b']:
            return f"**{content}**"
        elif tag_name in ['em', 'i']:
            return f"*{content}*"
        elif tag_name == 'a':
            href = element.get('href', '')
            if href and content:
                return f"[{content}]({href})"
            return content
        elif tag_name in ['ul', 'ol']:
            return f"\n\n{content}\n\n"
        elif tag_name == 'li':
            return f"- {content}\n"
        elif tag_name == 'br':
            return "\n"
        elif tag_name in ['span']:
            return content
        else:
            return content
    
    def extract_content(self, soup):
        """Extract main content from HTML soup."""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Try to find main content area
        content_areas = soup.find_all(['article', 'main'])
        
        if content_areas:
            # Use article or main content
            main_content = content_areas[0]
        else:
            # Fallback to body content
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Convert to markdown
        markdown_content = self.html_to_markdown_simple(main_content)
        
        # Clean up the final markdown
        # Remove excessive newlines
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        # Fix bold formatting spacing
        markdown_content = re.sub(r'\*\*\s*\*\*', ' ', markdown_content)  # Remove empty bolds
        markdown_content = re.sub(r'\*\*([^*]+)\*\*\*\*([^*]+)\*\*', r'**\1** **\2**', markdown_content)  # Space between bolds
        # Add spaces around list items
        markdown_content = re.sub(r'-\*\*', r'- **', markdown_content)
        # Clean up spacing around punctuation
        markdown_content = re.sub(r'\*\*\s*([.,:;!?])', r'**\1', markdown_content)
        
        return self.clean_text(markdown_content)
    
    def categorize_file(self, filename):
        """Categorize files into subdirectories."""
        filename_lower = filename.lower()
        
        if filename_lower.startswith('portfolio_'):
            return 'products'
        elif filename_lower.startswith('portfolio-type'):
            return 'categories'  
        elif 'about' in filename_lower:
            return 'about'
        elif 'contact' in filename_lower:
            return 'contact'
        elif 'blog' in filename_lower or 'category' in filename_lower:
            return 'blog'
        elif filename_lower in ['index.htm', 'faqs.htm']:
            return 'main'
        else:
            return 'other'
    
    def convert_file(self, html_file):
        """Convert a single HTML file to markdown."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Extract title and content
            title = self.extract_title(soup)
            content = self.extract_content(soup)
            
            if not content:
                print(f"Warning: No content extracted from {html_file.name}")
                return None
            
            # Create markdown content
            markdown = f"# {title}\n\n{content}"
            
            # Determine output path
            category = self.categorize_file(html_file.name)
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Create output filename
            output_name = html_file.stem + '.md'
            output_path = category_dir / output_name
            
            # Write markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"Converted: {html_file.name} -> {category}/{output_name}")
            return output_path
            
        except Exception as e:
            print(f"Error converting {html_file.name}: {e}")
            return None
    
    def generate_index(self, converted_files):
        """Generate an index README file for the markdown documentation."""
        index_content = """# RegimaZone Documentation

This directory contains LLM-friendly markdown documentation converted from the original HTML files.

## Directory Structure

"""
        
        # Group files by category
        by_category = {}
        for file_path in converted_files:
            if file_path:
                category = file_path.parent.name
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(file_path)
        
        # Add category descriptions
        category_descriptions = {
            'main': 'Main website pages (home, FAQs, etc.)',
            'about': 'About the company and background information',
            'contact': 'Contact information and location details',
            'products': 'Individual product pages and descriptions',
            'categories': 'Product category pages',
            'blog': 'Blog posts and news articles',
            'other': 'Other miscellaneous pages'
        }
        
        for category in sorted(by_category.keys()):
            description = category_descriptions.get(category, f'{category.title()} pages')
            index_content += f"\n### {category.title()}\n{description}\n\n"
            
            for file_path in sorted(by_category[category]):
                relative_path = file_path.relative_to(self.output_dir)
                file_title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
                index_content += f"- [{file_title}]({relative_path})\n"
        
        index_content += f"""
## Summary

- **Total files converted**: {len([f for f in converted_files if f])}
- **Categories**: {len(by_category)}
- **Source**: HTML files from the RegimaZone website
- **Purpose**: LLM-friendly documentation for easy content analysis and processing

## Content Overview

This documentation covers:
- Company information and background
- Skincare product catalog with detailed descriptions
- Product categories and classifications
- Contact information and support
- Blog content and news updates

All content has been cleaned and formatted for optimal readability and LLM processing.
"""
        
        # Write index file
        index_path = self.output_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"Generated index: {index_path}")
    
    def convert_all(self):
        """Convert all HTML files in the sources directory."""
        html_files = list(self.sources_dir.glob("*.htm"))
        
        if not html_files:
            print(f"No HTML files found in {self.sources_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files to convert")
        
        converted_files = []
        for html_file in html_files:
            result = self.convert_file(html_file)
            converted_files.append(result)
        
        # Generate index
        self.generate_index(converted_files)
        
        successful = len([f for f in converted_files if f])
        print(f"\nConversion complete: {successful}/{len(html_files)} files converted successfully")


if __name__ == "__main__":
    converter = HTMLToMarkdownConverter()
    converter.convert_all()