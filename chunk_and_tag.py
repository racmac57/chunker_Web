#!/usr/bin/env python3
"""
Lightweight Chunking and Tagging Tool

Chunks text/markdown files into logical segments and adds:
- Chunk headers (### Chunk N)
- 1-2 sentence summaries
- Specific, useful tags based on content

Usage:
    python chunk_and_tag.py <input_file> [output_file]
    python chunk_and_tag.py --text "Your text here"
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

# Tag detection patterns organized by category
TAG_PATTERNS = {
    # Technical/Programming
    'python': [r'\bpython\b', r'\.py\b', r'\bdef\s+\w+', r'\bimport\s+', r'\bclass\s+\w+'],
    'json': [r'\bjson\b', r'\{[\s\S]*"[\w]+":', r'\.json\b'],
    'regex': [r'\bregex\b', r'\bregexp?\b', r'r"[^"]*[\\][^"]*"', r're\.\w+\('],
    'loop': [r'\bfor\s+\w+\s+in\b', r'\bwhile\s+', r'\bloop\b', r'\biterat'],
    'config': [r'\bconfig\b', r'\bconfigur', r'\bsettings?\b', r'\bparameters?\b', r'\boptions?\b'],
    'function': [r'\bfunction\b', r'\bdef\s+', r'\bcallable\b', r'\bmethod\b', r'\breturn\b'],
    'input/output': [r'\binput\b', r'\boutput\b', r'\bread\b', r'\bwrite\b', r'\bfile\b', r'\bpath\b'],
    'API': [r'\bAPI\b', r'\bendpoint', r'\bREST\b', r'\bHTTP\b', r'\brequest\b', r'\bresponse\b'],
    'error handling': [r'\btry\b', r'\bexcept\b', r'\berror\b', r'\bexception\b', r'\braise\b'],
    'variable': [r'\bvariable\b', r'\bassign', r'\b=\s*["\'\[\{]'],

    # Procedural/Workflow
    'workflow': [r'\bworkflow\b', r'\bprocess\b', r'\bpipeline\b', r'\bsequence\b'],
    'steps': [r'\bstep\s*\d+', r'\bfirst\b.*\bthen\b', r'\bnext\b', r'\bprocedure\b'],
    'automation': [r'\bautomat', r'\bscript\b', r'\bschedul', r'\bcron\b', r'\btask\b'],
    'logging': [r'\blog\b', r'\blogging\b', r'\blogger\b', r'\bdebug\b', r'\bprint\('],
    'monitoring': [r'\bmonitor', r'\balert', r'\bnotif', r'\bwatch', r'\btrack'],

    # Data-related
    'columns': [r'\bcolumn\b', r'\bfield\b', r'\battribute\b'],
    'schema': [r'\bschema\b', r'\bmodel\b', r'\bstructure\b'],
    'csv': [r'\bcsv\b', r'\bcomma.separated', r'\.csv\b'],
    'table': [r'\btable\b', r'\brows?\b', r'\bdataframe\b', r'\bpandas\b'],
    'ETL': [r'\bETL\b', r'\bextract\b', r'\btransform\b', r'\bload\b'],
    'data cleaning': [r'\bclean', r'\bsanitiz', r'\bnormaliz', r'\bvalidat', r'\bfilter\b'],
    'database': [r'\bdatabase\b', r'\bSQL\b', r'\bquery\b', r'\bSELECT\b', r'\bINSERT\b'],

    # UI/UX
    'GUI': [r'\bGUI\b', r'\binterface\b', r'\bwindow\b', r'\bbutton\b', r'\bwidget\b'],
    'Streamlit': [r'\bstreamlit\b', r'\bst\.\w+', r'\.streamlit\b'],
    'form': [r'\bform\b', r'\bsubmit\b', r'\binput\s+field'],
    'input field': [r'\btext_input\b', r'\bnumber_input\b', r'\bslider\b', r'\bcheckbox\b'],
    'visualization': [r'\bchart\b', r'\bplot\b', r'\bgraph\b', r'\bvisuali'],

    # RAG/Pipeline
    'RAG': [r'\bRAG\b', r'\bretrieval.augmented', r'\bgenerat'],
    'embedding': [r'\bembedding\b', r'\bvector\b', r'\bencode\b'],
    'vector store': [r'\bvector\s*store\b', r'\bchroma\b', r'\bfaiss\b', r'\bpinecone\b'],
    'retrieval': [r'\bretrieval\b', r'\bsearch\b', r'\bquery\b', r'\bfetch\b'],
    'chunking': [r'\bchunk', r'\bsplit', r'\bsegment', r'\btokeniz'],
    'LLM': [r'\bLLM\b', r'\blanguage\s*model\b', r'\bGPT\b', r'\bClaude\b', r'\bOpenAI\b'],

    # Metadata/Structure
    'sidecar': [r'\bsidecar\b', r'\bcompanion\b', r'\bauxiliary\b'],
    'manifest': [r'\bmanifest\b', r'\bindex\b', r'\bcatalog\b'],
    'metadata': [r'\bmetadata\b', r'\bmeta\b', r'\btag\b', r'\blabel\b'],
    'enrichment': [r'\benrich', r'\baugment', r'\benhance\b', r'\bannotat'],

    # File/Format types
    'markdown': [r'\bmarkdown\b', r'\.md\b', r'\b##+\s+'],
    'PDF': [r'\bPDF\b', r'\.pdf\b'],
    'Excel': [r'\bExcel\b', r'\bxlsx?\b', r'\bspreadsheet\b'],
    'YAML': [r'\bYAML\b', r'\.ya?ml\b'],

    # Security/Validation
    'redaction': [r'\bredact', r'\bmask\b', r'\bhide\b', r'\bprivacy\b', r'\bsensitive\b'],
    'validation': [r'\bvalidat', r'\bverif', r'\bcheck\b', r'\bassert\b'],
    'authentication': [r'\bauth', r'\blogin\b', r'\btoken\b', r'\bpassword\b', r'\bcredential'],
}


def chunk_text(text: str, min_sentences: int = 8, max_sentences: int = 12) -> List[str]:
    """
    Chunk text into logical segments by paragraph boundaries and sentence count.

    Args:
        text: Input text to chunk
        min_sentences: Minimum sentences per chunk
        max_sentences: Maximum sentences per chunk

    Returns:
        List of text chunks
    """
    # Split into paragraphs first
    paragraphs = re.split(r'\n\s*\n', text.strip())

    # Simple sentence splitter
    def split_sentences(text: str) -> List[str]:
        # Handle common abbreviations and split on sentence boundaries
        text = re.sub(r'([.!?])\s+', r'\1\n', text)
        sentences = [s.strip() for s in text.split('\n') if s.strip()]
        return sentences

    chunks = []
    current_chunk = []
    current_sentence_count = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        sentences = split_sentences(para)

        # If adding this paragraph would exceed max, save current chunk
        if current_sentence_count + len(sentences) > max_sentences and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_sentence_count = 0

        current_chunk.append(para)
        current_sentence_count += len(sentences)

        # If we've reached the target range, save the chunk
        if current_sentence_count >= min_sentences:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_sentence_count = 0

    # Don't forget the last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def generate_summary(chunk: str) -> str:
    """
    Generate a 1-2 sentence summary of the chunk.

    Uses heuristics to extract key information:
    - First sentence if it's descriptive
    - Key phrases and topics
    """
    sentences = re.split(r'(?<=[.!?])\s+', chunk.strip())

    if not sentences:
        return "This section contains content."

    # Get first sentence, clean it up
    first_sentence = sentences[0].strip()

    # If first sentence is too short, combine with second
    if len(first_sentence) < 50 and len(sentences) > 1:
        first_sentence = f"{first_sentence} {sentences[1].strip()}"

    # Truncate if too long
    if len(first_sentence) > 200:
        first_sentence = first_sentence[:197] + "..."

    # Make it sound like a summary
    summary = first_sentence

    # If it doesn't already describe what "this section" does, frame it
    if not any(word in summary.lower() for word in ['this', 'describes', 'explains', 'shows', 'defines', 'covers']):
        # Extract key topics for context
        topics = extract_key_topics(chunk)
        if topics:
            summary = f"This section covers {', '.join(topics[:3])}. {summary}"

    return summary


def extract_key_topics(text: str) -> List[str]:
    """Extract key topics/nouns from text."""
    # Common technical nouns to look for
    topics = []

    # Look for capitalized terms (potential proper nouns/concepts)
    caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    topics.extend([c for c in caps if len(c) > 3])

    # Look for quoted terms
    quoted = re.findall(r'["`\']([\w\s]+)["`\']', text)
    topics.extend(quoted)

    # Look for terms followed by "is" or "are" (definitions)
    definitions = re.findall(r'(\b\w+\b)\s+(?:is|are)\s+', text)
    topics.extend([d for d in definitions if len(d) > 3])

    # Deduplicate and return
    seen = set()
    unique_topics = []
    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower not in seen and topic_lower not in ['this', 'that', 'these', 'those']:
            seen.add(topic_lower)
            unique_topics.append(topic)

    return unique_topics[:5]


def generate_tags(chunk: str) -> List[str]:
    """
    Generate specific, useful tags based on chunk content.

    Uses pattern matching against predefined tag categories.
    """
    text_lower = chunk.lower()
    tags = []

    for tag, patterns in TAG_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, chunk, re.IGNORECASE):
                tags.append(tag)
                break  # One match per tag is enough

    # Ensure we have at least some tags
    if not tags:
        # Fallback: extract potential tags from content
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'from', 'have', 'been', 'were', 'will', 'would', 'could', 'should']:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top frequent words as fallback tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, _ in sorted_words[:3]]

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)

    return unique_tags[:8]  # Limit to 8 most relevant tags


def format_chunk_output(chunk_num: int, chunk: str, summary: str, tags: List[str]) -> str:
    """
    Format a single chunk with header, summary, tags, and content.
    """
    output = f"### Chunk {chunk_num}\n\n"
    output += f"**Summary:**  \n{summary}\n\n"
    output += f"**Tags:**  \n`{'`, `'.join(tags)}`\n\n"
    output += f"---\n\n{chunk}\n\n"

    return output


def process_file(input_path: str, output_path: str = None,
                 min_sentences: int = 8, max_sentences: int = 12) -> str:
    """
    Process a file and generate chunked, tagged markdown output.

    Args:
        input_path: Path to input file
        output_path: Path to output file (optional)
        min_sentences: Minimum sentences per chunk
        max_sentences: Maximum sentences per chunk

    Returns:
        Formatted markdown string
    """
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    return process_text(text, output_path, min_sentences, max_sentences,
                       source_file=os.path.basename(input_path))


def process_text(text: str, output_path: str = None,
                 min_sentences: int = 8, max_sentences: int = 12,
                 source_file: str = "input") -> str:
    """
    Process text and generate chunked, tagged markdown output.

    Args:
        text: Input text to process
        output_path: Path to output file (optional)
        min_sentences: Minimum sentences per chunk
        max_sentences: Maximum sentences per chunk
        source_file: Name of source for header

    Returns:
        Formatted markdown string
    """
    # Generate chunks
    chunks = chunk_text(text, min_sentences, max_sentences)

    # Build output
    output = f"# Chunked and Tagged: {source_file}\n\n"
    output += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  \n"
    output += f"*Total chunks: {len(chunks)}*\n\n"
    output += "---\n\n"

    for i, chunk in enumerate(chunks, 1):
        summary = generate_summary(chunk)
        tags = generate_tags(chunk)
        output += format_chunk_output(i, chunk, summary, tags)

    # Save to file if output path specified
    if output_path:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"Output saved to: {output_path}")

    return output


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Chunk and tag text/markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chunk_and_tag.py README.md
  python chunk_and_tag.py document.txt output/tagged_document.md
  python chunk_and_tag.py --text "Your text content here..."
  python chunk_and_tag.py input.md --min-sentences 5 --max-sentences 10
        """
    )

    parser.add_argument('input_file', nargs='?', help='Input file to process')
    parser.add_argument('output_file', nargs='?', help='Output file path (default: output/<input>_chunked.md)')
    parser.add_argument('--text', '-t', help='Process text directly instead of file')
    parser.add_argument('--min-sentences', type=int, default=8, help='Minimum sentences per chunk (default: 8)')
    parser.add_argument('--max-sentences', type=int, default=12, help='Maximum sentences per chunk (default: 12)')
    parser.add_argument('--print', '-p', action='store_true', help='Print output to console')

    args = parser.parse_args()

    if args.text:
        # Process direct text input
        output_path = args.output_file or 'output/text_chunked.md'
        result = process_text(
            args.text,
            output_path if not args.print else None,
            args.min_sentences,
            args.max_sentences,
            source_file="direct_input"
        )
        if args.print or not args.output_file:
            print(result)

    elif args.input_file:
        # Process file
        input_path = args.input_file

        if not os.path.exists(input_path):
            print(f"Error: File not found: {input_path}")
            sys.exit(1)

        # Generate default output path if not specified
        if args.output_file:
            output_path = args.output_file
        else:
            base_name = Path(input_path).stem
            output_path = f'output/{base_name}_chunked.md'

        result = process_file(
            input_path,
            output_path if not args.print else None,
            args.min_sentences,
            args.max_sentences
        )

        if args.print:
            print(result)
        else:
            print(f"\nProcessed {len(chunk_text(open(input_path).read()))} chunks")
            print(f"Output: {output_path}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
