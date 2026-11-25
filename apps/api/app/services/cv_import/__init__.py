"""Import a CV or LinkedIn PDF: validate it, extract it with Claude, then propose a draft.

Modules, in the order a PDF goes through them:
- pdf: check the file before paying for an extraction
- extraction / claude_extractor / prompt: turn the PDF into a CvExtraction
- normalize: turn a CvExtraction into valid profile and experience data
- merge: combine that data with what the user already has
- imports: the workflow and the database rows (start, read, apply, discard)
"""
